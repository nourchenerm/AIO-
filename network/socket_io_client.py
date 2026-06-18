import sys
import time
import logging
import socketio

from network.protocol import Protocol


class Socket_IO_Client(Protocol):

    # TODO check : DEBUG:urllib3.connectionpool:Resetting dropped connection
    def __init__(self, conf):
        super().__init__(conf)
        self.client_socket_io = socketio.Client()
        self.__check_sio_last_time = 0
        self.__sio_need_to_connect = True
        self.logger = logging.getLogger(__name__)
        self.retry_s = conf.get('retry_connection_s')
        self.connect()
        self.client_socket_io.on('connect', self.on_connect)
        self.client_socket_io.on('disconnect', self.on_disconnect)
        self.client_socket_io.on('values', self.on_receive)

    def on_connect(self):
        self.logger.debug("Connected to the Socket IO server on http://{self.host}:{self.port}")

    # Define the disconnect event handler
    def on_disconnect(self):
        # TODO to be improved to check if disconnection is triggered by server ...
        self.client_socket_io.connected = False
        self.logger.debug(f"Unexpected Disconnection from the Socket IO server on http://{self.host}:{self.port}")
        self._on_disconnect_clbk()

    def connect(self):
        while self.__sio_need_to_connect:
            if time.time() > self.__check_sio_last_time + self.retry_s:
                self.__check_sio_last_time = time.time()
                if self.host and self.port:
                    try:
                        self.client_socket_io.connect(f"http://{self.host}:{self.port}")
                        self.__sio_need_to_connect = not self.client_socket_io.connected  # False if already connected
                        self.logger.debug(f'connected = {self.client_socket_io.connected}')
                        self.logger.debug(f'self.__sio_need_to_connect = {self.__sio_need_to_connect}')
                        time.sleep(.1)
                    except Exception as e:
                        self.logger.warning(
                            f'Failed to connect to Socket IO Server, retrying in {self.retry_s} second...')
                        self.logger.error(e)
                        self.logger.debug(f'connected = {self.client_socket_io.connected}')
                        self.__sio_need_to_connect = True
                else:
                    self.logger.error(f'({self.host}, {self.port}) is not a valid socket, exiting...')
                    self.__sio_need_to_connect = False
                    sys.exit(1)

    def disconnect(self):
        self.client_socket_io.disconnect()


    def on_receive(self, message):
        print(f'received {message}')

    def send(self, *data):
        if data:
            value = data[0]
            try:
                self.client_socket_io.emit('message', value)
            except Exception as e:
                self.logger.error(f"Error: Failed to send data, reason : {e}")

    def _on_disconnect_clbk(self):
        self.logger.critical('Unexpected disconnection. Reconnecting...')
        #self.client_socket_io.disconnect()
        #self.client_socket_io = socketio.Client()
        self.connect()


if __name__ == "__main__":
    conf = {
        "host": "192.168.1.200",
        "port": 6799,
        "retry_connection_s": 1
    }

    logging.basicConfig(level=logging.DEBUG)
    client = Socket_IO_Client(conf)
    is_loop = True

    while True:
        try:
            time.sleep(1)
            # cmd = input('>>')
            # if cmd == 'd':
            #     client.disconnect()
        except KeyboardInterrupt as e:
            #client.disconnect()
            sys.exit(0)
            break
        finally:
            print('finally..')

