#!/usr/bin/env python
import datetime
import json
import time
import urllib

import energyweb

from energyweb.config import CooV1ConsumerConfiguration, CooV1ProducerConfiguration


class CooGeneralTask(energyweb.Logger, energyweb.Task):

    def __init__(self, task_config: energyweb.config.CooV1ConsumerConfiguration, polling_interval: datetime.timedelta,
                 store: str = '', enable_debug: bool = False):
        """
        :param task_config: Consumer configuration class instance
        :param polling_interval: Time interval between interrupts check
        :param store: Path to folder where the log files will be stored in disk. DEFAULT won't store data in-disk.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        self.task_config = task_config
        self.chain_file_name = 'origin.pkl'
        self.msg_success = 'minted %s watts - block # %s'
        self.msg_error = 'energy_meter: %s - stack: %s'
        energyweb.Logger.__init__(self, log_name=task_config.name, store=store, enable_debug=enable_debug)
        energyweb.Task.__init__(self, polling_interval=polling_interval, eager=False)

    def main(self, duration: int = 3):
        running = True
        self._log_configuration()
        while running:
            self._log_measured_energy()
            time.sleep(duration)
        return False

    def _log_configuration(self):
        """
        Outputs the logger configuration
        """
        message = '[CONFIG] name: %s - energy energy_meter: %s'
        if self.store and self.enable_debug:
            self.console.debug('[CONFIG] path to logs: %s', self.store)
        self.console.debug(message, self.task_config.name, self.task_config.energy_meter.__class__.__name__)

    def _log_measured_energy(self):
        """
        Try to reach the energy_meter and logs the measured energy.
        Wraps the complexity of the data read and the one to be written to the smart-contract
        """
        try:
            # Get the data by accessing the external energy device
            # Storing logs locally
            if self.store:
                local_storage = energyweb.DiskStorage(path_to_files=self.store,
                                                      chain_file_name=self.chain_file_name)
                last_file_hash = local_storage.get_last_hash()
                energy_data = self._transform(local_file_hash=last_file_hash)
                if not energy_data.is_meter_down:
                    local_chain_file = local_storage.add_to_chain(data=energy_data)
                    self.console.info('%s created', local_chain_file)
            else:
                last_chain_hash = self.task_config.smart_contract.last_hash()
                energy_data = self._transform(local_file_hash=last_chain_hash)
            # Logging to the blockchain
            tx_receipt = self.task_config.smart_contract.mint(energy_data)
            block_number = str(tx_receipt['blockNumber'])
            self.console.info(self.msg_success, energy_data.to_dict(), block_number)
        except Exception as e:
            self.console.exception(self.msg_error, self.task_config.energy_meter.__class__.__name__, e)
            self.console.warning('Smart-contract is unreachable.')

    def _transform(self, local_file_hash: str):
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract and configuration type.
        """
        raise NotImplementedError

    def _fetch_remote_data(self, ip: energyweb.IntegrationPoint) -> (energyweb.ExternalData, bool):
        """
        Tries to reach external device for data.
        Returns smart-contract friendly data and logs error in case of failing.
        :param ip: Energy or Carbon Emission Device
        :return: Energy or Carbon Emission Data, Is device offline flag
        """
        try:
            result = ip.read_state()
            if not issubclass(result.__class__, energyweb.ExternalData):
                raise AssertionError('Make sure to inherit ExternalData when reading data from IntegrationPoint.')
            return result, False
        except Exception as e:
            # TODO debug log self.error_log
            self.console.exception(self.msg_error, self.task_config.energy_meter.__class__.__name__, e)
            return None, True


