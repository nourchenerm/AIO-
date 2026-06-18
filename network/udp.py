import threading
import socket
import logging
import time
import sys
from network.protocol import Protocol


class UDP(Protocol):
    DEFAULT_BUFF_SIZE = 10240

    def __init__(self, conf):
        super().__init__(conf)
        self.logger = logging.getLogger(__name__)
        self.__check_udp_last_time = 0
        self.__udp_need_to_bind = True
        self.is_running = True
        self._address = (self.host, self.port)
        self.tx_port = conf.get('tx_port',1111)
        self.buff_size = conf.get('buffer_size', UDP.DEFAULT_BUFF_SIZE)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.is_broadcast = conf.get('broadcast', False)
        self.encoding = conf.get('encoding', 'utf-8')
        self.broadcast_ip = conf.get('tx_ip', '255.255.255.255')  # fallback
        self.__init_udp()
        self.stop_recv_event = threading.Event()
        self.thread = threading.Thread(target=self.do_loop)
        self.thread.start()

    def __init_udp(self):
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.is_broadcast:
            self.udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def do_loop(self):
        while self.is_running:
            if self.__udp_need_to_bind:
                self.__bind_udp()
            else:
                self.receive_loop()
            time.sleep(0.01)
        print('exit loop...')

    def __bind_udp(self):
        while self.__udp_need_to_bind:
            if time.time() > self.__check_udp_last_time + self.retry_s:
                self.__check_udp_last_time = time.time()
                if self.host and self.port:
                    try:
                        self.client_socket.bind((self.host, self.port))
                        pass
                        self.__udp_need_to_bind = False
                        time.sleep(.1)
                    except Exception as e:
                        self.logger.warning(f'Failed to connect to UDP Socket, retrying in {self.retry_s} second...')
                        print(e)
                    else:
                        self.logger.info('Successfully connected to UDP Socket')
                else:
                    self.logger.error(f'({self.host}, {self.port}) is not a valid socket, exiting...')
                    self.__udp_need_to_bind = False
                    sys.exit(1)

    def receive_loop(self):
        print('enter receive loop')
        while not self.stop_recv_event.is_set():
            try:
                received_data, _ = self.client_socket.recvfrom(self.buff_size)  # Receive from server
                if received_data:
                    self.on_receive(received_data.decode(self.encoding))
            except Exception as e:
                self.logger.error(f"Error receiving data: {e}")

    def disconnect(self):
        self.is_running = False
        self.stop_recv_event.set()
        self.client_socket.close()

    def on_receive(self, message):
        print(message)
        self.logger.info(f'received {message}')

    def send(self, *data):
        if data:
            value = data[0]
            try:
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.client_socket.sendto(value.encode(), (self.broadcast_ip, self.tx_port))
            except socket.error as e:
                self.logger.error(f"Error sending data: {e}")


    def _on_disconnect_clbk(self):
        self.logger.critical('Unexpected disconnection. Reconnecting...')
        self.__udp_need_to_bind = True
        self.connect()


if __name__ == "__main__":
    conf = {
        'type': 'udp_client',
        'host': '127.0.0.1',
        'port': 1230,
        'retry_connection_s': 1,
        'encoding': 'utf-8',
        'broadcast': True,
        'buffer_size': 10240
    }
    udp_socket = UDP(conf)
    # udp_socket.logger.info = print
    try:
        while True:
            time.sleep(0.1)  # Simulate some work
    except KeyboardInterrupt:
        udp_socket.disconnect()
