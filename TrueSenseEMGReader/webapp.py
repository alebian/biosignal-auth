from flask import Flask, jsonify, request
import jwt
from orator import DatabaseManager, Model
import bcrypt

SECRET = 'f187418a8f99847aa66912dfb87f9c865fdb5a628475a507393c2fed4d810593fd127cbd293a23088c9144e15dc9742ba17e158963f41b0b8fde7a73926d42b9'

DATABASE_CONFIG = {
    'postgres': {
        'driver': 'postgres',
        'host': 'localhost',
        'database': 'biosignal-auth',
        'user': 'biosignal-auth',
        'password': 'biosignal-auth',
        'prefix': ''
    }
}

db = DatabaseManager(DATABASE_CONFIG)
Model.set_connection_resolver(db)
app = Flask(__name__)


def encode(payload):
  return jwt.encode(payload, SECRET, algorithm='HS256')

def decode(token):
    return jwt.decode(token.split(' ')[1], SECRET, algorithm=['HS256'])

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
    app.run()