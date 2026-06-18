


class ProtocolFactory:
    @staticmethod
    def create_instance(conf: dict):
        _type = conf.pop('type')
        if _type == 'mqtt':
            from network.mqtt import MQTT
            return MQTT(conf)
        elif _type == 'tcp_client':
            from network.tcp_client import TCPClient
            return TCPClient(conf)
        elif _type == 'tcp_server':
            from network.tcp_server import TCPServer
            return TCPServer(conf)
        elif _type == 'udp':
            from network.udp import UDP
            return UDP(conf)
        elif _type == 'http_server':
            from network.http_server import HTTPServer
            return HTTPServer(conf)
        elif _type == 'can':
            from network.can_node import CAN
            return CAN(conf)
        elif _type == 'websocket_server':
            from network.websocket_server import WebSocketServer# CHANGED from 'async_ws_server'
            return WebSocketServer(conf)
        elif _type == 'async_ws_server':
            raise NotImplementedError(f'Add implementation for {_type}')
        elif _type == 'mock':
            from network.mock_client import MockClient
        elif _type == 'mcp':
            # Nouveau protocole MCP
            return MCPProtocol(config)
        elif _type == 'baby_lin':
            from network.baby_lin_handler import BabyLIN_Handler
            return BabyLIN_Handler(conf)

        else:
            raise NotImplementedError(f'Add implementation for {_type} Protocol')
