from flask import Flask, jsonify, request
from flask_cors import CORS
import string
import random


database = {}
app = Flask(__name__)
CORS(app)


def random_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


@app.route("/api/v1/start", methods=['POST'])
def start():
    try:
        token = random_generator()
        database[token] = {
            'signal': []
        }
        # TODO: Start reading from device
        return jsonify(
            { 'signalToken': token }
        ), 201
    except:
        return jsonify({}), 500


@app.route("/api/v1/stop", methods=['POST'])
def stop():
    try:
        token = request.get_json()['signalToken']
        if token in database.keys():
            # TODO: Send signal and token to other server
            del database[token]
            return jsonify({}), 200
        else:
            return jsonify({}), 400
    except:
        return jsonify({}), 500


@app.route("/api/v1/cancel", methods=['POST'])
def cancel():
    try:
        token = request.get_json()['signalToken']
        if token in database.keys():
            # TODO: Stop reading and don't send info to other server
            del database[token]
            return jsonify({}), 200
        else:
            return jsonify({}), 400
    except:
        return jsonify({}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
