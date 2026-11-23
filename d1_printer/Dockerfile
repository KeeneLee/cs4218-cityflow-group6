FROM python:3.11-slim

# Install the Kafka client and TLS certificates.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir confluent-kafka

WORKDIR /app
COPY d1_printer.py /app/d1_printer.py
USER 65532:65532
CMD ["python", "-u", "/app/d1_printer.py"]
