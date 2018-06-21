## Installation

```bash
pip install -r requirements.txt
```

Then you need to create the database with name biosignal-auth

## Migrating DB

```bash
orator migrate
```

## Docker

To run the webapp using docker you can:

```bash
docker build .
docker run -e POSTGRES_DB=biosignal-auth \
           -e POSTGRES_USER=biosignal-auth \
           -e POSTGRES_PASSWORD=biosignal-auth \
           -e SECRET_KEY_BASE=f187418a8f99847aa66912dfb87f9c865fdb5a628475a507393c2fed4d810593fd127cbd293a23088c9144e15dc9742ba17e158963f41b0b8fde7a73926d42b9 \
           -p 5000:5000 \
           biosignal-auth:latest
```

or

```bash
docker-compose up
```
