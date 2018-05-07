import os
import json
import pickle
import hashlib
import datetime

from core import base58

from core.abstract.input import ExternalDataSource, ExternalData
from core.abstract.bond import ChainLink, ChainFile, ProductionFileData, ConsumptionFileData, ProducedChainData, \
    ConsumedChainData, LocalFileData, InputConfiguration

from core.input.eumel import DataLoggerV1, DataLoggerV2d1d1


class DiskStorage:

    def __init__(self, chain_file_name: str, path_to_files: str = '/mnt/data/tobalaba/'):
        """
        :param chain_file_name:
        :param path_to_files:
        """
        self.chain_file = path_to_files + chain_file_name
        self.path = path_to_files
        if not os.path.exists(path_to_files):
            os.makedirs(path_to_files)
        if not os.path.exists(self.chain_file):
            self.__memory = None
        else:
            self.__memory = pickle.load(open(self.chain_file, 'rb'))

    @property
    def chain(self) -> ChainLink:
        return self.__memory

    @chain.setter
    def chain(self, chain_link: ChainLink):
        if chain_link is not None:
            raise AttributeError
        self.__chain_append(chain_link)

    def add_to_chain(self, data: LocalFileData) -> str:
        """
        Add new file to chain.
        :param data: Data to store
        :return: Base58 hash string
        """
        data_file_name = self.__save_file(data)
        chain_data = ChainFile(data_file_name, datetime.datetime.now())
        new_link = ChainLink(data=chain_data, last_link=self.chain)
        self.__chain_append(new_link)
        self.__save_memory()
        return data_file_name

    def get_last_hash(self) -> str:
        """
        Get hash of the last chain file.
        :return: Base58 hash string
        """
        if self.chain:
            # sha3 = hashlib.sha3_256()
            sha3 = hashlib.sha1()
            sha3.update(open(self.chain.data.file, 'rb').read())
            base58_digest = base58.b58encode(sha3.digest())
            return 'Qm' + base58_digest
        else:
            return '0x0'

    def __chain_append(self, chain_link: ChainLink):
        self.__memory = chain_link
        self.__save_memory()

    def __save_memory(self):
        pickle.dump(self.__memory, open(self.chain_file, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

    def __save_file(self, data):
        if isinstance(data, ProductionFileData):
            prefix = self.path + 'production/'
        else:
            prefix = self.path + 'consumption/'
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        file_name_mask = prefix + '%Y-%m-%d-%H:%M:%S.json'
        file_name = datetime.datetime.now().strftime(file_name_mask)
        with open(file_name, 'w+') as file:
            json.dump(data.to_dict(), file)
        return file_name


def __fetch_input_data(external_data_source: ExternalDataSource):
    try:
        result = external_data_source.read_state()
        if not issubclass(result.__class__, ExternalData):
            raise AssertionError
        return result
    except Exception as e:
        return None


def read_production_data(config: InputConfiguration, last_hash: str, last_state: list) -> ProductionFileData:
    """
    Reach for external data sources and return parsed consumed data
    :param last_hash: Last file hash
    :param config: Configuration
    :return: ProductionInputData
    """
    input_data_dict = {
        'raw_energy': __fetch_input_data(config.energy),
        'raw_carbon_emitted': __fetch_input_data(config.carbon_emission),
        'produced': None,
    }
    input_data = ProductionFileData(**input_data_dict)
    co2_saved = input_data.raw_carbon_emitted.accumulated_co2 if input_data.raw_carbon_emitted else 0
    energy = input_data.raw_energy.accumulated_power if input_data.raw_energy else 0
    # add last measured energy in case it is not accumulated
    # TODO: refactor this to the data input classes
    if not (isinstance(config.energy, DataLoggerV1) or isinstance(config.energy, DataLoggerV2d1d1)):
        last_energy = last_state[3]
        energy += last_energy
    # x * y kg/Watts = xy kg/Watts
    calculated_co2 = energy * co2_saved
    co2_saved = int(calculated_co2 * pow(10, 3))
    energy = int(energy)
    produced = {
        'energy': energy,
        'is_meter_down': True if input_data.raw_energy is None else False,
        'previous_hash': last_hash,
        'co2_saved': co2_saved,
        'is_co2_down': True if input_data.raw_carbon_emitted is None else False
    }
    input_data.produced = ProducedChainData(**produced)
    return input_data


def read_consumption_data(config: InputConfiguration, last_hash: str, last_state: list) -> ConsumptionFileData:
    """
    Reach for external data sources and return parsed consumed data
    :param last_hash: Last file hash
    :param config: InputConfiguration
    :return: ConsumptionInputData
    """
    input_data_dict = {
        'raw_energy': __fetch_input_data(config.energy),
        'consumed': None,
    }
    input_data = ConsumptionFileData(**input_data_dict)
    # add last measured energy in case it is not accumulated
    # TODO: refactor this to the data input classes
    energy = int(input_data.raw_energy.accumulated_power) if input_data.raw_energy else 0
    if not (isinstance(config.energy, DataLoggerV1) or isinstance(config.energy, DataLoggerV2d1d1)):
        last_energy = last_state[5]
        energy += last_energy
    consumed = {
        'energy': energy,
        'is_meter_down': True if input_data.raw_energy is None else False,
        'previous_hash':  last_hash
    }
    input_data.consumed = ConsumedChainData(**consumed)
    return input_data

