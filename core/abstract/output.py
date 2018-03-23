"""
General external data output interfaces
"""
import web3


class LogEntry:
    """
    Standard for logging data2
    """

    def __init__(self, epoch, value):
        """
        :param epoch:  Time the value was measured in epoch format
        :param value:  Measured value
        """
        self.epoch = epoch
        self.value = value


class AsyncClientError(EnvironmentError):
    """
    Ethereum-like smart contracts abstraction
    """
    pass


class SmartContractClient:
    """
    Ethereum-like smart contracts abstraction
    """

    def __init__(self, credentials: tuple, contracts: dict, provider: web3.providers.BaseProvider):
        """
        :param credentials: Network credentials ( address, password )
        :param contracts: Contract structure containing name, ABI and bytecode and address keys.
        :param provider: Blockchain client rpc structure containing endpoint URL and connection type
        """
        self.credentials = credentials
        self.contract = contract
        self.w3 = web3.Web3(provider)

    def check_sync(self) -> bool:
        """
        Compares latest block from peers with client's last synced block.
        :return: Synced status
        :rtype: bool
        """
        raise NotImplementedError

    def call(self, address: str, contract_name: str, method_name: str, password: str, args=None) -> dict:
        """
        Calls a contract
        Sends a transaction to the Blockchain and awaits for mining until a receipt is returned.
        :param address: Contract address
        :param contract_name: Name of the contract in contracts
        :param method_name: Use the same name as found in the contract abi
        :param password: String of the raw password
        :param args: Method parameters
        :return: Transaction receipt
        :rtype: dict
        """
        raise NotImplementedError
