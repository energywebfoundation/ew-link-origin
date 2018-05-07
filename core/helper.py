import os
import json
import time
import sched
import syslog
import logging
import colorlog
import datetime

import core.data_access as dao
import core.config_parser as config_parser

from core.abstract.bond import InputConfiguration, Configuration
from core.input.sp_group import SPGroupAPI

from resin import Resin

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

# Default color scheme is 'example'
logger = colorlog.getLogger('example')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class AsyncClientError(EnvironmentError):
    pass


class NoCompilerError(NotImplementedError):
    pass


class AllGasUsedWarning(Warning):
    pass


def convert_time(epoch: int):
    access_time = datetime.datetime.fromtimestamp(epoch)
    return access_time.strftime("%Y-%m-%d  %H:%M:%S")


def read_config(token: str, resin_device_uuid: str):
    """
    Device variable must be added in the services variable field on resin.io dashboard.
    Yeah, I know.
    :param token: Resin io token
    :param resin_device_uuid: Device UUID from resin.io dashboard.
    :return: Dict from json parsed string.
    """
    resin = Resin()
    resin.auth.login_with_token(token)
    app_vars = resin.models.environment_variables.device.get_all(resin_device_uuid)
    config_json_string = next(var for var in app_vars if var['env_var_name'] == 'config')
    return json.loads(config_json_string['value'])


def print_config(config_file: str = None):
    if config_file:
        configuration = config_parser.parse(json.load(open(config_file)))
    else:
        configuration = config_parser.parse(json.loads(os.environ['config']))

    prod = '[PROD][CONF] meter: {} - co2: {}'
    coms = '[COMS][CONF] meter: {}'
    if configuration.production is not None:
        [logger.debug(prod.format(item.energy.__class__.__name__, item.carbon_emission.__class__.__name__))
         for item in configuration.production]
    if configuration.consumption is not None:
        [logger.debug(coms.format(item.energy.__class__.__name__)) for item in configuration.consumption]
    return configuration


def _produce(chain_file, config, item) -> bool:
    try:
        production_local_chain = dao.DiskStorage(chain_file)
        last_local_chain_hash = production_local_chain.get_last_hash()
        last_remote_state = config.client.last_state(item.origin)
        produced_data = dao.read_production_data(item, last_local_chain_hash, last_remote_state)
        created_file = production_local_chain.add_to_chain(produced_data)
        tx_receipt = config.client.mint(produced_data.produced, item.origin)
        class_name = item.energy.__class__.__name__
        data = produced_data.produced
        bn = str(tx_receipt['blockNumber'])
        msg = '[PROD] {} - offline: {} - {} Watts - {}kg Co2 Saved - Block: {} - File: {}'
        logger.info(msg.format(class_name, data.is_meter_down, data.energy, data.co2_saved, bn, created_file))
        return True
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, "[BOND][PROD] meter: {} - stack: {}".format(item.energy.__class__.__name__, e))
        return False


def print_production_results(config: Configuration, item: InputConfiguration, chain_file: str):
    for trial in range(3):
        if _produce(chain_file, config, item):
            return
        time.sleep(300 * trial)
        if trial == 2:
            logger.critical("[COMS][FAIL] meter: {} - Check syslog [BOND][PROD].".format(item.energy.__class__.__name__))


def _consume(chain_file, config, item):
    try:
        consumption_local_chain = dao.DiskStorage(chain_file)
        last_local_chain_hash = consumption_local_chain.get_last_hash()
        last_remote_state = config.client.last_state(item.origin)
        consumed_data = dao.read_consumption_data(item, last_local_chain_hash, last_remote_state)
        created_file = consumption_local_chain.add_to_chain(consumed_data)
        tx_receipt = config.client.mint(consumed_data.consumed, item.origin)
        class_name = item.energy.__class__.__name__
        data = consumed_data.consumed
        block_number = str(tx_receipt['blockNumber'])
        message = '[COMS] {} - offline: {} - {} Watts - Block: {} - File: {}'
        logger.info(message.format(class_name, data.is_meter_down, data.energy, block_number, created_file))
        return True
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, "[BOND][COMS] meter: {} - stack: {}".format(item.energy.__class__.__name__, e))
        return False


def print_consumption_results(config: Configuration, item: InputConfiguration, chain_file: str):
    for trial in range(3):
        if _consume(chain_file, config, item):
            return
        time.sleep(300 * trial)
        if trial == 2:
            logger.critical("[COMS][FAIL] meter: {} - Check syslog [BOND][COMS].".format(item.energy.__class__.__name__))


def log(prod_chain_file: str, cons_chain_file: str, configuration: Configuration):
    if configuration.production:
        production = [item for item in configuration.production if not issubclass(item.energy.__class__, SPGroupAPI)]
        [print_production_results(configuration, item, prod_chain_file) for item in production]
    if configuration.consumption:
        [print_consumption_results(configuration, item, cons_chain_file) for item in configuration.consumption]


def log_sp(prod_chain_file: str, cons_chain_file: str, configuration: Configuration):
    if configuration.production:
        production = [item for item in configuration.production if issubclass(item.energy.__class__, SPGroupAPI)]
        [print_production_results(configuration, item, prod_chain_file) for item in production]


def schedule(kwargs):
    scheduler = sched.scheduler(time.time, time.sleep)
    today = datetime.datetime.now() + datetime.timedelta(hours=1)
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    daily_wake = tomorrow.replace(hour=0, minute=31)
    if datetime.datetime.now() > daily_wake:
        daily_wake = daily_wake + datetime.timedelta(days=1)
    remaining_hours = set(range(24)) - set(range(today.hour))
    for hour in list(remaining_hours):
        hourly_wake = today.replace(hour=hour, minute=1)
        scheduler.enterabs(time=time.mktime(hourly_wake.timetuple()), priority=2, action=log_sp, kwargs=kwargs)
    hourly_wake = tomorrow.replace(hour=0, minute=1)
    scheduler.enterabs(time=time.mktime(hourly_wake.timetuple()), priority=2, action=log_sp, kwargs=kwargs)
    scheduler.enterabs(time=time.mktime(daily_wake.timetuple()), priority=1, action=log, kwargs=kwargs)
    scheduler.run()
