FROM python:3.6.5-alpine3.7

RUN apk --update add \
    postgresql-libs \
    libffi-dev \
    gcc \
    musl-dev \
    postgresql-dev \
    alpine-sdk \
    linux-headers

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
