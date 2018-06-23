#!/bin/bash

/app/cloud_sql_proxy -dir=/cloudsql -instances=proyecto-final-itba:us-central1:biosignal-auth -credential_file=/app/key.json &
gunicorn -b :$PORT main:app
