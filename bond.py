import json
import time
import subprocess

import os
from resin import Resin

import core.config_parser as config
import core.data_access as dao
import core.helper as helper


APP_ID = '1001794'


def read_config(app_id: str):
    resin = Resin()
    app_vars = resin.models.environment_variables.device.get_all_by_application(APP_ID)
    # app_vars = resin.models.application.get_config(APP_ID)
    config_json_string = next(var for var in app_vars if var['name'] == 'config')
    return json.loads(config_json_string['value'])


if __name__ == '__main__':
    infinite = True
    print(os.path.isfile('./certificate_of_origin/build/contracts/AssetLogic.json'))
    print(os.path.isfile('certificate_of_origin/build/contracts/AssetLogic.json'))
    print(os.path.isfile('/usr/src/app/certificate_of_origin/build/contracts/AssetLogic.json'))
    print(os.listdir('/usr/local/lib/'))
    print(os.getcwd())
    print(os.listdir(os.getcwd()))

    subprocess.Popen(["./assets/ewf-client-arm", "--jsonrpc-apis", "all", "--reserved-peers", "./tobalaba-peers"],
                     # stdout=subprocess.PIPE,
                     # stderr=subprocess.PIPE
                     )
    print('waiting for ewf-client...\n\n')
    time.sleep(20)
    # while infinite:
    print('`•.,,.•´¯¯`•.,,.•´¯¯`•.,, Config ,,.•´¯¯`•.,,.•´¯¯`•.,,.•´\n')
    configuration = config.parse(read_config(APP_ID))
    if configuration.production is not None:
        print('Energy Production Module: ' + configuration.production.energy.__class__.__name__)
        print('Carbon Emission Saved: ' + configuration.production.carbon_emission.__class__.__name__)
    if configuration.consumption is not None:
        print('Energy Consumption Module: ' + configuration.consumption.energy.__class__.__name__)
    [print('Output: ' + output.__class__.__name__) for output in configuration.outputs]

            # print('\n\n¸.•*´¨`*•.¸¸.•*´¨`*•.¸ Results ¸.•*´¨`*•.¸¸.•*´¨`*•.¸\n')
            # if configuration.production is not None:
            #     production_local_chain = dao.DiskStorage(PRODUCTION_CHAIN)
            #     last_local_chain_hash = production_local_chain.get_last_hash()
            #     last_remote_chain_hash = dao.get_last_hash(configuration)
            #     print('Local and Remote chain sync:')
            #     print(last_local_chain_hash == last_remote_chain_hash)
            #     print('----------')
            #     # Get the remote data.
            #     produced_data = dao.read_production_data(configuration, last_local_chain_hash)
            #     file_name_created = production_local_chain.add_to_chain(produced_data)
            #     print('Produced Energy:')
            #     print(helper.convert_time(produced_data.raw_energy.measurement_epoch))
            #     print(produced_data.raw_energy.accumulated_power)
            #     print('----------')
            #     print('Carbon Emission Today:')
            #     print(helper.convert_time(produced_data.raw_carbon_emitted.measurement_epoch))
            #     print(produced_data.raw_carbon_emitted.accumulated_co2)
            #     print('----------')
            #     print('Sent to Blockchain:')
            #     print(produced_data.produced.to_dict())
            #     print('----------')
            #     print('Lash Remote Hash:')
            #     print(dao.get_last_hash(configuration))
            #     print('----------')
            #     tx_receipt = dao.send_to_origin_contract(configuration, produced_data.produced)
            #     print('Receipt Block Number: ' + str(tx_receipt['blockNumber']))
            #     print('-------------------\n')
            #     print('New Remote Hash:')
            #     print(dao.get_last_hash(configuration))
            #     print('----------')
            #     print('New Local Hash:')
            #     print(production_local_chain.get_last_hash())
            #     print('----------')
            #     print('New Local File:')
            #     print(file_name_created)
            #     print('----------')
            # if configuration.consumption is not None:
            #     consumption_local_chain = dao.DiskStorage(CONSUMPTION_CHAIN)
            #     last_local_chain_hash = consumption_local_chain.get_last_hash()
            #     last_remote_chain_hash = dao.get_last_hash(configuration)
            #     print('Local and Remote chain sync:')
            #     print(last_local_chain_hash == last_remote_chain_hash)
            #     print('----------')
            #     # Get the remote data.
            #     consumed_data = dao.read_consumption_data(configuration, last_local_chain_hash)
            #     file_name_created = consumption_local_chain.add_to_chain(consumed_data)
            #     print('Produced Energy:')
            #     print(helper.convert_time(consumed_data.raw_energy.measurement_epoch))
            #     print(consumed_data.raw_energy.accumulated_power)
            #     print('----------')
            #     print('Sent to Blockchain:')
            #     print(consumed_data.consumed.to_dict())
            #     print('----------')
            #     print('Lash Remote Hash:')
            #     print(dao.get_last_hash(configuration))
            #     print('----------')
            #     tx_receipt = dao.send_to_origin_contract(configuration, consumed_data.consumed)
            #     print('Receipt Block Number: ' + str(tx_receipt['blockNumber']))
            #     print('-------------------\n')
            #     print('New Remote Hash:')
            #     print(dao.get_last_hash(configuration))
            #     print('----------')
            #     print('New Local Hash:')
            #     print(consumption_local_chain.get_last_hash())
            #     print('----------')
            #     print('New Local File:')
            #     print(file_name_created)
            #     print('----------')

        # time.sleep(350)
