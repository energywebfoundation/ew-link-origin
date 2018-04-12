import logging
import colorlog
import datetime

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(message)s'))

# Default color scheme is 'example'
tty_logger = colorlog.getLogger('example')
tty_logger.addHandler(handler)
tty_logger.setLevel(logging.ERROR)


file_logger = logging.getLogger('spam_application')
file_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('./bond.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
file_logger.addHandler(fh)


class AsyncClientError(EnvironmentError):
    pass


class NoCompilerError(NotImplementedError):
    pass


class AllGasUsedWarning(Warning):
    pass


def convert_time(epoch: int):
    access_time = datetime.datetime.fromtimestamp(epoch)
    return access_time.strftime("%Y-%m-%d  %H:%M:%S")
