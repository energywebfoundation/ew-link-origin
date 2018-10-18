import os
import time
import sched
import logging
import colorlog
import datetime

import pytz

import core.data_access as dao
import core.config_parser as config_parser

from core.abstract.bond import InputConfiguration, Configuration
from core.input.sp_group import SPGroupAPI

PERSISTENCE = '/app/logs/'

tty_handler = colorlog.StreamHandler()
tty_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))
if not os.path.exists(PERSISTENCE):
    os.makedirs(PERSISTENCE)
file_handler = logging.FileHandler(PERSISTENCE + 'bond.log')
formatter = logging.Formatter('%(asctime)s [%(levelname)s]%(message)s')
file_handler.setFormatter(formatter)

# Default color scheme is 'example'
logger = colorlog.getLogger('example')
logger.addHandler(tty_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

error_log = logging.getLogger()
error_file_handler = logging.FileHandler(PERSISTENCE + 'error.log')
error_file_handler.setFormatter(formatter)
error_log.addHandler(error_file_handler)
error_log.setLevel(logging.ERROR)


class AsyncClientError(EnvironmentError):
    pass


class NoCompilerError(NotImplementedError):
    pass


class AllGasUsedWarning(Warning):
    pass


def convert_time(epoch: int):
    access_time = datetime.datetime.fromtimestamp(epoch)
    return access_time.strftime("%Y-%m-%d  %H:%M:%S")


def print_config(configuration_file):
    prod = '[PROD][CONF] meter: {} - energy module: {} - co2 module: {}'
    coms = '[COMS][CONF] meter: {} - energy module: {}'
    logger.debug('[CONF] path to logs: {}'.format(PERSISTENCE))
    configuration = config_parser.parse(configuration_file)
    if configuration.production is not None:
        [logger.debug(prod.format(item.name, item.energy.__class__.__name__, item.carbon_emission.__class__.__name__))
         for item in configuration.production]
    if configuration.consumption is not None:
        [logger.debug(coms.format(item.name, item.energy.__class__.__name__))
         for item in configuration.consumption]
    return {"configuration": configuration}


def _produce(chain_file, config, item) -> bool:
    try:
        production_local_chain = dao.DiskStorage(chain_file, PERSISTENCE)
        last_local_chain_hash = production_local_chain.get_last_hash()
        last_remote_state = config.client.last_state(item.origin)
        produced_data = dao.read_production_data(
            item, last_local_chain_hash, last_remote_state)
        created_file = production_local_chain.add_to_chain(produced_data)
        tx_receipt = config.client.mint(produced_data.produced, item.origin)
        friendly_name = item.name
        data = produced_data.produced

        logger.info(F"produced data: {produced_data}")

        block_number = str(tx_receipt['blockNumber'])
        msg = '[PROD] meter: {} - {} watts - {} kg of Co2 - block: {}'
        if data.is_meter_down:
            logger.warning(msg.format(friendly_name, data.energy,
                                      data.co2_saved, block_number))
        else:
            logger.info(msg.format(friendly_name, data.energy,
                                   data.co2_saved, block_number))
        return True
    except Exception as e:
        error_log.exception(
            "[BOND][PROD] module: {} - stack: {}".format(item.energy.__class__.__name__, e))
        return False


def print_production_results(config: Configuration, item: InputConfiguration, chain_file: str):
    for trial in range(3):
        if _produce(chain_file, config, item):
            return
        time.sleep(300 * trial)
        if trial == 2:
            logger.critical(
                "[COMS][FAIL] module: {} - Check error.log".format(item.energy.__class__.__name__))


def _consume(chain_file, config, item):
    try:
        consumption_local_chain = dao.DiskStorage(chain_file, PERSISTENCE)
        last_local_chain_hash = consumption_local_chain.get_last_hash()
        last_remote_state = config.client.last_state(item.origin)
        consumed_data = dao.read_consumption_data(
            item, last_local_chain_hash, last_remote_state)
        created_file = consumption_local_chain.add_to_chain(consumed_data)
        tx_receipt = config.client.mint(consumed_data.consumed, item.origin)
        friendly_name = item.name
        data = consumed_data.consumed
        block_number = str(tx_receipt['blockNumber'])
        message = '[COMS] meter: {} - {} watts - block: {}'
        if data.is_meter_down:
            logger.warning(message.format(
                friendly_name, data.energy, block_number))
        else:
            logger.info(message.format(
                friendly_name, data.energy, block_number))
        return True
    except Exception as e:
        error_log.exception(
            "[BOND][COMS] module: {} - stack: {}".format(item.energy.__class__.__name__, e))
        return False


def print_consumption_results(config: Configuration, item: InputConfiguration, chain_file: str):
    for trial in range(3):
        if _consume(chain_file, config, item):
            return
        time.sleep(300 * trial)
        if trial == 2:
            logger.critical(
                "[COMS][FAIL] module: {} - Check error.log".format(item.energy.__class__.__name__))


def log_production(configuration: Configuration):
    fn = '{}.pkl'
    production = [item for item in configuration.production if not issubclass(
        item.energy.__class__, SPGroupAPI)]
    [print_production_results(configuration, item, fn.format(
        item.name)) for item in production]


def log_consumption(configuration: Configuration):
    fn = '{}.pkl'
    try:
        [print_consumption_results(configuration, item, fn.format(
            item.name)) for item in configuration.consumption]
    except Exception as err:
        logger.error(err)


def log_sp(configuration: Configuration):
    fn = '{}.pkl'
    if configuration.production:
        production = [item for item in configuration.production if issubclass(
            item.energy.__class__, SPGroupAPI)]
        [print_production_results(configuration, item, fn.format(
            item.name)) for item in production]


def schedule(kwargs):
    scheduler = sched.scheduler(time.time, time.sleep)
    today = datetime.datetime.now(pytz.utc)
    next_hour = today + datetime.timedelta(hours=1, seconds=0, minutes=0)
    scheduler.enterabs(time=time.mktime(next_hour.timetuple()),
                       priority=2, action=log_consumption, kwargs=kwargs)
    scheduler.enterabs(time=time.mktime(next_hour.timetuple()),
                       priority=1, action=log_production, kwargs=kwargs)
    logger.debug("[BOND] next data collection: {}".format(
        next_hour.isoformat()))
    scheduler.run()
