import time
import logging
import threading
from network.protocol import Protocol
from typing import Any, Callable


class MockClient(Protocol):
    DEFAULT_QOS = 2

    def __init__(self, conf):
        super().__init__(conf)
        # Example: __mqtt__MQTT[Thermal]
        self.generate_data = None
        self.is_simulator_set = False
        self.logger = logging.getLogger(f'{__name__}_{__class__.__name__}[{conf.get("function")}]')
        self.connect()
        self.thread = threading.Thread(target=self.receive_loop)
        self.stop_recv_event = threading.Event()
        self.thread.start()

    def connect(self):
        self.logger.debug('connected!')

    def disconnect(self):
        self.stop_recv_event.set()
        self.logger.debug('disconnected!')

    def receive_loop(self, delimiter=None, data_type=None):
        while not self.is_simulator_set: time.sleep(0.5)
        while not self.stop_recv_event.is_set():
            received_data = self.generate_data()
            if received_data:
                self.on_receive(received_data)
            else:
                self.logger.debug('Simulator not yet set...')
            time.sleep(0.01)

    def generate_data(self):
        return None

    def set_data_simulator(self, data_simulator_func):
        self.is_simulator_set = True
        self.generate_data = data_simulator_func

    def send(self, *data):
        self.logger.debug(f'send -> {data}')

    def subscribe(self):
        pass
    def set_on_receive_callback(self, callback: Callable):
        Protocol.set_on_receive_callback(self,callback)
