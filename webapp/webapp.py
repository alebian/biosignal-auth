from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
from orator import DatabaseManager, Model
import bcrypt

import config


db = DatabaseManager(config.DATABASES)
Model.set_connection_resolver(db)
app = Flask(__name__)
CORS(app)

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


class User(Model):
    __fillable__ = ['password_hash', 'email']


@app.route("/api/v1/register", methods=['POST'])
def register():
    try:
        new_user = User.create(
            email=request.get_json()['email'],
            password_hash=hash_password(request.get_json()['password'])
        )
        return jsonify(
            {'token': encode({'email': new_user.email, 'percentage': '0.0'})}
        ), 201
    except:
        return jsonify(
            {'error': 'Email already taken.'}
        ), 400


@app.route("/api/v1/login", methods=['POST'])
def login():
    try:
        user = User.where('email', request.get_json()['email']).first_or_fail()
        # TODO: Check signal
        if check_password(request.get_json()['password'], user.password_hash):
            return jsonify(
                { 'token': encode({ 'email': user.email, 'percentage': '0.0' }) }
            ), 200
    except:
        return jsonify({}), 401


if __name__ == "__main__":
    app.run(host='0.0.0.0')
