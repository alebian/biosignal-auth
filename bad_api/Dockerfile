FROM python:3.6.5-alpine3.7

WORKDIR /app

COPY requirements.txt ./

RUN apk update && \
    apk add postgresql-libs && \
    apk add libffi-dev && \
    apk add linux-headers && \
    apk add alpine-sdk && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
