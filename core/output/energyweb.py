import json
import time
from web3 import HTTPProvider

from web3.contract import ConciseContract
from web3.providers import BaseProvider

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
        self.synced = self.check_sync()
        self.MAX_RETRIES = max_retries
        self.SECONDS_BETWEEN_RETRIES = retry_pause
        super().__init__(credentials, contracts, provider)

    def check_sync(self) -> bool:
        synced_block = str(self.w3.eth.blockNumber)

        latest_block_obj = self.w3.eth.getBlock('latest')
        latest_block = str(latest_block_obj.number)

        return synced_block == latest_block

    def call(self, address: str, contract_name: str, method_name: str, event_name: str, *args) -> dict:
        self.w3.personal.unlockAccount(account=self.credentials[0], passphrase=self.credentials[1])
        contract = self.contracts[contract_name]
        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=address,
            bytecode=contract['bytecode'],
            ContractFactoryClass=ConciseContract)
        tx_hash = getattr(contract_instance, method_name)(*args, transact={'from': self.credentials[0]})
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
                "producer": json.load(open('certificate_of_origin/build/contracts/AssetProducingRegistryLogic.json')),
                "consumer": json.load(open('certificate_of_origin/build/contracts/AssetProducingRegistryLogic.json')),
                "asset": json.load(open('certificate_of_origin/build/contracts/AssetLogic.json'))
            },
            "provider": HTTPProvider(url),
            "max_reties": 1000,
            "retry_pause": 5
        }
        super().__init__(credentials, **params)


class Origin(EnergyWeb):
    """
    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def __init__(self, asset_id: int, credentials: tuple, contract_address: str, url: str = 'http://localhost:8545'):
        """
        :param asset_id: ID received in asset registration.
        :param credentials: Network credentials ( address, password )
        :param contract: Contract structure containing ABI and bytecode and address keys.
        :param provider: Blockchain client rpc structure containing endpoint URL and connection type
        """
        self.asset_id = asset_id
        self.contract_address = contract_address
        super().__init__(credentials, url)

    def register_asset(self, country: str, region: str, zip_code: str, city: str, street: str, house_number: str, latitude: str, longitude: str):
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

    def mint_produced(self, energy: int, is_meter_down: bool, previous_hash: str, co2_saved: int, is_co2_down: bool) -> dict:
        """
        Source:
            AssetProducingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead( uint _assetId, uint _newMeterRead, bool _smartMeterDown, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown ) external isInitialized onlyAccount(AssetProducingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, bool _smartMeterDown, uint _certificatesCreatedForWh, uint _oldCO2OffsetReading, uint _newCO2OffsetReading, bool _serviceDown);
        """
        receipt = self.call(self.contract_address, 'producer', 'saveSmartMeterRead', 'LogNewMeterRead',
                            self.asset_id, energy, is_meter_down, previous_hash, co2_saved, is_co2_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def mint_consuming(self, energy: int, previous_hash: str, is_meter_down: bool):
        """
        Source:
            AssetConsumingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, bool _smartMeterDown) external isInitialized onlyAccount(AssetConsumingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, uint _certificatesUsedForWh, bool _smartMeterDown);
        """
        receipt = self.call(self.contract_address, 'consumer', 'saveSmartMeterRead', 'LogNewMeterRead',
                            self.asset_id, energy, previous_hash, is_meter_down)
        if not receipt:
            raise ConnectionError
        return receipt

    def mint(self, **kwargs):
        """
        Mint the consumption or production of green energy.
        :return:
        """
        raise NotImplementedError


class LocalClientOriginProducer(Origin):
    """
    Green Energy Producer
    """

    def mint(self, energy: int, is_meter_down: bool, previous_hash: str, co2_saved: int, is_co2_down: bool) -> dict:
        return self.mint_produced(energy, is_meter_down, previous_hash, co2_saved, is_co2_down)


class LocalClientOriginConsumer(Origin):
    """
    Green Energy Consumer
    """

    def mint(self, energy: int, previous_hash: str, is_meter_down: bool):
        return self.mint_consuming(energy, previous_hash, is_meter_down)
