import pika
import json
import os


class PikaClient:
    def __init__(self):
        credentials = pika.PlainCredentials(
            os.environ["RABBITMQ_USER"], os.environ["RABBITMQ_PASS"]
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                os.environ["RABBITMQ_HOST"],
                os.environ["RABBITMQ_PORT"],
                "/",
                credentials,
            )
        )
        self.channel = self.connection.channel()
        self.response = None

    def send_message(self, message: dict):
        """Method to publish message to RabbitMQ"""
        self.channel.basic_publish(
            exchange="orders",
            routing_key="created_order",
            body=json.dumps(message),
        )
