from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
from orator import DatabaseManager, Model
import bcrypt
import os
import json
import requests

import config

db = DatabaseManager(config.DATABASES)
Model.set_connection_resolver(db)
app = Flask(__name__)
CORS(app)

###################################################################################################
#                                             HELPERS                                             #
###################################################################################################
def encode(payload):
  return jwt.encode(payload, config.SECRET_KEY_BASE, algorithm='HS256')

def decode(token):
    return jwt.decode(token.split(' ')[1], config.SECRET_KEY_BASE, algorithm=['HS256'])

def hash_password(password):
    return bcrypt.hashpw(
        bytes(password, 'utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def check_password(password, hash):
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hash.encode('utf-8')
    )

###################################################################################################
#                                             MODELS                                              #
###################################################################################################
class User(Model):
    __fillable__ = ['password_hash', 'email', 'signal_uuid']

###################################################################################################
#                                            ENDPOINTS                                            #
###################################################################################################
@app.route("/api/v1/devices", methods=['GET'])
def devices():
    r = requests.get(
        '{}/api/v1/devices'.format(os.environ['BAD_API_HOST']),
        headers={
            'Authorization': os.environ['ACCESS_KEY'],
            'Content-Type': 'application/json'
        }
    )
    return r.text, r.status_code

@app.route("/api/v1/signal/<uuid>", methods=['GET'])
def signal(uuid):
    r = requests.get(
        '{}/api/v1/signals/{}'.format(os.environ['BAD_API_HOST'], uuid),
        headers={
            'Authorization': os.environ['ACCESS_KEY'],
            'Content-Type': 'application/json'
        }
    )
    return r.text, r.status_code

@app.route("/api/v1/register", methods=['POST'])
def register():
    data = request.get_json()
    r = requests.get(
        '{}/api/v1/signals/{}'.format(os.environ['BAD_API_HOST'], data['signal_token']),
        headers={
            'Authorization': os.environ['ACCESS_KEY'],
            'Content-Type': 'application/json'
        }
    )
    if r.status_code != 204:
        return jsonify({'error': 'Hubo un problema con la señal'}), r.status_code

    new_user = User.create(
        email=data['email'],
        password_hash=hash_password(data['password']),
        signal_uuid=data['signal_token']
    )
    return jsonify(
        {'token': encode({'email': new_user.email})}
    ), 201


@app.route("/api/v1/login", methods=['POST'])
def login():
    data = request.get_json()
    user = User.where('email', data.get('email')).first_or_fail()

    if not check_password(data.get('password'), user.password_hash):
        return '', 401

    r = requests.post(
        '{}/api/v1/signals/compare'.format(os.environ['BAD_API_HOST']),
        headers={
            'Authorization': os.environ['ACCESS_KEY'],
            'Content-Type': 'application/json'
        },
        json={
            'signal_1_uuid': user.signal_uuid,
            'signal_2_uuid': data.get('signal_token')
        }
    )

    if r.status_code != 200:
        return jsonify({'error': 'Hubo un problema con las señales'}), r.status_code

    percentage = json.loads(r.text)['percentage']
    if percentage >= 0.8:
        return jsonify(
            {
                'token': encode({ 'email': user.email }),
                'percentage': percentage,
                'message': 'Logueado satisfactoriamente!'
            }
        ), 200
    else:
        return jsonify(
            {
                'percentage': percentage,
                'message': 'Fallo la comparación de la señal.'
            }
        ), 401


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
