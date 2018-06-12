import datetime
import os
import ssl
import jwt
import json
import random
import time
import paho.mqtt.client as mqtt


AT_LEAST_ONCE = 1
AT_MOST_ONCE = 0
MAXIMUM_BACKOFF_TIME = 32


def create_jwt(algorithm='RS256'):
    token = {
        'iat': datetime.datetime.utcnow(), # The time that the token was issued at
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60), # The time the token expires.
        'aud': os.environ['GCLOUD_PROJECT_ID'], # The audience field should always be set to the GCP project id.
    }
    # Read the private key file.
    with open(os.environ['PRIVATE_KEY_PATH'], 'r') as f:
        private_key = f.read()
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Queue():
    def __init__(self):
        self.should_backoff = False
        self.minimum_backoff_time = 1

    def publish_event(self, payload):
        self._publish(payload, 'events')

    def publish_state(self, payload):
        self._publish(payload, 'state')

    def _get_client(self):
        client = mqtt.Client(
            client_id=(
                'projects/{}/locations/{}/registries/{}/devices/{}'.format(
                    os.environ['GCLOUD_PROJECT_ID'],
                    os.environ['GCLOUD_REGION'],
                    os.environ['GCLOUD_REGISTRY_ID'],
                    os.environ['GCLOUD_DEVICE_ID']
                )
            )
        )
        client.username_pw_set(username='unused', password=create_jwt())
        client.tls_set(ca_certs=os.environ['CA_CERTS'], tls_version=ssl.PROTOCOL_TLSv1_2)
        client.on_connect = self.on_connect
        client.on_publish = self.on_publish
        client.on_disconnect = self.on_disconnect
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message
        client.connect(os.environ['GCLOUD_BRIDGE_HOSTNAME'], 8883)
        mqtt_config_topic = '/devices/{}/config'.format(os.environ['GCLOUD_DEVICE_ID'])
        client.subscribe(mqtt_config_topic, qos=AT_LEAST_ONCE)
        return client

    def _publish(self, payload, topic):
        client = self._get_client()
        jwt_iat = datetime.datetime.utcnow()
        jwt_exp_mins = 20

        client.loop()
        if self.should_backoff:
            # If backoff time is too large, give up.
            if self.minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maximum backoff time. Giving up.')
                return

            # Otherwise, wait and connect again.
            delay = self.minimum_backoff_time + random.randint(0, 1000) / 1000.0
            print('Waiting for {} before reconnecting.'.format(delay))
            time.sleep(delay)
            self.minimum_backoff_time *= 2
            client.connect(os.environ['GCLOUD_BRIDGE_HOSTNAME'], 8883)

        seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if seconds_since_issue > 60 * jwt_exp_mins:
            print('Refreshing token after {}s').format(seconds_since_issue)
            jwt_iat = datetime.datetime.utcnow()
            client = self._get_client()

        mqtt_topic = '/devices/{}/{}'.format(os.environ['GCLOUD_DEVICE_ID'], topic)
        client.publish(mqtt_topic, self._build_payload(payload), qos=AT_LEAST_ONCE)
        time.sleep(5)

        client.disconnect()

    def _build_payload(self, payload):
        return json.dumps(payload)

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('on_connect', mqtt.connack_string(rc))
        self.should_backoff = False
        self.minimum_backoff_time = 1

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.should_backoff = True

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = message.payload
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        # The config is passed in the payload of the message. In this example,
        # the server sends a serialized JSON string.
        data = json.loads(payload)
        print(data)
