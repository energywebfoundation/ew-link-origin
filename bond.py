import json

import subprocess

import os

import time
import core.config_parser as config
import core.data_access as dao
from core.abstract.bond import InputConfiguration, Configuration

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'


def read_config():
    return json.loads(os.environ['config'])


def print_config():
    if configuration.production is not None:
        for item in configuration.production:
            print('Energy Production Module: ' + item.energy.__class__.__name__)
            print('Carbon Emission Saved: ' + item.carbon_emission.__class__.__name__)
    if configuration.consumption is not None:
        [print('Energy Consumption Module: ' + item.energy.__class__.__name__) for item in configuration.consumption]
    print('EWF Client: ' + configuration.client.__class__.__name__)


def start_ewf_client():
    subprocess.Popen(["assets/ewf-client-arm", "--jsonrpc-apis", "all", "--reserved-peers", "assets/tobalaba-peers"],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('waiting for ewf-client...\n\n')
    time.sleep(60)


def print_production_results(config: Configuration, item: InputConfiguration):
    print("==================== PRODUCTION INPUT READ ===========================")
    try:
        production_local_chain = dao.DiskStorage(PRODUCTION_CHAIN)
        last_local_chain_hash = production_local_chain.get_last_hash()
    except Exception as e:
        print('ERROR: Writing or reading files')
        return
    try:
        last_remote_chain_hash = config.client.last_hash(item.origin)
        print('Local and Remote chain sync:')
        print(last_local_chain_hash == last_remote_chain_hash)
        print('----------')
    except Exception as e:
        print('ERROR: Reading hash from blockchain')
        return
    try:
        produced_data = dao.read_production_data(item, last_local_chain_hash)
    except Exception as e:
        print('ERROR: Reading from remote api.')
        return
    try:
        file_name_created = production_local_chain.add_to_chain(produced_data)
    except Exception as e:
        print('ERROR: Writing to local chain of files.')
        return
    try:
        print('Produced Energy:')
        if produced_data.raw_energy:
            print(produced_data.raw_energy.measurement_epoch)
            print(produced_data.raw_energy.accumulated_power)
        print('----------')
        print('Carbon Emission Today:')
        if produced_data.raw_carbon_emitted:
            print(produced_data.raw_carbon_emitted.measurement_epoch)
            print(produced_data.raw_carbon_emitted.accumulated_co2)
        print('----------')
        print('Sending to Blockchain:')
        print(produced_data.produced.to_dict())
        print('----------')

    except Exception as e:
        print('ERROR: Converting results to print.')
        return
    try:
        print('Lash Remote Hash:')
        print(config.client.last_hash(item.origin))
        print('----------')
        tx_receipt = config.client.mint(produced_data.produced, item.origin)
        print('Receipt Block Number: ' + str(tx_receipt['blockNumber']))
        print('-------------------')
        print('New Remote Hash:')
        print(config.client.last_hash(item.origin))
        print('----------')
    except Exception as e:
        print('ERROR: Reading or writing to the blockchain.')
        return
    try:
        print('New Local Hash:')
        print(production_local_chain.get_last_hash())
        print('----------')
        print('New Local File:')
        print(file_name_created)
        print('----------\n')
    except Exception as e:
        print('ERROR: Reading from local chain of files.')
        return


def print_consumption_results(config: Configuration, item: InputConfiguration):
    print("==================== CONSUMPTION INPUT READ ===========================")
    try:
        consumption_local_chain = dao.DiskStorage(CONSUMPTION_CHAIN)
        last_local_chain_hash = consumption_local_chain.get_last_hash()
    except Exception as e:
        print('ERROR: Writing or reading files')
        return
    try:
        last_remote_chain_hash = config.client.last_hash(item.origin)
        print('Local and Remote chain sync:')
        print(last_local_chain_hash == last_remote_chain_hash)
        print('----------')
    except Exception as e:
        print('ERROR: Reading hash from blockchain')
        return
    # Get the remote data.
    try:
        consumed_data = dao.read_consumption_data(item, last_local_chain_hash)
    except Exception as e:
        print('ERROR: Reading from remote api.')
        return
    try:
        file_name_created = consumption_local_chain.add_to_chain(consumed_data)
    except Exception as e:
        print('ERROR: Writing to local chain of files.')
        return
    try:
        print('Produced Energy:')
        print(consumed_data.raw_energy.measurement_epoch)
        print(consumed_data.raw_energy.accumulated_power)
        print('----------')
        print('Sending to Blockchain:')
        print(consumed_data.consumed.to_dict())
        print('----------')

    except Exception as e:
        print('ERROR: Converting results to print.')
        return
    try:
        print('Lash Remote Hash:')
        print(config.client.last_hash(item.origin))
        print('----------')
        tx_receipt = config.client.mint(consumed_data.consumed, item.origin)
        print('Receipt Block Number: ' + str(tx_receipt['blockNumber']))
        print('-------------------')
        print('New Remote Hash:')
        print(config.client.last_hash(item.origin))
        print('----------')
    except Exception as e:
        print('ERROR: Reading or writing to the blockchain.')
        return
    try:
        print('New Local Hash:')
        print(consumption_local_chain.get_last_hash())
        print('----------')
        print('New Local File:')
        print(file_name_created)
        print('----------\n')
    except Exception as e:
        print('ERROR: Reading from local chain of files.')
        return


if __name__ == '__main__':

    infinite = True
    configuration = config.parse(read_config())
    print('`•.,,.•´¯¯`•.,,.•´¯¯`•.,, Config ,,.•´¯¯`•.,,.•´¯¯`•.,,.•´\n')
    print_config()

    while infinite:
        print('\n\n¸.•*´¨`*•.¸¸.•*´¨`*•.¸ Results ¸.•*´¨`*•.¸¸.•*´¨`*•.¸\n')
        if configuration.production:
            [print_production_results(configuration, item) for item in configuration.production]
        if configuration.consumption:
            [print_consumption_results(configuration, item) for item in configuration.consumption]

        time.sleep(86400)
