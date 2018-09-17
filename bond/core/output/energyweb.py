import json
import time

import requests
from web3 import HTTPProvider, Web3

from web3.contract import ConciseContract
from web3.providers import BaseProvider

from core.abstract.bond import ProducedChainData, ConsumedChainData, OriginCredentials
from core.abstract.output import SmartContractClient


class GeneralSmartContractClient(SmartContractClient):
    """
    General EVM based blockchain client smart contract integration.
    Tested:
        - https://github.com/paritytech/parity
        - https://github.com/ethereum/go-ethereum
        - https://github.com/energywebfoundation/energyweb-client
    """

    def __init__(self, credentials: tuple, contracts: dict, provider: BaseProvider, max_retries: int, retry_pause: int):
        """
        :param credentials: Network credentials ( address, password )
        :param contracts: Contracts structure containing name, ABI and bytecode and address keys.
        :param provider: Blockchain client rpc structure containing endpoint URL and connection type
        :param max_retries: Software will try to connect to provider this amount of times
        :param retry_pause: Software will wait between reconnection trials this amount of seconds
        """
        self.MAX_RETRIES = max_retries
        self.SECONDS_BETWEEN_RETRIES = retry_pause
        super().__init__(credentials, contracts, provider)

    def check_sync(self) -> bool:
        synced_block = str(self.w3.eth.blockNumber)
        latest_block_obj = self.w3.eth.getBlock('latest')
        latest_block = str(latest_block_obj.number)
        return synced_block == latest_block

    def import_keys(self):
        url = self.url
        payload = {
            "method": "parity_newAccountFromPhrase",
            "params": [self.credentials[0], self.credentials[1]],
            "id": 1,
            "jsonrpc": "2.0"
        }
        r = requests.post(url, json=payload)
        response = r.json()
        return self.w3.toChecksumAddress(response['result'])

    def send(self, address: str, contract_name: str, method_name: str, event_name: str, *args) -> dict:
        # TODO: Implement event catcher when present
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')
        self.w3.personal.unlockAccount(account=self.w3.toChecksumAddress(self.wallet_address), passphrase=self.credentials[1])
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(address),
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        tx_hash = getattr(contract_instance, method_name)(*args, transact={'from': self.w3.toChecksumAddress(self.wallet_address)})
        if not tx_hash:
            raise ConnectionError('Transaction was not sent.')
        tx_receipt = None
        for _ in range(self.MAX_RETRIES):
            tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt and tx_receipt['blockNumber']:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return tx_receipt

    def call(self, address: str, contract_name: str, method_name: str, *args) -> dict:
        # TODO: Implement event catcher when present
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(address),
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        return getattr(contract_instance, method_name)(*args)

    def send_raw(self, contract_name: str, method_name: str, origin: OriginCredentials, *args) -> dict:
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')

        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(origin.contract_address),
            bytecode=contract['bytecode'])

        nonce = self.w3.eth.getTransactionCount(account=self.w3.toChecksumAddress(origin.wallet_add))
        transaction = {
            'from': self.w3.toChecksumAddress(origin.wallet_add),
            'gas': 400000,
            'gasPrice': self.w3.toWei('0', 'gwei'),
            'nonce': nonce,
        }
        tx = getattr(contract_instance.functions, method_name)(*args).buildTransaction(transaction)
        self.w3.eth.enable_unaudited_features()
        private_key = bytearray.fromhex(origin.wallet_pwd)
        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        if not tx_hash:
            raise ConnectionError('Transaction was not sent.')
        tx_receipt = None
        for _ in range(self.MAX_RETRIES):
            tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt and tx_receipt['blockNumber']:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return tx_receipt


class EnergyWeb(GeneralSmartContractClient):
    """
    Energy web Blockchain client rpc.

    https://github.com/energywebfoundation/energyweb-client
    """

    def __init__(self, credentials: tuple, url: str):
        """
        :param credentials: Network credentials ( address, password )
        :param url: Url to connect to Energyweb Client RPC
        """
        params = {
            "contracts": {
                "producer": json.load(open('./assets/AssetProducingRegistryLogic.json')),
                "consumer": json.load(open('./assets/AssetConsumingRegistryLogic.json')),
                "asset": json.load(open('./assets/AssetLogic.json'))
            },
            "provider": HTTPProvider(url),
            "max_retries": 1000,
            "retry_pause": 5
        }
        self.url = url
        super().__init__(credentials, **params)


