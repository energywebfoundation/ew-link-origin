import subprocess
import time
from bond.origin import origin as origin

JSON = 'origin/assets/local-consumer.json'


# Helper to spawn an Tobalaba client on execution
def start_ewf_client():
    subprocess.Popen(["/usr/local/bin/ewf-client", "--jsonrpc-apis", "all", "--reserved-peers",
                      "/assets/tobalaba-peers"], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
    print('waiting for ewf-client...\n\n')
    time.sleep(60)


# The original bond code is executed on a scheduled basis and connects to all producers and consumers listed on
# the json file. After gathering data on the api it signs a transaction to a smart-contract and sends it
# to the client also specified on the json file.
# This method jumps the scheduling process, logs the data on time of execution and exits.
if __name__ == '__main__':
    configuration = origin.print_config(JSON)
    origin.log(configuration)
