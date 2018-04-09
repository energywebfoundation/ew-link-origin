import importlib
import json

from core.abstract.bond import InputConfiguration, Configuration


def __get_input_configuration(configuration: dict) -> InputConfiguration:
    try:
        instance = {
            "energy": __get_class_instances(configuration['energy']),
            "carbon_emission": __get_class_instances(configuration['carbonemission']),
        }
        return InputConfiguration(**instance)
    except Exception:
        return None


def __get_class_instances(submodule: dict) -> object:
    """
    Reflection algorithm to dynamically load python modules referenced on the configuration json.
    :param submodule: Configuration dict must have the keys 'module', 'class_name', 'class_parameters'.
    :return: Class instance as in config file.
    """
    module_instance = importlib.import_module(submodule['module'])
    class_obj = getattr(module_instance, submodule['class_name'])
    class_instance = class_obj(**submodule['class_parameters'])
    return class_instance


def parse_file(config_file_path: str) -> Configuration:
    """
    Read config file into structured class instances.
    :param config_file_path: File system path to json format file.
    :return: Configuration instance
    """
    config_json = json.load(open(config_file_path))
    return parse(config_json)


def parse(config_dict: dict) -> Configuration:
    """
    Read config file into structured class instances.
    :param config_dict: Config dictionary.
    :return: Configuration instance
    """
    is_consuming = 'consumption' in config_dict
    is_producing = 'production' in config_dict
    instance = {
        "consumption": __get_input_configuration(config_dict['consumption'] if is_consuming else None),
        "production": __get_input_configuration(config_dict['production'] if is_producing else None),
        "outputs": [__get_class_instances(output) for output in config_dict['outputs']]
    }
    return Configuration(**instance)
