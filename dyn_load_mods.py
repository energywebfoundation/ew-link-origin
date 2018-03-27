"""
    Json must have the key 'modules' plus the specific kw for class init on the root. Every module should hold a list
    of files and classes to load.
    i.e.:
    {
      "modules": {
        "input": [
          { "carbonemission": ["Wattime"] },
          { "engiepower": ["Eget"] },
        ]
      },
      "Wattime": {
        "usr": "foo",
        "pwd": "barbaz",
        "ba": "National Grid"
      }
    }
"""
import importlib
import json
import datetime

from core.abstract.input import EnergyDataSource, CarbonEmissionDataSource
from core.output.energyweb import LocalClientOriginProducer


def convert_time(epoch: int):
    access_time = datetime.datetime.fromtimestamp(epoch)
    return access_time.strftime("%Y-%m-%d  %H:%M:%S")


def get_class_instances(config_json: dict, submodule: str) -> list:
    """
    Reflection algorithm to dynamically load python modules referenced on the configuration json.
    :param config_json: Configuration dict. Json must have the key 'modules' plus the specific kw for class init \
    on the root. Every module should hold a list of files and classes to load.
    :param submodule: Name of any submodule of the core library. i.e.: "input" i.e.: "input.special"
    :return: List of core library class instances.
    """
    class_instances = []
    for entry in config_json['modules'][submodule]:
        for module_name in entry:
            module_path = 'core.' + submodule + '.' + module_name
            for class_name in entry[module_name]:
                module = importlib.import_module(module_path)
                class_obj = getattr(module, class_name)
                class_kwargs = config_json[class_name]
                class_instance = class_obj(**class_kwargs)
                class_instances.append(class_instance)
    return class_instances


if __name__ == '__main__':

    modules = []
    misty_firefly = json.load(open('misty-firefly.json'))

    # WARN: The sequence of input first is important to keep the following for loop working.
    modules.extend(get_class_instances(misty_firefly, 'input'))
    modules.extend(get_class_instances(misty_firefly, 'output'))

    print('`•.,,.•´¯¯`•.,,.•´¯¯`•.,, Config ,,.•´¯¯`•.,,.•´¯¯`•.,,.•´\n')
    for module in modules:
        if isinstance(module, CarbonEmissionDataSource):
            print('Carbon Emission: ' + module.__class__.__name__)
            carbon_emission = module.read_state()
        elif isinstance(module, EnergyDataSource):
            print('Energy: ' + module.__class__.__name__)
            energy = module.read_state()
        elif isinstance(module, LocalClientOriginProducer):
            print('Smart Contract: ' + module.__class__.__name__)
            # TODO: Multiple energy and carbon measurements capabilities.
            # TODO: Add Meter down and api down capabilities.
            # TODO: File hashing and loading capabilities.
            produced_energy = {
                'energy': energy.accumulated_power,
                'is_meter_down': False,
                'previous_hash': 'null',
                'co2_saved': carbon_emission.accumulated_co2,
                'is_co2_down': False
            }
            smart_contract = module.mint(**produced_energy)

    # asd
    print('\n\n¸.•*´¨`*•.¸¸.•*´¨`*•.¸ Results ¸.•*´¨`*•.¸¸.•*´¨`*•.¸\n')
    print('Carbon Emission:')
    print(convert_time(carbon_emission.measurement_epoch))
    print(carbon_emission.accumulated_co2)
    print('----------')
    print('Energy:')
    print(convert_time(energy.measurement_epoch))
    print(energy.accumulated_power)
    print('----------')
    print('B.N.: ' + str(smart_contract['blockNumber']))
    print('-------------------\n')
