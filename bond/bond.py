import core.helper as core

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'

if __name__ == '__main__':
    infinite = True
    configuration = core.print_config()
    while infinite:
        config = {
            "configuration": configuration
        }
        core.log(**config)
        core.schedule(config)
