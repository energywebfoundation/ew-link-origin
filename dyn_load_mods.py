import importlib
import json

from core.abstract.input import ExternalDataSource
from core.output.energyweb import Origin


def get_class_instances(submodule: str) -> list:
    class_instances = []
    for entry in misty_firefly['modules'][submodule]:
        for module_name in entry:
            module_path = 'core.' + submodule + '.' + module_name
            for class_name in entry[module_name]:
                module = importlib.import_module(module_path)
                class_obj = getattr(module, class_name)
                class_kwargs = misty_firefly[class_name]
                class_instance = class_obj(**class_kwargs)
                class_instances.append(class_instance)
    return class_instances


if __name__ == '__main__':

    modules = []
    misty_firefly = json.load(open('misty-firefly.json'))
    modules.extend(get_class_instances('input'))
    modules.extend(get_class_instances('output'))

    for module in modules:
        if isinstance(module, ExternalDataSource):
            pass
        if isinstance(module, Origin):
            pass
        if isinstance(module, ExternalDataSource):
            pass
