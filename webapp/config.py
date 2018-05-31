import os

DATABASES = {
    'postgres': {
        'driver': 'postgres',
        'host': os.environ['POSTGRES_HOST'],
        'database': os.environ['POSTGRES_DB'],
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'prefix': ''
    }
}

SECRET_KEY_BASE = os.environ['SECRET_KEY_BASE']
