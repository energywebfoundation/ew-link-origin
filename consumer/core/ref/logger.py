import json
import time
from xml.etree import ElementTree

import requests
import web3
from core import Spinner, Device, LogEntry

ACCOUNT = '0x00E27b1BB824D66d8ec926f23b04913Fe9b1Bd77'
CONTRACT = '0x122A00cAef700037Bb74D269468c82b21629507F'
PWD = '48qzjbhPdZnw'

EUMEL_XML = 'test_examples/EumelXMLOutput.xml'
EUMEL_IP = ''
EUMEL_ENDPOINT = EUMEL_IP + '/rest'

ABI = json.load(open('abi.json', 'r'))

w3 = web3.Web3(web3.HTTPProvider('http://localhost:8545'))

# Contract instance in concise mode
contract_instance = w3.eth.contract(ABI, CONTRACT, ContractFactoryClass=web3.contract.ConciseContract)


def get_eumel_xml():
    http_request = requests.get(EUMEL_ENDPOINT, auth=('admin', 'aA123456!'))


def parse_eumel_xml():
    #http_packet = requests.get(EUMEL_ENDPOINT, auth=('admin', 'aA123456!'))

    tree = ElementTree.parse(EUMEL_XML)
    tree_root = tree.getroot()
    tree_header = tree_root[0].attrib
    tree_leaves = {child.attrib['id']: child.text for child in tree_root[0][0]}
    parsed_device = Device(manufacturer=tree_header['man'], model=tree_header['mod'], serial_number=tree_header['sn'])
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    converted_epoch_time = int(time.mktime(time.strptime(tree_header['t'], time_format)))
    accumulated_measurement_in_watts = int(tree_leaves['TotWhImp'].replace('.', ''))
    parsed_log_entry = LogEntry(epoch=converted_epoch_time, value=accumulated_measurement_in_watts)
    return parsed_device, parsed_log_entry


def convert_log_entry(epoch, reading):
    pretty_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
    pretty_reading = float(reading) / 100
    return '{} - {:,} Whr'.format(pretty_time, pretty_reading)


def log_values(epoch, reading):
    print('Inserting new values')
    w3.personal.unlockAccount(account=ACCOUNT, passphrase=PWD)
    tx_hash = contract_instance.log(epoch, reading, transact={'from': ACCOUNT})
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
    device, log_entry = parse_eumel_xml()
    log_values(log_entry.epoch, log_entry.value)
    print(device.manufacturer, device.model, device.serial_number)
    print(convert_log_entry(log_entry.epoch, log_entry.value))
    print('------------------')
    print_log_history()


except Exception as e:
    print(e)
    pass
