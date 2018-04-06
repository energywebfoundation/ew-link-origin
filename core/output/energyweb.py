import json
import time
from web3 import HTTPProvider

from web3.contract import ConciseContract
from web3.providers import BaseProvider

from core.abstract.bond import ProducedChainData, ConsumedChainData
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

    def send(self, address: str, contract_name: str, method_name: str, event_name: str, *args) -> dict:
        # TODO: Implement event catcher when present
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')
        self.w3.personal.unlockAccount(account=self.credentials[0], passphrase=self.credentials[1])
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=address,
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        tx_hash = getattr(contract_instance, method_name)(*args, transact={'from': self.credentials[0]})
        if not tx_hash:
            raise ConnectionError('Transaction was not sent.')
        tx_receipt = None
        for _ in range(self.MAX_RETRIES):
            tx_receipt = self.w3.eth.getTransactionReceipt(tx_hash)
            if tx_receipt and tx_receipt['blockNumber']:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return tx_receipt

    def call(self, address: str, contract_name: str, method_name: str, event_name: str, *args) -> dict:
        # TODO: Implement event catcher when present
        if not self.check_sync():
            raise ConnectionError('Client is not synced to the last block.')
        self.w3.personal.unlockAccount(account=self.credentials[0], passphrase=self.credentials[1])
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=address,
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        return getattr(contract_instance, method_name)(*args)


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
                "producer": json.load(open('certificate_of_origin/build/contracts/AssetProducingRegistryLogic.json')),
                "consumer": json.load(open('certificate_of_origin/build/contracts/AssetProducingRegistryLogic.json')),
                "asset": json.load(open('certificate_of_origin/build/contracts/AssetLogic.json'))
            },
            "provider": HTTPProvider(url),
            "max_retries": 1000,
            "retry_pause": 5
        }
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
        receipt = self.call(self.contract_address, 'producer', 'getLastSmartMeterReadFileHash', '', self.asset_id)
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
                            produced_energy.previous_hash, produced_energy.co2_saved, produced_energy.is_co2_down)
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
        receipt = self.call(self.contract_address, 'consumer', 'getLastSmartMeterReadFileHash', '', self.asset_id)
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
                            self.asset_id, consumed_energy.energy, consumed_energy.previous_hash,
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


class RemoteClientOriginProducer(OriginProducer):
    """
    Green Energy Producer accessing a remote ewf client
    """


class RemoteClientOriginConsumer(OriginConsumer):
    """
    Green Energy Consumer accessing a remote ewf client
    """
