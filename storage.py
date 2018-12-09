from energyweb import Serializable, RawEnergyData, RawCarbonEmissionData
from energyweb.smart_contract.origin_v1 import ConsumedEnergy, ProducedEnergy
from energyweb.storage import DiskStorage


class LocalDiskStorage(DiskStorage):

    def add_to_chain(self, data: Serializable) -> str:
        """
        Add new file to chain.
        :param data: Data to store
        :return: Base58 hash string
        """
        if isinstance(data, ProductionFileData):
            self.path += 'production/'
        else:
            self.path += 'consumption/'
        super().add_to_chain(data)


class ConsumptionFileData(Serializable):
    """
    Structure of every consumption data stored on disk
    """
    def __init__(self, raw_energy: RawEnergyData, consumed: ConsumedEnergy):
        self.raw_energy = raw_energy
        self.consumed = consumed


class ProductionFileData(Serializable):
    """
    Structure of every production data stored on disk
    """
    def __init__(self, raw_energy: RawEnergyData, raw_carbon_emitted: RawCarbonEmissionData, produced: ProducedEnergy):
        self.raw_energy = raw_energy
        self.raw_carbon_emitted = raw_carbon_emitted
        self.produced = produced