class CooProducerTask(CooGeneralTask):

    def __init__(self, task_config: CooV1ProducerConfiguration, polling_interval: datetime.timedelta, store: str = None,
                 enable_debug: bool = False):
        """
        :param task_config: Producer configuration class instance
        :param polling_interval: Time interval between interrupts check
        :param store: Path to folder where the log files will be stored in disk. DEFAULT won't store data in-disk.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        super().__init__(task_config=task_config, polling_interval=polling_interval, store=store,
                         enable_debug=enable_debug)

    def _transform(self, local_file_hash: str) -> energyweb.EnergyData:
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract and configuration type.
        """
        raw_energy, is_meter_down = self._fetch_remote_data(self.task_config.energy_meter)
        if not self.task_config.energy_meter.is_accumulated:
            last_remote_state = self.task_config.smart_contract.last_state()
            raw_energy.energy += last_remote_state[3] # get the fourth element returned from the contract from last_state: uint _lastSmartMeterReadWh
        raw_carbon_emitted, is_co2_down = self._fetch_remote_data(self.task_config.carbon_emission)
        calculated_co2 = raw_energy.energy * raw_carbon_emitted.accumulated_co2
        produced = {
            'value': int(raw_energy.energy),
            'is_meter_down': is_meter_down,
            'previous_hash': local_file_hash,
            'co2_saved': int(calculated_co2),
            'is_co2_down': is_co2_down
        }
        return energyweb.ProducedEnergy(**produced)


class CooConsumerTask(CooGeneralTask):

    def __init__(self, task_config: CooV1ConsumerConfiguration, polling_interval: datetime.timedelta, store: str = None,
                 enable_debug: bool = False):
        """
        :param task_config: Consumer configuration class instance
        :param polling_interval: Time interval between interrupts check
        :param store: Path to folder where the log files will be stored in disk. DEFAULT won't store data in-disk.
        :param enable_debug: Enabling debug creates a log for errors. Needs storage. Please manually delete it.
        """
        super().__init__(task_config=task_config, polling_interval=polling_interval, store=store, enable_debug=enable_debug)

    def _transform(self, local_file_hash: str) -> energyweb.EnergyData:
        """
        Transforms the raw external energy data into blockchain format. Needs to be implemented for each different
        smart-contract and configuration type.
        """
        raw_energy, is_meter_down = self._fetch_remote_data(self.task_config.energy_meter)
        if not self.task_config.energy_meter.is_accumulated:
            last_remote_state = self.task_config.smart_contract.last_state()
            raw_energy.energy += last_remote_state[3]
        consumed = {
            'value': int(raw_energy.energy),
            'is_meter_down': is_meter_down,
            'previous_hash': local_file_hash,
        }
        return energyweb.ConsumedEnergy(**consumed)


class NetworkTask(energyweb.Task):
    """
    Example Task reading and writing network
    """
    def prepare(self):
        print('Net try open')
        return super().prepare()

    def main(self, number):
        try:
            net = urllib.request.urlopen(f'http://localhost:8000/{number}')
        except urllib.error.URLError:
            print('Net unavailable')
            return True

        response = net.read().decode().strip()
        if response == 'ja':
            print('Here we go', end='')
            for _ in range(3):
                print('.', end='', flush=True)
                time.sleep(1)
            print('')
        elif response == 'stop':
            return False
        return True

    def finish(self):
        print('Net close')
        return super().finish()


class MyApp(energyweb.dispatcher.App):

    def configure(self):
        try:
            app_configuration_file = json.load(open('config.json'))
            app_config = energyweb.config.parse_coo_v1(app_configuration_file)
            interval = datetime.timedelta(seconds=3)
            for producer in app_config.production:
                self.add_task(CooProducerTask(task_config=producer, polling_interval=interval, store='/tmp/origin/produce'))
            for consumer in app_config.consumption:
                self.add_task(CooConsumerTask(task_config=consumer, polling_interval=interval, store='/tmp/origin/consume'))
        except energyweb.config.ConfigurationFileError as e:
            print(f'Error in configuration file: {e}')
        except Exception as e:
            print(f'Fatal error: {e}')


if __name__ == '__main__':
    MyApp().run()
