import json
import os

from energyweb import event_loop, log, config, RawEnergyData

import energyweb.smart_contract.origin_v1 as origin


class ConsumerLogger(log.EnergyLogger):
    """
    Read data from the user configured smart-meter and send it to the user configured smart contract.
    """

    def __transform(self, raw_energy: RawEnergyData) -> origin.ConsumedEnergy:
        is_meter_down = raw_energy.raw and raw_energy.energy
        previous_hash = ''
        if isinstance(self.asset.smart_contract, origin.OriginConsumer):
            previous_hash = self.asset.smart_contract.last_hash()
        return origin.ConsumedEnergy(value=raw_energy.energy, previous_hash=previous_hash, is_meter_down=is_meter_down)


class LogConsumedEnergy(event_loop.Task):
    """
    Reads the configuration - therefore the user can change it without the need to restart the app
    Try to access the user provided smart-meter url
    Try to write the measured energy on the energyweb tobalaba chain
    """
    def __init__(self, variable_name: str, interval: event_loop.LifeCycle, is_eager: bool = True):
        """
        :param variable_name: Environment Variable name to read the configuration from. Env vars are safer than files
        because they live in ram memory only, are os protected, and can be safely set by external actors.
        :param interval: Interval to which the energy will be logged
        :param is_eager: When true, will run when the software starts running. If not will wait the first interval.
        """
        self.asset_configuration = config.parse_single_asset(json.loads(os.environ[variable_name]))
        super().__init__(interval=interval, is_eager=is_eager)

    def coroutine(self) -> None:
        # TODO: Add configuration for enabling logs storage, interval and debug mode
        # TODO: Log config only when debugging
        energy_logger = ConsumerLogger(asset=self.asset_configuration, store=None, enable_debug=False)
        # energy_logger.log_configuration()
        energy_logger.log_measured_energy()


class OriginConsumerApp(event_loop.App):
    """
    Energy Consumer Decentralized Application
    Energy Web's Certificate of Origin Project
    """
    def prepare(self):
        print('Preparing to start {}'.format(self.__class__.__name__))
        if not os.environ['CONSUMER']:
            raise EnvironmentError('Add a CONSUMER named variable with the application configuration.')

    def configure(self):
        log_consumed_energy = LogConsumedEnergy(variable_name='CONSUMER', interval=event_loop.LifeCycle.ONE_MINUTE)
        self.add_task(log_consumed_energy)

    def finish(self):
        print('Finishing {}. So long and thanks for all the fish!'.format(self.__class__.__name__))
