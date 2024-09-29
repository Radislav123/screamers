import logging

from core.service.singleton import Singleton


class Settings(Singleton):
    def __init__(self):
        # Настройки логгера
        self.LOG_FORMAT = ("[%(asctime)s] - [%(levelname)s] - %(name)s"
                           " - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
        self.LOG_FOLDER = "logs"
        self.CONSOLE_LOG_LEVEL = logging.DEBUG
        self.FILE_LOG_LEVEL = logging.DEBUG
