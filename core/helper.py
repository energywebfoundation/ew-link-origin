import os
import json
import time
import sched
import logging
import colorlog
import datetime

from resin import Resin

import core.data_access as dao
import core.config_parser as config_parser
from core.abstract.bond import InputConfiguration, Configuration

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

# Default color scheme is 'example'
tty_logger = colorlog.getLogger('example')
tty_logger.addHandler(handler)
tty_logger.setLevel(logging.ERROR)


file_logger = logging.getLogger('spam_application')
file_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('./bond.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
file_logger.addHandler(fh)


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

    print('\n\n`•.,,.•´¯¯`•.,,.•´¯¯`•.,, Config ,,.•´¯¯`•.,,.•´¯¯`•.,,.•´\n')
    if configuration.production is not None:
        for item in configuration.production:
            print('Energy Production Module: ' + item.energy.__class__.__name__)
            print('Carbon Emission Saved: ' + item.carbon_emission.__class__.__name__)
    if configuration.consumption is not None:
        [print('Energy Consumption Module: ' + item.energy.__class__.__name__) for item in configuration.consumption]
    print('EWF Client: ' + configuration.client.__class__.__name__)
    print('\n\n')
    return configuration


def print_production_results(config: Configuration, item: InputConfiguration, chain_file: str):
    print("==================== PRODUCTION INPUT READ ===========================")
    print('Energy Production Module: ' + item.energy.__class__.__name__)
    print('Carbon Emission Saved: ' + item.carbon_emission.__class__.__name__)
    print('----------')
    try:
        production_local_chain = dao.DiskStorage(chain_file)
        last_local_chain_hash = production_local_chain.get_last_hash()
    except Exception as e:
        print('ERROR: Writing or reading files')
        return
    try:
        print('Last Blockchain state:')
        last_remote_state = config.client.last_state(item.origin)
        print(last_remote_state)
        print('----------')
    except Exception as e:
        print('ERROR: Reading hash from blockchain')
        return
    try:
        produced_data = dao.read_production_data(item, last_local_chain_hash, last_remote_state)
    except Exception as e:
        print('ERROR: Reading from remote api.')
        return
    try:
        file_name_created = production_local_chain.add_to_chain(produced_data)
    except Exception as e:
        print('ERROR: Writing to local chain of files.')
        return
    try:
        print('Sending to Blockchain:')
        print(produced_data.produced.to_dict())
        print('----------')

    except Exception as e:
        print('ERROR: Converting results to print.')
        return
    try:
        tx_receipt = config.client.mint(produced_data.produced, item.origin)
        print('Receipt Block Number: ' + str(tx_receipt['blockNumber']))
        print('-------------------')
        print('New Blockchain state:')
        last_remote_state = config.client.last_state(item.origin)
        print(last_remote_state)
        print('----------')
    except Exception as e:
        print('ERROR: Reading or writing to the blockchain.')
        return
    try:
        print('New Local File:')
        print(file_name_created)
        print('----------\n')
    except Exception as e:
        print('ERROR: Reading from local chain of files.')
        return


def print_consumption_results(config: Configuration, item: InputConfiguration, chain_file: str):
    print("==================== CONSUMPTION INPUT READ ===========================")
    print('Energy Production Module: ' + item.energy.__class__.__name__)
    print('Carbon Emission Saved: ' + item.carbon_emission.__class__.__name__)
    print('----------')
    try:
        consumption_local_chain = dao.DiskStorage(chain_file)
        last_local_chain_hash = consumption_local_chain.get_last_hash()
    except Exception as e:
        print('ERROR: Writing or reading files')
        return
    try:
        print('Last Blockchain state:')
        last_remote_state = config.client.last_state(item.origin)
        print(last_remote_state)
        print('----------')
    except Exception as e:
        print('ERROR: Reading hash from blockchain')
        return
    # Get the remote data.
    try:
        consumed_data = dao.read_consumption_data(item, last_local_chain_hash, last_remote_state)
    except Exception as e:
        print('ERROR: Reading from remote api.')
        return
    try:
        file_name_created = consumption_local_chain.add_to_chain(consumed_data)
    except Exception as e:
        print('ERROR: Writing to local chain of files.')
        return
    try:
        print('Sending to Blockchain:')
        print(consumed_data.consumed.to_dict())
        print('----------')

    except Exception as e:
        print('ERROR: Converting results to print.')
        return
    try:
        tx_receipt = config.client.mint(consumed_data.consumed, item.origin)
        print('Receipt Block Number: ' + str(tx_receipt['blockNumber']))
        print('-------------------')
    except Exception as e:
        print('ERROR: Reading or writing to the blockchain.')
        return
    try:
        print('Last Blockchain state:')
        last_remote_state = config.client.last_state(item.origin)
        print(last_remote_state)
        print('----------')
        print('New Local File:')
        print(file_name_created)
        print('----------\n')
    except Exception as e:
        print('ERROR: Reading from local chain of files.')
        return


def log(prod_chain_file: str, cons_chain_file: str, configuration: Configuration):
    print('\n\n¸.•*´¨`*•.¸¸.•*´¨`*•.¸ Results ¸.•*´¨`*•.¸¸.•*´¨`*•.¸\n')
    if configuration.production:
        [print_production_results(configuration, item, prod_chain_file) for item in configuration.production]
    if configuration.consumption:
        [print_consumption_results(configuration, item, cons_chain_file) for item in configuration.consumption]


def schedule():
    scheduler = sched.scheduler(time.time, time.sleep)
    time_sched = '19:13'
    now = datetime.datetime.now()
    hour, min = tuple(time_sched.split(':'))
    future = now.replace(hour=int(hour), minute=int(min))
    if now > future:
        future = future + datetime.timedelta(days=1)
    print('\n\n===================== WAITING ==================')
    print('Next Event: ' + future.strftime('%d-%b-%Y %H:%M'))
    scheduler.enterabs(time=time.mktime(future.timetuple()), priority=1, action=log, argument=())
    scheduler.run()
