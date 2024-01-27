FROM python:3.12-alpine

LABEL name="Nexus" \
      maintainer="Nexus Team" \
      description="On Demand Cache Real-Debrid Indexer" \
      url="https://github.com/Pukabyte/Nexus"

WORKDIR /app
COPY . /app

RUN apk add --update \
    gcc \
    musl-dev \
    libc-dev \
    libxslt-dev \
    libxml2-dev \
    python3-dev \
    curl \
    bash \
    tzdata \
    && pip3 install --upgrade pip \
    && rm -rf /var/cache/apk/*

RUN python3 -m venv /venv && \
    source /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN chmod +x ./entrypoint.sh

EXPOSE 8978
ARG RD_KEY
ENV RD_KEY=$RD_KEY

ENTRYPOINT ["/app/entrypoint.sh"]
