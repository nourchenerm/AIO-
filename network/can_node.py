import os
import sys
import logging
import can
from network.protocol import Protocol


class CAN(Protocol):
    def __init__(self, conf):
        super().__init__(conf)
        self.logger = logging.getLogger(__name__)
        self.channel = conf.get("channel", "can0")
        self.interface = conf.get("interface", "pcan")
        self.bitrate = conf.get("bitrate", 500000)

        self.bus = None
        self.notifier = None

        self.logger.info(f"Initialized with channel={self.channel}, interface={self.interface}, bitrate={self.bitrate}")

    def connect(self):
        if (sys.platform == 'linux'):
            os.system(f'sudo /sbin/ip link set {self.channel} up type can bitrate {self.bitrate}')
        try:
            self.bus = can.interface.Bus(
                channel=self.channel,
                interface=self.interface,
                bitrate=self.bitrate
            )
            self.logger.info(f"Connected to CAN bus on {self.channel} using {self.interface} @ {self.bitrate}bps")
        except Exception as e:
            self.logger.error(f"Failed to connect to CAN bus: {e}")
            raise

    def send(self, data: can.Message):
        if not self.bus:
            self.logger.warning("Attempted to send message while bus is not connected.")
            return

        try:
            self.bus.send(data)
            self.logger.info(f"Sent message: {data}")
        except can.CanError as e:
            self.logger.error(f"Failed to send CAN message: {e}")

    def receive(self):
        if not self.bus:
            self.logger.warning("Attempted to receive message while bus is not connected.")
            return None

        try:
            msg = self.bus.recv(timeout=1)
            if msg:
                self.logger.debug(f"Received message: {msg}")
            return msg
        except can.CanError as e:
            self.logger.error(f"Error while receiving CAN message: {e}")
            return None

    def disconnect(self):
        if self.notifier:
            self.notifier.stop()
            self.logger.info("Notifier stopped.")

        if self.bus:
            self.bus.shutdown()
            self.logger.info("CAN bus shutdown.")
            self.bus = None

    def add_listener(self, listener):
        if not self.bus:
            self.logger.warning("Cannot add listener. Bus is not connected.")
            return

        self.notifier = can.Notifier(self.bus, [listener])
        self.logger.info(f"Listener added: {listener.__class__.__name__}")
