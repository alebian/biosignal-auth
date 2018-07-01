FROM gcr.io/google-appengine/python

RUN virtualenv /env

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /app/cloud_sql_proxy
RUN chmod +x /app/cloud_sql_proxy
RUN mkdir /cloudsql; chmod 777 /cloudsql

ADD . /app

WORKDIR /app

EXPOSE 8080

CMD /app/run_app.sh
