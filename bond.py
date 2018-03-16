import time
import datetime

from core.input import carbonemission


def convert_time(epoch: int):
    access_time = datetime.datetime.fromtimestamp(epoch)
    return access_time.strftime("%Y-%m-%d  %H:%M:%S")


if __name__ == '__main__':
    infinite = True
    while infinite:
        meter = carbonemission.Wattime('energyweb', 'en3rgy!web', 24)

        fr = meter.read_state('FR')
        print('Wattime - France')
        print(convert_time(fr.measurement_epoch))
        print(fr.accumulated_co2)
        print('----------')

        time.sleep(5)