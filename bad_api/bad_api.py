from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
from threading import Lock
import sys
import os
import json
import time

from orator import DatabaseManager, Model
from orator.orm import belongs_to, has_many

from google.cloud import pubsub
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery

import config

db = DatabaseManager(config.DATABASES)
Model.set_connection_resolver(db)
app = Flask(__name__)
CORS(app)

###################################################################################################
#                                             HELPERS                                             #
###################################################################################################
#def encode(payload):
#  return jwt.encode(payload, 'asdasdasdasdasdasdasdasdasdasdas', algorithm='HS256')

#def decode(token):
#    return jwt.decode(token.split(' ')[1], 'asdasdasdasdasdasdasdasdasdasdas', algorithm=['HS256'])

###################################################################################################
#                                             MODELS                                              #
###################################################################################################
class Client(Model):
    __table__ = 'clients'
    __fillable__ = ['name', 'access_token']

    @has_many
    def devices(self):
      return Device

class Device(Model):
    __table__ = 'devices'
    __fillable__ = ['external_id']

    @belongs_to
    def client(self):
        return Client

class Signal(Model):
    __table__ = 'signals'
    __fillable__ = ['external_uuid', 'signal']

    @belongs_to
    def device(self):
        return Device

    @has_many
    def signals(self):
      return Signal

###################################################################################################
#                                             THREADS                                             #
###################################################################################################
class MQTTListener(threading.Thread):
    def __init__(self):
        super(MQTTListener, self).__init__()
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.environ['JSON_KEY_FILE'], ['https://www.googleapis.com/auth/cloud-platform']
        )

        if not self.credentials:
            sys.exit('Could not load service account credential')

    def run(self):
        """The main loop. Consumes messages from the Pub/Sub subscription."""
        subscriber = pubsub.SubscriberClient()
        subscription_path = subscriber.subscription_path(os.environ['GCLOUD_PROJECT_ID'], 'signal')

        def callback(message):
            """Logic executed when a message is received from subscribed topic."""
            try:
                device_id = message.attributes['deviceId']
                data = json.loads(message.data)
                signal = data['signal']
                uuid = data['uuid']

                try:
                  device = Device.where('external_id', device_id).first_or_fail()
                  db.table('signals').insert({
                      'external_uuid': uuid,
                      'signal': json.dumps(signal),
                      'device_id': device.id
                  })
                except ModelNotFound as e:
                  print('Device with id {} not found', device_id)

            except ValueError as e:
                print('Loading Payload ({}) threw an Exception: {}.'.format(message.data, e))
                message.ack()
                return

            message.ack()

        print('Listening for messages on {}'.format(subscription_path))
        subscriber.subscribe(subscription_path, callback=callback)

        # The subscriber is non-blocking, so keep the main thread from
        # exiting to allow it to process messages in the background.
        while True:
            time.sleep(60)

thread = MQTTListener()
thread.start()

###################################################################################################
#                                            ENDPOINTS                                            #
###################################################################################################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
    # app.run(host='0.0.0.0', port=80)
