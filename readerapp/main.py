from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
import string
import random
import uuid
import threading

import emg_driver.settings as settings
from data_collection_manager import DataCollectionManager
from mqtt.mqtt import Mqtt

database = {
    'token': None,
    'signal': None,
    'interpreted_signal': None,
}

settings = {
    'window_size': settings.WINDOW_SIZE,
    'spike_threshold': settings.SPIKE_THRESHOLD,
    'zero_threshold': settings.ZERO_THRESHOLD,
    'zero_length': settings.ZERO_LENGTH,
}

app = Flask(__name__)
CORS(app)

q = Mqtt()
manager = DataCollectionManager(settings)

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
        if token != database['token']:
            return jsonify({}), 404
        return f(token, *args, **kwargs)
    return decorated_function

def create_signal(token):
    _nullify_database()
    values = []
    interpreted_values = []
    database['token'] = token
    database['signal'] = values
    database['interpreted_signal'] = interpreted_values
    manager.start_collection(values, interpreted_values, token)

def read_signal(token):
    return (database['signal'], database['interpreted_signal'])

def delete_signal(token):
    signals = _nullify_database()
    return signals

def _nullify_database():
    manager.stop_collection()
    previous_signal = database['signal']
    previous_interpreted_signal = database['interpreted_signal']

    database['token'] = None
    database['signal'] = None
    database['interpreted_signal'] = None

    return (previous_signal, previous_interpreted_signal)

###################################################################################################
#                                            ENDPOINTS                                            #
###################################################################################################
@app.route("/api/v1/start", methods=['POST'])
def start():
    new_token = random_uuid()
    create_signal(new_token)
    return jsonify(
        { 'signalUUID': new_token }
    ), 201


@app.route("/api/v1/stop", methods=['POST'])
@token_required
def stop(token):
    signals = delete_signal(token)

    if signals[1] is not None:
        q.publish_event({'uuid': token, 'signal': signals[1]})
        return jsonify({ 'signalUUID': token }), 200
    else:
        return jsonify({}), 404



@app.route("/api/v1/cancel", methods=['POST'])
@token_required
def cancel(token):
    delete_signal(token)
    return jsonify({}), 200


@app.route("/api/v1/read", methods=['GET'])
@token_required
def read(token):
    signals = read_signal(token)
    if signals[0] is not None:
        return jsonify({
            'signal': [[i, x] for i, x in enumerate(signals[0][-2000:])],
            'interpreted_signal': [[i, x] for i, x in enumerate(signals[1])]
        }), 200
    else:
        return jsonify({}), 404


@app.route("/api/v1/settings", methods=['GET'])
def get_settings():
    return jsonify(settings), 200


@app.route("/api/v1/settings", methods=['PUT'])
def change_settings():
    data = request.get_json()

    if data['window_size']:
        settings['window_size'] = data['window_size']
    if data['spike_threshold']:
        settings['spike_threshold'] = data['spike_threshold']
    if data['zero_threshold']:
        settings['zero_threshold'] = data['zero_threshold']
    if data['zero_length']:
        settings['zero_length'] = data['zero_length']

    return jsonify(settings), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
