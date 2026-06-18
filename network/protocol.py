from abc import ABC, abstractmethod
from typing import Any, Callable
import logging

class Protocol(ABC):

    def __init__(self, conf: dict):
        #TODO associate the function name to the logger !
        self.function     = conf.get('function')
        self.host         = conf.get('host')
        self.port         = conf.get('port')
        self.retry_s      = conf.get('retry_connection_s')
        self.__on_receive = lambda data: data  # Do nothing

    def connect(self, *args, **kwargs):
        pass

    @abstractmethod
    def send(self, data: Any):
        pass

    def on_receive(self, data: Any):
        self.__on_receive(data)

    def set_on_receive_callback(self, callback: Callable):
        if callback != None:
            self.on_receive = callback

    @abstractmethod
    def disconnect(self):
        pass
