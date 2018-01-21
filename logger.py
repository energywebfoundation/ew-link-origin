import json
import time
import web3
from lib import Spinner, Device, LogEntry
import xml.etree.ElementTree as ET

ACCOUNT = '0x00C6fD17d09097424F2CE3E794c6be2934ABBC25'
CONTRACT = '0x122A00cAef700037Bb74D269468c82b21629507F'
PWD = '!12345!'

EUMEL_XML = 'test_examples/EumelXMLOutput.xml'

ABI = json.load(open('abi.json', 'r'))

w3 = web3.Web3(web3.HTTPProvider('http://localhost:8545'))

# Contract instance in concise mode
contract_instance = w3.eth.contract(ABI, CONTRACT, ContractFactoryClass=web3.contract.ConciseContract)


def parse_eumel_xml():
    tree = ET.parse(EUMEL_XML)
    root = tree.getroot()
    header = root[0].attrib
    readings = {child.attrib['id']: child.text for child in root[0][0]}
    device = Device(manufacturer=header['man'], model=header['mod'], serial_number=header['sn'])
    pattern = '%Y-%m-%dT%H:%M:%SZ'
    epoch = int(time.mktime(time.strptime(header['t'], pattern)))
    value = int(readings['TotWhImp'].replace('.', ''))
    log_entry = LogEntry(epoch=epoch, value=value)
    return device, log_entry


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
