"""
General external data output interfaces
"""


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

    def check_sync(self) -> bool:
        """
        Compares latest block from peers with client's last synced block.
        :return: Synced status
        :rtype: bool
        """
        raise NotImplementedError

    def call(self, method_name, password, args=None) -> dict:
        """
        Calls a contract
        Sends a transaction to the Blockchain and awaits for mining until a receipt is returned.
        :param method_name: Use the same name as found in the contract abi
        :param password: String of the raw password
        :param args: Method parameters
        :return: Transaction receipt
        :rtype: dict
        """
        raise NotImplementedError

    def convert_registry(self, *args):
        """
        Converts stored data format to human readable
        """
        raise NotImplementedError
