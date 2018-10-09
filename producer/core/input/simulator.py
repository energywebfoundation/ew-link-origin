import calendar
import datetime
import random

from core.abstract.input import EnergyDataSource, EnergyData, Device


class EnergyMeter(EnergyDataSource):
    """
    Data logger simulator. It will return a pseudo-randomized incremental value in every iteration
    """

    def __init__(self):
        self.memory = random.randint(1, 20)

    def read_state(self) -> EnergyData:
        now = datetime.datetime.now().astimezone()
        access_epoch = calendar.timegm(now.timetuple())
        device = Device(
            manufacturer='Slock.it',
            model='Virtual Energy Meter',
            serial_number='0001000',
            geolocation=(1.123, 1.321))
        accumulated_power = random.randint(self.memory, (self.memory + 1) + 20)
        measurement_epoch = calendar.timegm(now.timetuple())
        device_str = device.manufacturer + device.model + device.serial_number
        raw = str(device_str + str(access_epoch) + str(accumulated_power) + str(measurement_epoch))
        return EnergyData(device=device, access_epoch=access_epoch, raw=raw, accumulated_energy=accumulated_power,
                          measurement_epoch=measurement_epoch)
