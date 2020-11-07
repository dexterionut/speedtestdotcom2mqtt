FROM python:3.8-alpine

ENV INSTALL_PATH /app
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

# Installing build dependencies
RUN apk update \
    && apk add --virtual .build-deps \
    python-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN apk del .build-deps

CMD ["python", "app.py"]