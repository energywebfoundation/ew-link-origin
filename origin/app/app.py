import os
import json
import time
import sched
import logging
import colorlog
import datetime

import origin.dao as dao
import origin.config as config_parser

from core.input import ExternalDataSource, ExternalData
from apps.origin.dao import ProductionFileData, ProducedChainData, ConsumptionFileData, ConsumedChainData
from apps.origin.config import InputConfiguration
from apps.origin.input.eumel import DataLoggerV1, DataLoggerV2d1d1
from apps.origin.input.sp_group import SPGroupAPI

from resin import Resin

PERSISTENCE = '/mnt/data/tobalaba/'

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
error_log.setLevel(logging.DEBUG)


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
    prod = '[PROD][CONF] meter: {} - co2 source: {}'
    coms = '[COMS][CONF] meter: {}'
    logger.debug('[CONF] path to logs: {}'.format(PERSISTENCE))

    if config_file:
        configuration = config_parser.parse(json.load(open(config_file)))
    else:
        configuration = config_parser.parse(json.loads(os.environ['config']))
    if configuration.production is not None:
        [logger.debug(prod.format(item.energy.__class__.__name__, item.carbon_emission.__class__.__name__))
         for item in configuration.production]
    if configuration.consumption is not None:
        [logger.debug(coms.format(item.energy.__class__.__name__)) for item in configuration.consumption]

    return configuration


def _produce(chain_file, config, item) -> bool:
    try:
        production_local_chain = dao.DiskStorage(chain_file, PERSISTENCE)
        last_local_chain_hash = production_local_chain.get_last_hash()
        last_remote_state = config.client.last_state(item.origin)
        produced_data = read_production_data(item, last_local_chain_hash, last_remote_state)
        created_file = production_local_chain.add_to_chain(produced_data)
        tx_receipt = config.client.mint(produced_data.produced, item.origin)
        class_name = item.energy.__class__.__name__
        data = produced_data.produced
        block_number = str(tx_receipt['blockNumber'])
        msg = '[PROD] meter: {} - {} watts - {} kg of Co2 - block: {}'
        if data.is_meter_down:
            logger.warning(msg.format(class_name, data.energy, data.co2_saved, block_number))
        else:
            logger.info(msg.format(class_name, data.energy, data.co2_saved, block_number))
        return True
    except Exception as e:
        error_log.exception("[BOND][PROD] meter: {} - stack: {}".format(item.energy.__class__.__name__, e))
        return False


def print_production_results(config: config_parser.Configuration, item: config_parser.InputConfiguration, chain_file: str):
    for trial in range(3):
        if _produce(chain_file, config, item):
            return
        time.sleep(300 * trial)
        if trial == 2:
            logger.critical("[COMS][FAIL] meter: {} - Check error.log".format(item.energy.__class__.__name__))


def _consume(chain_file, config, item):
    try:
        consumption_local_chain = dao.DiskStorage(chain_file, PERSISTENCE)
        last_local_chain_hash = consumption_local_chain.get_last_hash()
        last_remote_state = config.client.last_state(item.origin)
        consumed_data = read_consumption_data(item, last_local_chain_hash, last_remote_state)
        created_file = consumption_local_chain.add_to_chain(consumed_data)
        tx_receipt = config.client.mint(consumed_data.consumed, item.origin)
        class_name = item.energy.__class__.__name__
        data = consumed_data.consumed
        block_number = str(tx_receipt['blockNumber'])
        message = '[COMS] meter: {} - {} watts - block: {}'
        if data.is_meter_down:
            logger.warning(message.format(class_name, data.energy, block_number))
        else:
            logger.info(message.format(class_name, data.energy, block_number))
        return True
    except Exception as e:
        error_log.exception("[BOND][COMS] meter: {} - stack: {}".format(item.energy.__class__.__name__, e))
        return False


def print_consumption_results(config: config_parser.Configuration, item: config_parser.InputConfiguration, chain_file: str):
    for trial in range(3):
        if _consume(chain_file, config, item):
            return
        time.sleep(300 * trial)
        if trial == 2:
            logger.critical("[COMS][FAIL] meter: {} - Check error.log".format(item.energy.__class__.__name__))


def log(configuration: config_parser.Configuration):
    fn = '{}.pkl'
    if configuration.production:
        production = [item for item in configuration.production if not issubclass(item.energy.__class__, SPGroupAPI)]
        [print_production_results(configuration, item, fn.format(item.name)) for item in production]
    if configuration.consumption:
        [print_consumption_results(configuration, item, fn.format(item.name)) for item in configuration.consumption]


def log_sp(configuration: config_parser.Configuration):
    fn = '{}.pkl'
    if configuration.production:
        production = [item for item in configuration.production if issubclass(item.energy.__class__, SPGroupAPI)]
        [print_production_results(configuration, item, fn.format(item.name)) for item in production]


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


def __fetch_input_data(external_data_source: ExternalDataSource):
    try:
        result = external_data_source.read_state()
        if not issubclass(result.__class__, ExternalData):
            raise AssertionError
        return result
    except Exception as e:
        return None


def read_production_data(config: InputConfiguration, last_hash: str, last_state: list) -> ProductionFileData:
    """
    Reach for external data sources and return parsed consumed data
    :param last_hash: Last file hash
    :param config: Configuration
    :return: ProductionInputData
    """
    input_data_dict = {
        'raw_energy': __fetch_input_data(config.energy),
        'raw_carbon_emitted': __fetch_input_data(config.carbon_emission),
        'produced': None,
    }
    input_data = ProductionFileData(**input_data_dict)
    co2_saved = input_data.raw_carbon_emitted.accumulated_co2 if input_data.raw_carbon_emitted else 0
    energy = input_data.raw_energy.accumulated_power if input_data.raw_energy else 0
    # add last measured energy in case it is not accumulated
    # TODO: refactor this to the data input classes
    if not (isinstance(config.energy, DataLoggerV1) or isinstance(config.energy, DataLoggerV2d1d1)):
        last_energy = last_state[3]
        energy += last_energy
    # x * y kg/Watts = xy kg/Watts
    calculated_co2 = energy * co2_saved
    co2_saved = int(calculated_co2 * pow(10, 3))
    energy = int(energy)
    produced = {
        'energy': energy,
        'is_meter_down': True if input_data.raw_energy is None else False,
        'previous_hash': last_hash,
        'co2_saved': co2_saved,
        'is_co2_down': True if input_data.raw_carbon_emitted is None else False
    }
    input_data.produced = ProducedChainData(**produced)
    return input_data


def read_consumption_data(config: InputConfiguration, last_hash: str, last_state: list) -> ConsumptionFileData:
    """
    Reach for external data sources and return parsed consumed data
    :param last_hash: Last file hash
    :param config: InputConfiguration
    :return: ConsumptionInputData
    """
    input_data_dict = {
        'raw_energy': __fetch_input_data(config.energy),
        'consumed': None,
    }
    input_data = ConsumptionFileData(**input_data_dict)
    # add last measured energy in case it is not accumulated
    # TODO: refactor this to the data input classes
    energy = int(input_data.raw_energy.accumulated_power) if input_data.raw_energy else 0
    if not (isinstance(config.energy, DataLoggerV1) or isinstance(config.energy, DataLoggerV2d1d1)):
        last_energy = last_state[5]
        energy += last_energy
    consumed = {
        'energy': energy,
        'is_meter_down': True if input_data.raw_energy is None else False,
        'previous_hash':  last_hash
    }
    input_data.consumed = ConsumedChainData(**consumed)
    return input_data