from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
import string
import random

from emg_driver.emg_shield import EMGShieldController
from emg_driver.data_collection import DataCollectionThread

database = {}
app = Flask(__name__)
CORS(app)


def random_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def get_token_from_request(request):
    return request.args.get('signalToken') or request.get_json(force=True).get('signalToken')

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request(request)
        if token not in database.keys():
            return jsonify({}), 404
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/v1/start", methods=['POST'])
def start():
    token = random_generator()

    controller = EMGShieldController()
    values = []
    thread = DataCollectionThread(controller, values)
    database[token] = {
        'signal': values,
        'thread': thread
    }
    thread.start()

    return jsonify(
        { 'signalToken': token }
    ), 201


@app.route("/api/v1/stop", methods=['POST'])
@token_required
def stop():
    try:
        token = get_token_from_request(request)
        database[token]['thread'].stop()
        # Sleep?
        signal = database[token]['signal']
        database[token]['signal'] = []
        del database[token]
        return jsonify({ 'signal': signal }), 200
    except:
        return jsonify({}), 500


@app.route("/api/v1/cancel", methods=['POST'])
@token_required
def cancel():
    try:
        token = get_token_from_request(request)
        database[token]['thread'].stop()
        del database[token]
        return jsonify({}), 200
    except:
        return jsonify({}), 500


@app.route("/api/v1/read", methods=['GET'])
@token_required
def read():
    try:
        token = get_token_from_request(request)
        values = database[token]['signal']
        return jsonify([[i, x] for i, x in enumerate(values)]), 200
    except:
        return jsonify({}), 500


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=80)
    app.run(host='127.0.0.1', port=5001)
