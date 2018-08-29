import app

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'

if __name__ == '__main__':
    infinite = True
    configuration = app.print_config()
    while infinite:
        config = {
            "configuration": configuration
        }
        app.log(**config)
        app.schedule(config)
