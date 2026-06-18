import sys
import time
import socket
import logging
import paho.mqtt.client as mqtt

from network.protocol import Protocol


class MQTT(Protocol):

    DEFAULT_QOS = 2

    def __init__(self, conf):
        super().__init__(conf)
        self.mqttc                      = None
        # TODO change
        self.sub_topics                 = conf.get('sub_topics') or {}
        print(self.sub_topics)
        self.__mqtt_client_id           = f'{socket.gethostname()}:{self.function}'
        self.__check_mqtt_last_time     = 0
        self.__mqtt_need_to_connect     = True
        # Example: __mqtt__MQTT[Thermal]
        self.logger = logging.getLogger(f'{__name__}{__class__.__name__}[{conf.get("function")}]')

        self.init_mqtt()
        self.connect()
        #self.subscribe()

    def connect(self):
        while self.__mqtt_need_to_connect:

            if time.time() > self.__check_mqtt_last_time + self.retry_s:
                self.__check_mqtt_last_time = time.time()
                if self.host and self.port:
                    try:
                        self.mqttc.connect(self.host, self.port)
                        self.__mqtt_need_to_connect = False
                        self.mqttc.loop_start()
                        self.subscribe()
                        self.logger.info('Subscribing')
                        time.sleep(.1)
                    except Exception:
                        self.logger.warning(f'Failed to connect to MQTT broker, retrying in {self.retry_s} second...')
                    else:
                        self.logger.info('Successfully connected to MQTT Broker')

                else:
                    self.logger.error(f'({self.host}, {self.port}) is not a valid socket, exiting...')
                    self.__mqtt_need_to_connect = False
                    sys.exit(1)

    def subscribe(self):
        """ Subscribe to all topics from config file"""
        for topic in self.sub_topics.values():
            self.mqttc.subscribe(topic, MQTT.DEFAULT_QOS)
            print("subscribed to : ", topic)

    def disconnect(self):
        self.mqttc.disconnect()
        time.sleep(0.5)

    def on_receive(self, message):
        self.logger.debug(f'New MQTT message: {message.topic} => {str(message.payload.decode(errors="ignore"))}')

    def send(self, *data):
        topic, value, qos, retain = data
        res = self.mqttc.publish(topic, value, qos, retain)
        if res.rc != mqtt.MQTT_ERR_SUCCESS:
            if res.rc == mqtt.MQTT_ERR_NO_CONN:
                self.logger.error('Failed to send message, TCP connection is closed! error code:(4 = MQTT_ERR_NO_CONN)')
            else:
                self.logger.error(f'Failed to send message, Error code: {res.rc}')

    def init_mqtt(self):
        
        def on_connect_local_callback(client, userdata, flags, rc):
            if rc != 0:
                userdata.logger.error(f"Connection failed (rc={rc})")
                return

            userdata.logger.info("Connected to MQTT broker")

            # Re-subscribe to all topics
            for topic in userdata.sub_topics.values():
                client.subscribe(topic, MQTT.DEFAULT_QOS)


        def on_disconnect_local_callback(client, userdata, rc):
            if rc != 0:
                self.logger.critical('Unexpected disconnection. Reconnecting...')
                userdata.__mqtt_need_to_connect = True
                self.connect()
                self.logger.info('Connection is back!')
          

            else:
                userdata.disconnect()

        def on_message_local_callback(client, userdata, message):
            userdata.on_receive(message)
        
        self.mqttc = mqtt.Client(client_id=self.__mqtt_client_id, userdata=self,clean_session=False)
        self.mqttc.on_connect = on_connect_local_callback
        self.mqttc.on_disconnect = on_disconnect_local_callback
        self.mqttc.on_message = on_message_local_callback