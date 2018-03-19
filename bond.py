import time
import datetime

from core.input import carbonemission

from resin import Resin


def convert_time(epoch: int):
    access_time = datetime.datetime.fromtimestamp(epoch)
    return access_time.strftime("%Y-%m-%d  %H:%M:%S")


def read_config(resin: Resin):
    try:
        app_vars = resin.models.environment_variables.device.get_all_by_application('1001794')
        [print(var) for var in app_vars]
    except:
        print('deu ruim')
    try:
        config = resin.models.application.get_config('1001794')
        print(config)
    except:
        print('deu ruim')


if __name__ == '__main__':
    infinite = True
    read_config(Resin())

    while infinite:
        try:

            meter = carbonemission.Wattime('energyweb', 'en3rgy!web')

            fr = meter.read_state('FR', hours_from_now=48)
            print('Wattime - France')
            print(convert_time(fr.measurement_epoch))
            print(fr.accumulated_co2)
            print('----------')

            fr = meter.read_state('National Grid')
            print('Wattime - Uk')
            print(convert_time(fr.measurement_epoch))
            print(fr.accumulated_co2)
            print('----------\n')

        except:
            print('deu ruim')

        time.sleep(350)
