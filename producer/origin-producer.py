import json
import os

import core.helper as core

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'

if __name__ == '__main__':
    infinite = True
    configuration_file = json.loads(os.environ['PRODUCER'])
    configuration = core.print_config(configuration_file)
    while infinite:
        print('running prod')
        core.log_production(**configuration)
        print('log production')
        core.schedule(configuration)
        print('schedule')
