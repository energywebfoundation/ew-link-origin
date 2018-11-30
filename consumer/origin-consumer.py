import json
import os

import core.helper as core

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'

if __name__ == '__main__':
    infinite = True
    configuration_file = json.load(open(os.environ['CONFIG']))
    configuration = core.print_config(configuration_file)
    while infinite:
        core.log_consumption(**configuration)
        core.schedule(configuration)
