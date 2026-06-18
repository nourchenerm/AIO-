import sys
import threading
import time
import socket
import logging
import json

from network.protocol import Protocol

class TCPClient(Protocol):
    DEFAULT_BUFF_SIZE = 2048

    def __init__(self, conf):
        super().__init__(conf)
        self.conf = conf
        self.buff_size = conf.get('buffer_size', TCPClient.DEFAULT_BUFF_SIZE)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__check_tcp_last_time = 0
        self.__tcp_need_to_connect = True
        self.logger = logging.getLogger(__name__)
        self.stop_recv_event = threading.Event()
        self.thread = None
        self._connected_event = threading.Event()  # 🔑 Event to signal connected state
        self.connect()

    def connect(self):
        while self.__tcp_need_to_connect and not self.stop_recv_event.is_set():
            if time.time() > self.__check_tcp_last_time + self.retry_s:
                self.__check_tcp_last_time = time.time()

                try:
                    self.client_socket.connect((self.host, self.port))
                    self.__tcp_need_to_connect = False
                    self._connected_event.set()

                    client_id = self.conf.get('client_id', 'default_client')
                    registration_message = json.dumps({"REGISTER": client_id})
                    self.client_socket.sendall(registration_message.encode())
                    self.logger.info(f"Sent registration as {client_id}")

                    # 🚫 NO BLOCKING RECV HERE

                    self.stop_recv_event.clear()
                    self.thread = threading.Thread(
                        target=self.receive_loop,
                        daemon=True
                    )
                    self.thread.start()

                    self.logger.info("Successfully connected to TCP Server")

                except ConnectionRefusedError:
                    self.logger.error(
                        f"Connection refused by server ({self.host}:{self.port})"
                    )
                except Exception as e:
                    self.logger.error(f"TCP connect error: {e}")

                time.sleep(self.retry_s)


    def wait_until_connected(self, timeout=None):
        """Block until the socket is connected."""
        return self._connected_event.wait(timeout)

    def receive_loop(self, delimiter=None, data_type=None):
        try:
            self.client_socket.recv(self.DEFAULT_BUFF_SIZE)  # clear any residual data
        except Exception:
            pass

        while not self.stop_recv_event.is_set():
            try:
                received_data = self.client_socket.recv(self.buff_size)
                if not received_data:
                    raise ConnectionResetError("Connection closed by server")
                received_data = received_data.decode()
                self.on_receive(received_data)
            except ConnectionResetError:
                self.logger.critical('Connection lost. Attempting to reconnect...')
                self._on_disconnect_clbk()
                break
            except socket.error as e:
                self.logger.error(f"Socket error: {e}")
                break
            time.sleep(0.01)

    def disconnect(self):
        self.stop_recv_event.set()
        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        self.client_socket.close()
        self._connected_event.clear()  # 🔑 Mark disconnected

    def on_receive(self, message):
        self.logger.info(f'Received: {message}')

    def send(self, *data):
        if data:
            value = data[0]
            if not self._connected_event.is_set():
                self.logger.warning("Attempted to send data before TCP connection was ready")
                return
            try:
                self.client_socket.sendall(value.encode())
            except socket.error as e:
                self.logger.error(f"Error: Failed to send data, reason: {e}")

    def _on_disconnect_clbk(self):
        self.logger.critical('Unexpected disconnection. Reconnecting...')
        try:
            self.client_socket.close()
        except Exception:
            pass
        self._connected_event.clear()  # 🔑 Mark disconnected
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_need_to_connect = True
        self.connect()