class Origin(EnergyWeb):
    """
    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def __init__(self, contract_address: str, asset_id: int, wallet_add: str, wallet_pwd: str, url: str):
        """
        :param contract_address: Contract structure containing ABI and bytecode and address keys.
        :param asset_id: ID received in asset registration.
        :param wallet_add: Network wallet address
        :param wallet_add: Network wallet password
        """
        self.asset_id = asset_id
        self.contract_address = contract_address
        credentials = (wallet_add, wallet_pwd)
        super().__init__(credentials, url)

    def register_asset(self, country: str, region: str, zip_code: str, city: str, street: str, house_number: str,
                       latitude: str, longitude: str):
        """
        Register asset. The account signing the transaction must have "AssetAdmin" role to successfully register.
        Source:
            AssetLogic.sol
        Call stack:
            function createAsset() external onlyRole(RoleManagement.Role.AssetAdmin)
            function initLocation ( uint _index, bytes32 _country, bytes32 _region, bytes32 _zip, bytes32 _city, bytes32 _street, bytes32 _houseNumber, bytes32 _gpsLatitude, bytes32 _gpsLongitude ) external isInitialized onlyRole(RoleManagement.Role.AssetAdmin)
            function initGeneral ( uint _index, address _smartMeter, address _owner, AssetType _assetType, Compliance _compliance, uint _operationalSince, uint _capacityWh, bool _active ) external isInitialized userHasRole(RoleManagement.Role.AssetManager, _owner) onlyRole(RoleManagement.Role.AssetAdmin)
        Wait for:
            event LogAssetCreated(address sender, uint id);
            event LogAssetFullyInitialized(uint id);
        """
        pass

    def mint(self, **kwargs):
        """
        Mint the consumption or production of green energy.
        :return:
        """
        raise NotImplementedError

    def last_hash(self, **kwargs):
        """
        Get last file hash logged
        :return:
        """
        raise NotImplementedError


class OriginProducer(Origin):
    """
    Green Energy Producer
    """

    def __last_producer_file_hash(self):
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetDataLog(uint _assetId)
        """
        receipt = self.call(self.contract_address, 'producer', 'getLastSmartMeterReadFileHash', self.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt

    def __mint_produced(self, produced_energy: ProducedChainData) -> dict:
        """
        Source:
            AssetProducingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead( uint _assetId, uint _newMeterRead, bool _smartMeterDown, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown ) external isInitialized onlyAccount(AssetProducingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, bool _smartMeterDown, uint _certificatesCreatedForWh, uint _oldCO2OffsetReading, uint _newCO2OffsetReading, bool _serviceDown);
        """
        receipt = self.send(self.contract_address, 'producer', 'saveSmartMeterRead', 'LogNewMeterRead',
                            self.asset_id, produced_energy.energy, produced_energy.is_meter_down,
                            produced_energy.previous_hash.encode(), produced_energy.co2_saved,
                            produced_energy.is_co2_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def mint(self, produced_energy: ProducedChainData) -> dict:
        return self.__mint_produced(produced_energy)

    def last_hash(self):
        return self.__last_producer_file_hash()


class OriginConsumer(Origin):
    """
    Green Energy Consumer
    """

    def __last_consumer_file_hash(self):
        """
        Get last file hash registered from consumer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetDataLog(uint _assetId)
        """
        receipt = self.call(self.contract_address, 'consumer', 'getLastSmartMeterReadFileHash', self.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt

    def __mint_consumed(self, consumed_energy: ConsumedChainData) -> dict:
        """
        Source:
            AssetConsumingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, bool _smartMeterDown) external isInitialized onlyAccount(AssetConsumingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, uint _certificatesUsedForWh, bool _smartMeterDown);
        """
        receipt = self.send(self.contract_address, 'consumer', 'saveSmartMeterRead', 'LogNewMeterRead',
                            self.asset_id, consumed_energy.energy, consumed_energy.previous_hash.encode(),
                            consumed_energy.is_meter_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def mint(self, consumed_energy: ConsumedChainData) -> dict:
        return self.__mint_consumed(consumed_energy)

    def last_hash(self):
        return self.__last_consumer_file_hash()


class LocalClientOriginProducer(OriginProducer):
    """
    Green Energy Producer running a local ewf client
    """

    def __init__(self, contract_address: str, asset_id: int, wallet_add: str, wallet_pwd: str):
        """
        :param contract_address: Contract structure containing ABI and bytecode and address keys.
        :param asset_id: ID received in asset registration.
        :param wallet_add: Network wallet address
        :param wallet_add: Network wallet password
        """
        url = 'http://localhost:8545'
        super().__init__(contract_address, asset_id, wallet_add, wallet_pwd, url)
        self.wallet_address = self.import_keys()


class LocalClientOriginConsumer(OriginConsumer):
    """
    Green Energy Consumer running a local ewf client
    """

    def __init__(self, contract_address: str, asset_id: int, wallet_add: str, wallet_pwd: str):
        """
        :param contract_address: Contract structure containing ABI and bytecode and address keys.
        :param asset_id: ID received in asset registration.
        :param wallet_add: Network wallet address
        :param wallet_add: Network wallet password
        """
        url = 'http://localhost:8545'
        super().__init__(contract_address, asset_id, wallet_add, wallet_pwd, url)
        self.wallet_address = self.import_keys()


# -----------------------------------------------------------------------------
class RemoteClientOriginProducer(OriginProducer):
    """
    Green Energy Producer accessing a remote ewf client
    """

    def __init__(self, url):
        self.MAX_RETRIES = 1000
        self.SECONDS_BETWEEN_RETRIES = 5
        self.w3 = Web3(HTTPProvider(url))
        self.contracts = {
            "producer": json.load(open('./assets/AssetProducingRegistryLogic.json')),
            "asset": json.load(open('./assets/AssetLogic.json'))
        }

    def __last_producer_file_hash(self, origin: OriginCredentials):
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetDataLog(uint _assetId)
        """
        receipt = self.call(origin.contract_address, 'producer', 'getLastSmartMeterReadFileHash', origin.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt

    def __mint_produced(self, produced_energy: ProducedChainData, origin: OriginCredentials) -> dict:
        """
        Source:
            AssetProducingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead( uint _assetId, uint _newMeterRead, bool _smartMeterDown, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown ) external isInitialized onlyAccount(AssetProducingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, bool _smartMeterDown, uint _certificatesCreatedForWh, uint _oldCO2OffsetReading, uint _newCO2OffsetReading, bool _serviceDown);
        """
        if not isinstance(produced_energy.energy, int):
            raise ValueError('No Produced energy present or in wrong format.')
        if not isinstance(produced_energy.is_meter_down, bool):
            raise ValueError('No Produced energy status present or in wrong format.')
        if not isinstance(produced_energy.previous_hash, str):
            raise ValueError('No Produced hash of last file present or in wrong format.')
        if not isinstance(produced_energy.co2_saved, int):
            raise ValueError('No Produced co2 present or in wrong format.')
        if not isinstance(produced_energy.is_co2_down, bool):
            raise ValueError('No Produced co2 status present or in wrong format.')

        self.credentials = origin.wallet_add, origin.wallet_pwd
        receipt = self.send_raw('producer', 'saveSmartMeterRead', origin, origin.asset_id, produced_energy.energy,
                                produced_energy.is_meter_down, produced_energy.previous_hash.encode(),
                                produced_energy.co2_saved, produced_energy.is_co2_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def mint(self, produced_energy: ProducedChainData, origin: OriginCredentials) -> dict:
        return self.__mint_produced(produced_energy, origin)

    def last_hash(self, origin: OriginCredentials):
        return self.__last_producer_file_hash(origin)

    def last_state(self, origin: OriginCredentials) -> dict:
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetGeneral(uint _assetId)
                external
                constant
                returns(
                    address _smartMeter,
                    address _owner,
                    uint _operationalSince,
                    uint _lastSmartMeterReadWh,
                    bool _active,
                    bytes32 _lastSmartMeterReadFileHash
                    )
        """
        receipt = self.call(origin.contract_address, 'producer', 'getAssetGeneral', origin.asset_id)
        if not receipt:
            raise ConnectionError
        state = {
            "smart_meter": Web3.toText(receipt[0]) if isinstance(receipt[0], bytes) else receipt[0],
            "owner": Web3.toText(receipt[1]) if isinstance(receipt[1], bytes) else receipt[1],
            "since": Web3.toText(receipt[2]) if isinstance(receipt[2], bytes) else receipt[2],
            "last_meter_read": Web3.toInt(receipt[3]) if isinstance(receipt[3], bytes) else receipt[3],
            "is_active": receipt[4],
            "last_hash": Web3.toBytes(receipt[5]) if not isinstance(receipt[5], bytes) else receipt[5],
        }
        return state


# ---------------------------------------------------------------------------------------------------
class RemoteClientOriginConsumer(OriginConsumer):
    """
    Green Energy Consumer accessing a remote ewf client
    """

    def __init__(self, url):
        self.MAX_RETRIES = 1000
        self.SECONDS_BETWEEN_RETRIES = 5
        self.w3 = Web3(HTTPProvider(url))
        self.contracts = {
            "consumer": json.load(open('./assets/AssetConsumingRegistryLogic.json')),
            "asset": json.load(open('./assets/AssetLogic.json'))
        }

    def __last_producer_file_hash(self, origin: OriginCredentials):
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetDataLog(uint _assetId)
        """
        receipt = self.call(origin.contract_address, 'consumer', 'getLastSmartMeterReadFileHash', origin.asset_id)
        if not receipt:
            raise ConnectionError
        return receipt

    def __mint_produced(self, consumed_energy: ConsumedChainData, origin: OriginCredentials) -> dict:
        """
        Source:
            AssetConsumingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, bool _smartMeterDown) external isInitialized onlyAccount(AssetConsumingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, uint _certificatesUsedForWh, bool _smartMeterDown);
        """
        if not isinstance(consumed_energy.energy, int):
            raise ValueError('No Produced energy present or in wrong format.')
        if not isinstance(consumed_energy.is_meter_down, bool):
            raise ValueError('No Produced energy status present or in wrong format.')
        if not isinstance(consumed_energy.previous_hash, str):
            raise ValueError('No Produced hash of last file present or in wrong format.')

        self.credentials = origin.wallet_add, origin.wallet_pwd
        receipt = self.send_raw('consumer', 'saveSmartMeterRead', origin, origin.asset_id, consumed_energy.energy,
                                consumed_energy.previous_hash.encode(), consumed_energy.is_meter_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def mint(self, consumed_energy: ConsumedChainData, origin: OriginCredentials) -> dict:
        return self.__mint_produced(consumed_energy, origin)

    def last_hash(self, origin: OriginCredentials):
        return self.__last_producer_file_hash(origin)

    def last_state(self, origin: OriginCredentials) -> dict:
        """
        Get last file hash registered from producer contract
        Source:
            AssetLogic.sol
        Call stack:
            function getAssetGeneral(uint _assetId)
                external
                constant
                returns (
                    address _smartMeter,
                    address _owner,
                    uint _operationalSince,
                    uint _capacityWh,
                    bool _maxCapacitySet,
                    uint _lastSmartMeterReadWh,
                    uint _certificatesUsedForWh,
                    bool _active,
                    bytes32 _lastSmartMeterReadFileHash
                    )
        """
        receipt = self.call(origin.contract_address, 'consumer', 'getAssetGeneral', origin.asset_id)
        if not receipt:
            raise ConnectionError
        state = {
            "smart_meter": Web3.toText(receipt[0]) if isinstance(receipt[0], bytes) else receipt[0],
            "owner": Web3.toText(receipt[1]) if isinstance(receipt[1], bytes) else receipt[1],
            "since": Web3.toText(receipt[2]) if isinstance(receipt[2], bytes) else receipt[2],
            "capacity": Web3.toInt(receipt[3]) if isinstance(receipt[3], bytes) else receipt[3],
            "is_max_capacity": receipt[4],
            "last_meter_read": Web3.toInt(receipt[5]) if isinstance(receipt[5], bytes) else receipt[5],
            "certificates": Web3.toInt(receipt[6]) if isinstance(receipt[6], bytes) else receipt[6],
            "is_active": receipt[7],
            "last_hash": Web3.toBytes(receipt[8]) if not isinstance(receipt[8], bytes) else receipt[8],
        }
        return state