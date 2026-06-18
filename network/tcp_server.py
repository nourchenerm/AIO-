import socket
import threading
import logging
import time
import sys
import json
from network.protocol import Protocol

class TCPServer(Protocol):
    DEFAULT_BUFF_SIZE = 2048

    def __init__(self, conf):
        super().__init__(conf)
        self.host = conf.get('host', '0.0.0.0')
        self.port = conf.get('port', 9000)
        self.buff_size = conf.get('buffer_size', TCPServer.DEFAULT_BUFF_SIZE)
        self.clients_to_send_to = conf.get('clients_to_send_to', [])  # <<<< NEW
        self._on_receive_callback = None
        self.logger = logging.getLogger(__name__)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # client_id -> socket
        self.addr_to_socket = {}  # (ip, port) -> socket
        self.stop_event = threading.Event()

        self.accept_thread = threading.Thread(target=self.accept_loop)
        self.accept_thread.start()

    def accept_loop(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.logger.info(f'TCPServer listening on {self.host}:{self.port}')
        except Exception as e:
            self.logger.critical(f'Failed to bind socket: {e}')
            sys.exit(1)

        while not self.stop_event.is_set():
            try:
                client_sock, client_addr = self.server_socket.accept()
                self.addr_to_socket[client_addr] = client_sock
                self.logger.info(f'Client connected from {client_addr}')

                thread = threading.Thread(target=self.receive_loop, args=(client_sock, client_addr))
                thread.start()
            except socket.error as e:
                self.logger.error(f'Accept failed: {e}')
                break
    def print_connected_clients(self):
        if not self.clients:
            print("No clients currently connected.")
        else:
            print("Connected clients:")
            for client_id in self.clients:
                print(f" - {client_id}")

    def receive_loop(self, client_sock, client_addr):
        client_id = None
        registered = False

        while not self.stop_event.is_set():
            try:
                received_data = client_sock.recv(self.buff_size)
                if not received_data:
                    raise ConnectionResetError(f"Client {client_addr} disconnected")
                received_data = received_data.decode().strip()
                self.logger.debug(f"Received data from {client_addr}: {received_data}")

                if not registered:
                    if received_data.startswith('{"REGISTER":'):
                        client_id = json.loads(received_data).get("REGISTER")
                        if client_id:
                            self.clients[client_id] = client_sock
                            self.logger.info(f'Client {client_addr} registered as {client_id}')
                            registered = True
                            # Send registration success response
                            client_sock.sendall("REGISTERED\n".encode('utf-8'))
                        else:
                            self.logger.warning(f"Invalid REGISTER message from {client_addr}")
                            client_sock.sendall("ERROR: Invalid registration".encode('utf-8'))
                            client_sock.close()
                            return
                    else:
                        self.logger.warning(f"First message from {client_addr} must be REGISTER")
                        client_sock.sendall("ERROR: Must send REGISTER first".encode('utf-8'))
                        client_sock.close()
                        return
                else:
                    self.on_receive(client_id, received_data)

            except Exception as e:
                self.logger.error(f"Error with client {client_addr}: {e}")
                break
            time.sleep(0.01)


        # Cleanup
        try:
            client_sock.close()
        except Exception:
            pass
        if client_id and client_id in self.clients:
            del self.clients[client_id]
        if client_addr in self.addr_to_socket:
            del self.addr_to_socket[client_addr]
        self.logger.info(f'Connection with {client_addr} closed')


    def send(self, client_id, data):
        if client_id not in self.clients:
            self.logger.warning(f"Client {client_id} not registered or disconnected")
            return

        sock = self.clients.get(client_id)
        if sock:
            try:
                sock.sendall(data.encode())
                self.logger.info(f'Sent to {client_id}: {data}')
            except socket.error as e:
                self.logger.error(f"Error sending to {client_id}: {e}")
        else:
            self.logger.warning(f"Socket for {client_id} not found")
    # inside __init__
    

    # method
    def set_on_receive_callback(self, callback):
        """Set a custom callback function to be called when a message is received."""
        self._on_receive_callback = callback

    # modified on_receive
    def on_receive(self, client_id, message):
        if self._on_receive_callback:
            self._on_receive_callback(client_id, message)
        else:
            self.logger.info(f'Received from {client_id}: {message}')


    def send_to_clients(self, data):
        """Send data to all clients listed in self.clients_to_send_to"""
        for client_id in self.clients_to_send_to:
            self.send(client_id, data)

    def disconnect(self):
        self.stop_event.set()
        for client_id, sock in list(self.clients.items()):
            try:
                sock.close()
            except Exception:
                pass
            self.logger.info(f'Disconnected client {client_id}')
        self.clients.clear()
        self.server_socket.close()
