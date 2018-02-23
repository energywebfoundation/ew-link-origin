import time
import web3

from web3.contract import ConciseContract
from web3.providers import BaseProvider
from core.abstract import SmartContract


class Origin(SmartContract):
    """
    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def __init__(self, address: str, contract: dict, provider: BaseProvider):
        """
        :param address: Contract address on the network
        :param contract: Contract structure containing ABI and BIN
        :param provider: Blockchain client rpc structure containing endpoint URL and connection type
        """
        self.address = address
        self.contract = contract
        self.w3 = web3.Web3(provider)
        self.synced = self.check_sync()
        self.MAX_RETRIES = 1000
        self.SECONDS_BETWEEN_RETRIES = 5

    def check_sync(self) -> bool:
        synced_block = str(self.w3.eth.blockNumber)

        latest_block_obj = self.w3.eth.getBlock('latest')
        latest_block = str(latest_block_obj.number)

        return synced_block == latest_block

    def call(self, method_name: str, password: str, *args) -> dict:
        self.w3.personal.unlockAccount(account=self.address, passphrase=password)
        contract_instance = self.w3.eth.contract(
            self.contract['abi'],
            bytecode=self.contract['bin'],
            ContractFactoryClass=ConciseContract)
        tx_hash = getattr(contract_instance, method_name)(*args)
        tx_receipt = None
        for _ in range(self.MAX_RETRIES):
            tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt and tx_receipt['blockNumber']:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return tx_receipt

    def convert_registry(self, epoch, reading):
        pretty_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
        pretty_reading = float(reading) / 100
        return '{} - {:,} Whr'.format(pretty_time, pretty_reading)
