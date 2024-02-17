"""Logging utils"""
import datetime
import logging
import os
import sys


def get_data_path():
    main_dir = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
    return os.path.join(os.path.dirname(main_dir), "data")


class NexusLogger(logging.Logger):
    """Logging class"""

    def __init__(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"nexus-{timestamp}.log"
        # data_path = get_data_path()

        super().__init__(file_name)
        formatter = logging.Formatter(
            "[%(asctime)s | %(levelname)s] <%(module)s.%(funcName)s> - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # if not os.path.exists(data_path):
        #     os.mkdir(data_path)

        # if not os.path.exists(os.path.join(data_path, "logs")):
        #     os.mkdir(os.path.join(data_path, "logs"))

        log_level = logging.DEBUG
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)


logger = NexusLogger()
