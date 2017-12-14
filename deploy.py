import json
import colorlog
import requests
import solc
import time
import web3

from requests import ReadTimeout

from lib import Spinner

CONTRACT_PATH = 'smart_contracts/data_logger.sol'
CONTRACT_NAME = 'DataLogger'
ACCOUNT = '0x00E27b1BB824D66d8ec926f23b04913Fe9b1Bd77'
PASSWORD = '48qzjbhPdZnw'

CONSTRUCTOR = ['siemens', 's5', 'c3dXokd09']

MAX_RETRIES = 100
SECONDS_BETWEEN_RETRIES = 2

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))
# Default color scheme is 'example'
logger = colorlog.getLogger('example')
logger.addHandler(handler)


class AsyncClientError(EnvironmentError):
    pass


print("\
*************************************************************\n\
*           Energy Web Foundation Contract Deployer         *\n\
*                      http://energyweb.org/                *\n\
*                                                           *\n\
*            Copyright © 2017 All rights reserved.          *\n\
*                                                           *\n\
*           This program requires Solidity installed.       *\n\
*               https://solidity.readthedocs.io             *\n\
*************************************************************\n")

try:
    with open(CONTRACT_PATH) as contract_file:
        contract_source_code = contract_file.read()

    if len(contract_source_code) < 10:
        logger.critical("File " + CONTRACT_PATH + " is empty.\n")
        exit()

except FileNotFoundError as e:
    logger.critical("File not found.")
    logger.warning("Quitting.")
    exit()

try:

    logger.info("Compiling contract.")

    # Use solc to compile contract
    compiled_sol = solc.compile_source(contract_source_code) # Compiled source code
    cname = '<stdin>:' + CONTRACT_NAME
    contract_interface = compiled_sol[cname]

    ABI = 'abi.json'
    with open('abi.json', 'w+') as abi:
        abi.write(json.dumps(contract_interface['abi']))
    logger.warning("Abi written to " + ABI)


except solc.exceptions.SolcError as e:
    logger.warning("Failed to compile smart contract. Fix error bellow:\n")
    logger.exception(".")
    logger.warning("Quitting.")
    exit()

except Exception as e:
    logger.error("Unexpected error: " + str(e))
    logger.warning("Quitting.")
    exit()


try:

    logger.info("Connecting to ethereum client.")

    # web3.py instance
    w3 = web3.Web3(web3.HTTPProvider('http://localhost:8545'))

    synced_block_str = str(w3.eth.blockNumber)
    latest_block_obj = w3.eth.getBlock('latest')
    latest_block_str = str(latest_block_obj.number)

    peers = w3.net.peerCount

    if synced_block_str != latest_block_str or peers < 5:
        raise AsyncClientError
    logger.info('Synced \033[1mOK')

    logger.info("Unlocking default Account.")
    w3.personal.unlockAccount(account=ACCOUNT, passphrase=PASSWORD)
    logger.warning("Account unlocked.")

    logger.info("Deploying contract.")
    # Instantiate and deploy contract
    contract = w3.eth.contract(contract_interface['abi'], bytecode=contract_interface['bin'])

    # Get transaction hash from deployed contract
    tx_hash = contract.deploy(transaction={'from': ACCOUNT}, args=CONSTRUCTOR)
    logger.warning("Transaction hash: " + tx_hash)

    logger.info("Waiting Tx to be mined ")
    spinner = Spinner()
    spinner.start()
    for _ in range(MAX_RETRIES):
        # Get tx receipt to get contract address
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        if tx_receipt and tx_receipt['blockNumber']:
            break
        time.sleep(SECONDS_BETWEEN_RETRIES)
    spinner.stop()

    # Status should work but always come as None. :(
    #if tx_receipt['status'] == 0:

    # Show the status to the user
    if tx_receipt['gasUsed'] >= tx_receipt['cumulativeGasUsed']:
        logger.critical("Most probably ran out of gas.")
        logger.critical("Check the Contract address in a block explorer or try to call it.")
        logger.warning("Contract address: " + tx_receipt['contractAddress'])
        logger.warning("Block number: " + str(tx_receipt['blockNumber']))
        logger.warning("Gas used: " + str(tx_receipt['gasUsed']))
    else:
        logger.warning("Contract address: " + tx_receipt['contractAddress'])
        logger.warning("Block number: " + str(tx_receipt['blockNumber']))
        logger.warning("Gas used: " + str(tx_receipt['gasUsed']))

except (requests.exceptions.ConnectionError, ConnectionRefusedError, ReadTimeout):
    logger.critical("Connection timed out. - Please verify that the ethereum client is running.")

except AsyncClientError:
    logger.error("Ethereum client is Out of Sync or Forked. Please check the client log and try again.")

except ValueError as ve:
    message =ve.args[0]['message']
    if message == "Unable to unlock the account.":
        logger.error("Wrong account password.")
    if message == "Method not found":
        logger.error("Unable to access Personal API.")
        logger.error("Run the ethereum client with appending flags: --jsonrpc-apis eth,net,web3,personal")
    else:
        logger.error("Client error message: " + message)

except Exception as e:
    logger.error("Unexpected error: " + str(e))

finally:
    try:
        logger.info("Quitting.")
        logger.info("Locking account.")
        w3.personal.lockAccount(account=ACCOUNT)
        logger.info("Account locked, Bye :)")

    except (requests.exceptions.ConnectionError, ConnectionRefusedError, ReadTimeout):
        logger.info("Connection timed out. - Please verify that the ethereum client is running.")

    # Needed for Geth only. Parity unlocks the acc for a single sign.
    except ValueError as v:
        logger.info("All good, Bye :)")

    except Exception as e:
        logger.info("Unexpected error:", e.args[0]['message'])