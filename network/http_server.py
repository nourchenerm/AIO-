import threading
import logging
from flask import Flask
from network.protocol import Protocol


class HTTPServer(Protocol):
    def __init__(self, conf):
        super().__init__(conf)
        self.conf = conf
        self.host = conf.get('host', '0.0.0.0')
        self.port = conf.get('port', 8080)
        self.logger = logging.getLogger(__name__)
        self.app = Flask(__name__)
        self.thread = None
        self.instance = None  # Will be set when routes are registered

    def register_routes(self, register_fn):
        """Register external Flask routes."""
        # The register_fn expects (app, host) where host is the Class instance
        # We need to pass the Class instance, not the HTTPServer instance
        if self.instance is not None:
            register_fn(self.app, self.instance)
        else:
            # Store the register function to call later when Class is available
            self._pending_register_fn = register_fn

    def connect(self):
        def run_flask():
            self.logger.info(f"Starting HTTP server on {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

        self.thread = threading.Thread(target=run_flask, daemon=True)
        self.thread.start()

    def send(self, data):
        self.logger.warning("Send not implemented for HTTPServer. Use it only to receive requests.")

    def disconnect(self):
        self.logger.info("HTTPServer cannot be stopped gracefully via Flask default; skipping.")