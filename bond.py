import time
import subprocess

import core.helper as core

PRODUCTION_CHAIN = 'production.pkl'
CONSUMPTION_CHAIN = 'consumption.pkl'


def start_ewf_client():
    subprocess.Popen(["assets/ewf-client-arm", "--jsonrpc-apis", "all", "--reserved-peers", "assets/tobalaba-peers"],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('waiting for ewf-client...\n\n')
    time.sleep(60)


if __name__ == '__main__':
    infinite = True
    while infinite:
        configuration = core.print_config()
        config = {
            "prod_chain_file": PRODUCTION_CHAIN,
            "cons_chain_file": CONSUMPTION_CHAIN,
            "configuration": configuration
        }
        core.schedule(config)
