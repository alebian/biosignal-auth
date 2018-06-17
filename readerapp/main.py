from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
import string
import random
import uuid
import time
import socket
import threading

from emg_driver.emg_shield import EMGShieldController
from emg_driver.data_collection import DataCollectionThread
from mqtt.mqtt import Mqtt

database = {}
app = Flask(__name__)
CORS(app)

q = Mqtt()

###################################################################################################
#                                             HELPERS                                             #
###################################################################################################
def random_uuid():
    return str(uuid.uuid4())

def get_uuid_from_request(request):
    return request.args.get('signalUUID') or request.get_json(force=True).get('signalUUID')

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_uuid_from_request(request)
        if token not in database.keys():
            return jsonify({}), 404
        return f(token, *args, **kwargs)
    return decorated_function

###################################################################################################
#                                             THREADS                                             #
###################################################################################################
class MQTTStatusReporter(threading.Thread):
    def __init__(self):
        super(MQTTStatusReporter, self).__init__()

    def run(self):
        """Every minute send the current IP of the device."""
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            q.publish_state({'IP': s.getsockname()[0]})
            s.close()
            time.sleep(60)

thread = MQTTStatusReporter()
thread.start()

###################################################################################################
#                                            ENDPOINTS                                            #
###################################################################################################
@app.route("/api/v1/start", methods=['POST'])
def start():
    token = random_uuid()

    controller = EMGShieldController()
    values = []
    thread = DataCollectionThread(controller, values)
    database[token] = {
        'signal': values,
        'thread': thread
    }
    thread.start()

    return jsonify(
        { 'signalUUID': token }
    ), 201


@app.route("/api/v1/stop", methods=['POST'])
@token_required
def stop(token):
    try:
        database[token]['thread'].stop()
        # Sleep?
        signal = database[token]['signal']
        database[token]['signal'] = []
        del database[token]

        q.publish_event({'uuid': token, 'signal': signal})
        return jsonify({ 'signalUUID': token }), 200
    except:
        return jsonify({}), 500


@app.route("/api/v1/cancel", methods=['POST'])
@token_required
def cancel(token):
    try:
        database[token]['thread'].stop()
        del database[token]
        return jsonify({}), 200
    except:
        return jsonify({}), 500


@app.route("/api/v1/read", methods=['GET'])
@token_required
def read(token):
    try:
        values = database[token]['signal']
        return jsonify([[i, x] for i, x in enumerate(values)]), 200
    except:
        return jsonify({}), 500


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=80)
    app.run(host='127.0.0.1', port=5001)
