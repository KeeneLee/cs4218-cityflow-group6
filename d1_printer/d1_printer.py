import os

from confluent_kafka import Consumer

# connect to OCI Streaming
consumer = Consumer({
    "bootstrap.servers": os.environ["BOOTSTRAP"],
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": os.environ["KAFKA_USER"],
    "sasl.password": os.environ["KAFKA_PASS"],
    "ssl.ca.location": "/etc/ssl/certs/ca-certificates.crt",
    "group.id": os.environ["KAFKA_GROUP"],
    "auto.offset.reset": "earliest",
})
consumer.subscribe([os.environ["TOPIC"]])

# print five trips
printed = 0
while printed < 5:
    message = consumer.poll(1.0)
    if message is None:
        continue

    recepit = message.value().decode("utf-8")
    print(recepit)
    printed += 1

consumer.close()
