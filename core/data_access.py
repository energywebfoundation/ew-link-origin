import hashlib
import json
import os
import pickle

import datetime

from core import base58
from core.abstract.input import ExternalDataSource, ExternalData
from core.abstract.bond import ChainLink, ChainFile, Configuration, ProductionFileData, ConsumptionFileData, \
    ProducedChainData, ConsumedChainData, ChainData, LocalFileData, InputConfiguration, OriginCredentials
from core.output.energyweb import Origin


class DiskStorage:

    def __init__(self, chain_file_name: str, path_to_files: str = './tobalaba/'):
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
    except Exception:
        return None


def read_production_data(config: InputConfiguration, last_hash: str) -> ProductionFileData:
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
    co2_saved = None
    energy = None
    if input_data.raw_carbon_emitted and input_data.raw_energy:
        # x * y kg/Watts = xy kg/Watts
        calculated_co2 = input_data.raw_carbon_emitted.accumulated_co2 * input_data.raw_energy.accumulated_power
        co2_saved = int(calculated_co2 * pow(10, 3))
        energy = int(input_data.raw_energy.accumulated_power)
    produced = {
        'energy': energy if energy else None,
        'is_meter_down': True if input_data.raw_energy is None else False,
        'previous_hash': last_hash,
        'co2_saved': co2_saved,
        'is_co2_down': True if input_data.raw_carbon_emitted is None else False
    }
    input_data.produced = ProducedChainData(**produced)
    return input_data


def read_consumption_data(config: InputConfiguration, last_hash: str) -> ConsumptionFileData:
    """
    Reach for external data sources and return parsed consumed data
    :param last_hash: Last file hash
    :param config: InputConfiguration
    :return: ConsumptionInputData
    """
    input_data_dict = {
        'raw_energy': __fetch_input_data(config.energy),
        'raw_carbon_emitted': __fetch_input_data(config.carbon_emission),
        'consumed': None,
    }
    input_data = ConsumptionFileData(**input_data_dict)
    consumed = {
        'energy': input_data.raw_energy.accumulated_power if input_data.raw_energy else None,
        'is_meter_down': True if input_data.raw_energy is None else False,
        'previous_hash':  last_hash
    }
    input_data.consumed = ConsumedChainData(**consumed)
    return input_data

