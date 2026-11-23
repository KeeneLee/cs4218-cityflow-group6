FROM python:3.11-slim

# Install the Kafka client and TLS certificates.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir confluent-kafka

WORKDIR /app
# Copy the script and the input trips.
COPY replayer.py /app/replayer.py
COPY input/trips.tsv /data/trips.tsv

USER 65532:65532
CMD ["python", "-u", "/app/replayer.py", "/data/trips.tsv"]
