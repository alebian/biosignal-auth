from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
import string
import random
import uuid
import threading

from data_collection_manager import DataCollectionManager
from mqtt.mqtt import Mqtt

database = {}
app = Flask(__name__)
CORS(app)

q = Mqtt()
manager = DataCollectionManager()

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
#                                            ENDPOINTS                                            #
###################################################################################################
@app.route("/api/v1/start", methods=['POST'])
def start():
    # if manager was not stopped cancel collection
    old_token = manager.stop_collection()
    if old_token is not None:
        del database[old_token]

    new_token = random_uuid()
    values = []
    interpreted_values = []
    database[new_token] = {
        'signal': values,
        'interpreted_signal': interpreted_values
    }

    manager.start_collection(values, interpreted_values, new_token)

    return jsonify(
        { 'signalUUID': new_token }
    ), 201


@app.route("/api/v1/stop", methods=['POST'])
@token_required
def stop(token):
    try:
        manager.stop_collection()
        signal = database[token]['interpreted_signal']
        del database[token]

        q.publish_event({'uuid': token, 'signal': signal})
        return jsonify({ 'signalUUID': token }), 200
    except:
        return jsonify({}), 500


@app.route("/api/v1/cancel", methods=['POST'])
@token_required
def cancel(token):
    try:
        manager.stop_collection()
        del database[token]
        return jsonify({}), 200
    except:
        return jsonify({}), 500


@app.route("/api/v1/read", methods=['GET'])
@token_required
def read(token):
    values = database[token]['signal']
    interpreted_values = database[token]['interpreted_signal']
    return jsonify({
        'signal': [[i, x] for i, x in enumerate(values[-2000:])],
        'interpreted_signal': [[i, x] for i, x in enumerate(interpreted_values)]
    }), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
