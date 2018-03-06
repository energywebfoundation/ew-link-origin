import time
import web3

from web3.contract import ConciseContract
from web3.providers import BaseProvider

from core.abstract.output import SmartContractClient


class EnergyWeb(SmartContractClient):
    """
    Energy web Blockchain client api integration. This should work for all parity based clients.

    https://github.com/energywebfoundation/energyweb-client
    https://github.com/paritytech/parity
    """

    def __init__(self, address: str, contract: dict, provider: BaseProvider, password=None):
        """
        :param address: Contract address on the network
        :param contract: Contract structure containing ABI and BIN
        :param provider: Blockchain client rpc structure containing endpoint URL and connection type
        """
        self.address = address
        self.contract = contract
        self.password = password
        self.w3 = web3.Web3(provider)
        self.synced = self.check_sync()
        self.MAX_RETRIES = 1000
        self.SECONDS_BETWEEN_RETRIES = 5

    def check_sync(self) -> bool:
        synced_block = str(self.w3.eth.blockNumber)

        latest_block_obj = self.w3.eth.getBlock('latest')
        latest_block = str(latest_block_obj.number)

        return synced_block == latest_block

    def call(self, method_name: str, *args) -> dict:
        self.w3.personal.unlockAccount(account=self.address, passphrase=self.password)
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


class Origin(EnergyWeb):
    """
    Origin in as smart-contract system deployed on Energy Web Blockchain network.
    It is designed to issue and validate green energy certificates of origin.

    This class is only an interface to a ewf-client via json rpc calls and interact with the smart-contract.
    """

    def __init__(self, asset_id: str, address: str, contract: dict, provider: BaseProvider):
        """
        :param asset_id: ID received in asset registration.
        :param address: Contract address on the network
        :param contract: Contract structure containing ABI and BIN
        :param provider: Blockchain client rpc structure containing endpoint URL and connection type
        """
        self.asset_id = asset_id
        super().__init__(address, contract, provider)

    def register_producer_asset(self, country: str, region: str, zip_code: str, city: str, street: str, house_number: str, latitude: str, longitude: str):
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


class OriginProducer(Origin):
    """
    Green Energy Producer
    """

    def mint_produced_energy(self, energy: int, previous_hash: str, co2_saved: int, service_down: bool):
        """
        function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown )
        Source:
            AssetProducingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown ) external isInitialized onlyAccount(AssetProducingRegistryDB(address(db)).getSmartMeter(_assetId))
        Wait for:
            event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, uint _certificatesCreatedForWh, uint _oldCO2OffsetReading, uint _newCO2OffsetReading, bool _serviceDown);
        """
        receipt = self.call('saveSmartMeterRead', energy, previous_hash, co2_saved, service_down)
        if receipt:
            return receipt
        else:
            raise ConnectionError


class OriginConsumer(Origin):
    """
    Green Energy Consumer
    """

    def mint_consumed_energy(self, energy: int, previous_hash: str, service_down: bool):
        """
        Source:
            AssetProducingRegistryLogic.sol
        Call stack:
            function saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash)
        Wait for:
             event LogNewMeterRead(uint indexed _assetId, uint _oldMeterRead, uint _newMeterRead, uint _certificatesUsedForWh);
        """
        receipt = self.call('saveSmartMeterRead', energy, previous_hash, service_down)
        if receipt:
            return receipt
        else:
            raise ConnectionError

