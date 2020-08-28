FROM python:3.8-alpine

RUN mkdir -p /scoresaber
COPY requirements.txt /scoresaber
WORKDIR /scoresaber

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev && \
  pip3 install --no-cache-dir -r requirements.txt && \
  apk del .build-deps

COPY app /scoresaber

CMD ["python3", "scoresaber.py"]
