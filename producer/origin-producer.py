import json

import core.helper as core

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'

if __name__ == '__main__':
    infinite = True
    configuration_file = json.loads(os.environ['producer'])
    configuration = core.print_config(configuration_file)
    while infinite:
        core.log_production(**configuration)
        core.schedule(configuration)
