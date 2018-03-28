import pickle
import sys
import time
import threading
from pathlib import Path

import os
import colorlog
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

# Default color scheme is 'example'
tty_logger = colorlog.getLogger('example')
tty_logger.addHandler(handler)
tty_logger.setLevel(logging.ERROR)


file_logger = logging.getLogger('spam_application')
file_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/bond.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
file_logger.addHandler(fh)


def save(file_name: str, data: str):
    with open(file_name, 'w+') as file:
        file.write(data)


class Memory:

    def __init__(self, file_name_with_path: str):
        # home_path = str(Path.home().joinpath(program_name))
        # self.file = home_path + '/memory.pkl'
        # if not os.path.exists(home_path):
        #     os.makedirs(home_path)
        self.file = file_name_with_path
        if not os.path.exists(self.file):
            self.memory = {}
        else:
            self.memory = pickle.load(open(self.file, 'rb'))

    def save_memory(self, data: dict):
        self.memory.update(data)
        pickle.dump(data, open(self.file, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)


class AsyncClientError(EnvironmentError):
    pass


class NoCompilerError(NotImplementedError):
    pass


class AllGasUsedWarning(Warning):
    pass
