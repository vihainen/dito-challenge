FROM python:3.7-alpine3.8

RUN mkdir /app

#Copy required file
ADD docker-entrypoint.sh /app
ADD restapp.py /app
ADD model.py /app
ADD requirements.txt /app

WORKDIR /app

RUN dos2unix docker-entrypoint.sh && \
    dos2unix restapp.py && \
    apk update && \
    python -m pip install --upgrade pip && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev postgresql-libs && \
    pip install -r requirements.txt && \
    rm requirements.txt && \
    apk del build-base && \
    rm -rf /var/cache/apk/*

VOLUME [ "/data" ]

EXPOSE 5000
WORKDIR /app

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
