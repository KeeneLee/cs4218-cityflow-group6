import json
import os
import sys
import time

from confluent_kafka import Producer

# define a helper method to read file
def load_trips(filename):
    # each line starts with the pickup zone, followed by a tab and the trip JSON
    records = []
    with open(filename, encoding="utf-8") as source:
        for line in source:
            key, value = line.rstrip("\n").split("\t", 1)
            records.append((key, json.loads(value)))
    return records

# Get the topic
topic = os.environ["TOPIC"]

records = load_trips(sys.argv[1])

# connect to OCI Streaming
producer = Producer({
    "bootstrap.servers": os.environ["BOOTSTRAP"],
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": os.environ["KAFKA_USER"],
    "sasl.password": os.environ["KAFKA_PASS"],
    "ssl.ca.location": "/etc/ssl/certs/ca-certificates.crt",
    "message.timeout.ms": 25000,
    "acks": "all",
})

# send trips
for uparea, recepit in records:
    # record send time
    recepit["sent_at"] = time.time()
    producer.produce(topic, key=uparea, value=json.dumps(recepit))

producer.flush(30)
