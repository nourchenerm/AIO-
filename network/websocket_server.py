import asyncio
import threading
import websockets
import logging
from network.protocol import Protocol


class WebSocketServer(Protocol):
    def __init__(self, conf):
        super().__init__(conf)  # host, port, retry_s set here
        self.logger = logging.getLogger(__name__)
        self._on_receive_callback = None
        self.connected_clients = set()
        self.server = None
        self._loop = None
        self._thread = None

        # Optional: use retry_s in reconnect logic if you implement it

    async def _handler(self, websocket, path):
        self.connected_clients.add(websocket)
        self.logger.info(f"Client connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                #self.logger.info(f"Received message: {message}")
                self.on_receive(message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {websocket.remote_address}")
        finally:
            self.connected_clients.remove(websocket)

    async def _start_server(self):
        self.server = await websockets.serve(self._handler, self.host, self.port)
        self.logger.info(f"WebSocketServer started on {self.host}:{self.port}")
        await self.server.wait_closed()

    def start(self):
        # Run the async server in a new event loop on a separate thread
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._start_server())

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def send(self, data):
        async def _broadcast():
            for client in self.connected_clients:
                try:
                    await client.send(data)
                except Exception as e:
                    self.logger.error(f"Failed to send to client: {e}")

        if self._loop:
            asyncio.run_coroutine_threadsafe(_broadcast(), self._loop)
        else:
            self.logger.warning("Cannot send data, event loop not started yet.")

    def disconnect(self):
        if self.server and self._loop:
            self.logger.info("Stopping WebSocketServer...")
            self.server.close()
            future = asyncio.run_coroutine_threadsafe(self.server.wait_closed(), self._loop)
            future.result()  # block until closed
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()

    def set_on_receive_callback(self, callback):
        self._on_receive_callback = callback

    def on_receive(self, data):
        if self._on_receive_callback:
            self._on_receive_callback(data)
        else:
            self.logger.info(f"Received: {data}")
