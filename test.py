import json
import time
from random import randrange

import web3

from lib import Spinner

ACCOUNT = '0x00E27b1BB824D66d8ec926f23b04913Fe9b1Bd77'
CONTRACT = '0xC2c4e2E135d3E1963d375E20AB8d40ee9eEDb7Fe'
PWD = '48qzjbhPdZnw'

ABI = json.load(open('abi.json', 'r'))

w3 = web3.Web3(web3.HTTPProvider('http://localhost:8545'))

# Contract instance in concise mode
contract_instance = w3.eth.contract(ABI, CONTRACT, ContractFactoryClass=web3.contract.ConciseContract)


def convert_log_entry(epoch, reading):
    pretty_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
    pretty_reading = float(reading) / 10
    return '{} - {:,} mW'.format(pretty_time, pretty_reading)


def check_values():
    log_size = contract_instance.getLogSize()
    print('Log size: {}'.format(log_size))
    if log_size > 0:
        epoch, reading = contract_instance.registry(log_size-1)
        print('Latest log value: {} - {}'.format(epoch, reading))
        print('Pretty printing: ' + convert_log_entry(epoch, reading))


def input_random_values():
    print('Inserting new values')
    w3.personal.unlockAccount(account=ACCOUNT, passphrase=PWD)
    return contract_instance.log(int(time.time()), randrange(0, 100, 2), transact={'from': ACCOUNT})


def check_transaction(tx_hash):
    print("Waiting Tx to be mined ")
    spinner = Spinner()
    spinner.start()
    for _ in range(100):
        # Get tx receipt to get contract address
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        if tx_receipt and tx_receipt['blockNumber']:
            break
        time.sleep(2)
    spinner.stop()


def print_log_history():
    print('Log History:')
    log_size = contract_instance.getLogSize()
    if log_size > 0:
        for entry in range(log_size):
            epoch, reading = contract_instance.registry(entry)
            print('Pretty printing: ' + convert_log_entry(epoch, reading))


try:
    check_values()
    tx_hash = input_random_values()
    check_transaction(tx_hash)
    check_values()
    print('------------------')
    print_log_history()


except Exception as e:
    print(e)
    print('- DEU RUIM CORAI')
    pass
