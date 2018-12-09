
from energyweb import RawEnergyData
from energyweb.log import EnergyLogger

import energyweb.smart_contract.origin_v1 as origin


class Consumer(EnergyLogger):

    def __transform(self, raw_energy: RawEnergyData) -> origin.ConsumedEnergy:
        is_meter_down = raw_energy.raw and raw_energy.energy
        energy_in_wh = raw_energy.energy
        previous_hash = ''
        if isinstance(self.asset.smart_contract, origin.OriginConsumer):
            previous_hash = self.asset.smart_contract.last_hash()
        return origin.ConsumedEnergy(value=raw_energy.energy, previous_hash=previous_hash, is_meter_down=is_meter_down)



# class LogConsumedEnergy(Task):
#
#     def __init__(self, log_path: str, interval: int, is_eager: bool = True):
#         self.log_path = log_path
#         super().__init__(LifeCycle(interval), is_eager)
#
#     def coroutine(self) -> None:
#         paths = {
#             "log_path": self.log_path,
#             "logfile_name": 'energy.log',
#             "errorlog_name": 'energy.error.log',
#             "asset_config": 'config_parser.AssetConfiguration'
#         }
#         energy_logger = EnergyLogger(**paths)
#         self.energy_logger.read_from_devices()
#
#
# class EnergyLoggerApp(App):
#     """
#     Example Application
#     """
#     def prepare(self):
#         print('{} Prepared'.format(self.__class__.__name__))
#
#     def configure(self):
#         t1 = LogEnergy(interval=LifeCycle.THIRTY_MINUTES)
#         t2 = MyTask(interval=6, is_eager=False)
#         [self.add_task(t) for t in [t2, t1]]
#
#     def finish(self):
#         print('{} Finished'.format(self.__class__.__name__))
