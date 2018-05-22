"""
Data Structures for binding input data into chained data
"""
import datetime

from core.abstract import JSONAble
from core.abstract.input import EnergyData, CarbonEmissionData, EnergyDataSource, CarbonEmissionDataSource
from core.abstract.output import SmartContractClient


class LocalFileData(JSONAble):
    pass


class ChainData(JSONAble):
    pass


class ProducedChainData(ChainData):
    """
    Helper for mint_produced
    """
    def __init__(self, energy: int, is_meter_down: bool, previous_hash: str, co2_saved: int, is_co2_down: bool):
        """
        :type previous_hash: previous
        :param energy:  Time the value was measured in epoch format
        :param is_meter_down:  Measured value
        """
        self.energy = energy
        self.is_meter_down = is_meter_down
        self.previous_hash = previous_hash
        self.co2_saved = co2_saved
        self.is_co2_down = is_co2_down


class ConsumedChainData(ChainData):
    """
    Helper for mint_consumed
    """
    def __init__(self, energy: int, previous_hash: str, is_meter_down: bool):
        """
        :type previous_hash: previous
        :param energy:  Time the value was measured in epoch format
        :param is_meter_down:  Measured value
        """
        self.energy = energy
        self.is_meter_down = is_meter_down
        self.previous_hash = previous_hash


class ProductionFileData(LocalFileData):
    """
    Structure of every production data stored on disk
    """
    def __init__(self, raw_energy: EnergyData, raw_carbon_emitted: CarbonEmissionData, produced: ProducedChainData):
        self.raw_energy = raw_energy
        self.raw_carbon_emitted = raw_carbon_emitted
        self.produced = produced


class ConsumptionFileData(LocalFileData):
    """
    Structure of every consumption data stored on disk
    """
    def __init__(self, raw_energy: EnergyData, consumed: ConsumedChainData):
        self.raw_energy = raw_energy
        self.consumed = consumed


class ChainFile:

    def __init__(self, file: str, timestamp: datetime.datetime):
        self.file = file
        self.timestamp = timestamp


class ChainLink:

    def __init__(self, data: ChainFile, last_link: object):
        self.data = data
        self.last_link = last_link

    def __next__(self):
        return self.last_link


class OriginCredentials(JSONAble):
    def __init__(self, contract_address: str, asset_id: int, wallet_add: str, wallet_pwd: str):
        self.contract_address = contract_address
        self.asset_id = asset_id
        self.wallet_add = wallet_add
        self.wallet_pwd = wallet_pwd


class InputConfiguration:

    def __init__(self, energy: EnergyDataSource, origin: OriginCredentials, carbon_emission: CarbonEmissionDataSource, name: str):
        if not isinstance(energy, EnergyDataSource):
            raise AttributeError
        if not isinstance(origin, OriginCredentials):
            raise AttributeError
        if carbon_emission is not None and not isinstance(carbon_emission, CarbonEmissionDataSource):
            raise AttributeError
        self.energy = energy
        self.origin = origin
        self.carbon_emission = carbon_emission
        self.name = name


class Configuration:

    def __init__(self, production: [InputConfiguration], consumption: [InputConfiguration], client: SmartContractClient):
        self.production = production
        self.consumption = consumption
        self.client = client

    def __check(self, production, consumption, client):
        [self.__check_input_config(item) for item in production]
        [self.__check_input_config(item) for item in consumption]
        if not issubclass(client.__class__, SmartContractClient):
            raise AttributeError('Must have strictly one blockchain client.')

    @staticmethod
    def __check_input_config(obj):
        if not isinstance(obj, InputConfiguration):
            raise AttributeError('Configuration file contain errors.')
