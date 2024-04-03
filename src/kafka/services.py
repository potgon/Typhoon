import atexit
import os
import json
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from dataclasses import dataclass

from utils.singleton import Singleton
from utils.logger import make_log
from database.models import User
from database.models import Queue


@dataclass
class KafkaModelMessage:
    user_id: int
    asset_id: int
    model_type_id: int


class KafkaProducerSingleton(metaclass=Singleton):
    def __init__(self):
        if not hasattr(self, "producer_instance"):
            self.producer_instance = Producer(
                {"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVER")}
            )
            atexit.register(self.close_producer)

    def get_producer(self):
        return self.producer_instance

    def close_producer(self):
        if hasattr(self, "producer_instance"):
            self.producer_instance.flush()
            self.producer_instance.close()
            del self.producer_instance


def get_consumer():
    consumer = Consumer(
        {
            "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVER"),
            "group.id": os.getenv("KAFKA_GROUP_ID"),
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe(os.getenv("MODEL_QUEUE_TRAIN_TOPIC"))
    return consumer


async def consumer_loop():
    try:
        with get_consumer() as consumer:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        make_log(
                            "KAFKA_CONSUMER",
                            40,
                            "models_workflow.log",
                            f"Kafka consumer error: {msg.error()}",
                        )
                        break
                try:
                    data = KafkaModelMessage(**json.loads(msg.value().decode("utf-8")))
                    user_id = data.user_id
                    asset_id = data.asset_id
                    model_type_id = data.model_type_id
                except json.JSONDecodeError:
                    make_log(
                        "KAFKA_CONSUMER",
                        40,
                        "models_workflow.log",
                        "Error decoding JSON request data",
                    )
                    continue

                priority = await User.get(id=user_id).priority

                try:
                    await Queue.create(
                        user=user_id,
                        asset_id=asset_id,
                        model_type_id=model_type_id,
                        priority=priority,
                    )
                except Exception as e:
                    make_log(
                        "KAFKA_DB",
                        40,
                        "models_workflow.log",
                        f"Error creating Queue object: {str(e)}",
                    )
                    continue

                consumer.commit(msg)
        consumer.close()
    except (
        KafkaException
    ) as ke:  # Propagate this error to the caller whenever I implement it
        make_log(
            "KAFKA_CONSUMER",
            40,
            "models_workflow.log",
            f"Error getting Kafka consumer: {str(ke.args[0])}",
        )


async def producer_call(msg) -> tuple:
    try:
        topic = os.getenv("MODEL_QUEUE_TRAIN_TOPIC")
    except KafkaException as ke:
        make_log(
            "KAFKA_PRODUCER",
            40,
            "models_workflow.log",
            f"Error connecting to topic: {ke.args[0]}",
        )
        return (0, "Error sending train request")
    try:
        producer = KafkaProducerSingleton().get_producer()
    except (KafkaException, Exception) as ke:
        make_log(
            "KAFKA_PRODUCER",
            40,
            "models_workflow.log",
            f"Error getting Kafka producer: {ke.args[0] if isinstance(ke, KafkaException) else str(ke)}",
        )
        return (0, "Error sending train request")
    try:
        producer.produce(topic, msg.encode("utf-8"), callback=delivery_callback)
        producer.flush()
    except KafkaException as ke:
        make_log(
            "KAFKA_PRODUCER",
            40,
            "models_workflow.log",
            f"Error producing message to topic: {ke.args[0]}",
        )
        return (0, "Error sending train request")
    return (1, "Train request successfully sent")


def delivery_callback(err, msg):
    if err:
        make_log(
            "KAFKA_MODEL",
            40,
            "kafka_workflow.log",
            f"ERROR: Message delivery failed: {err}",
        )
    else:
        make_log(
            "KAFKA_MODEL",
            20,
            "kafka_workflow.log",
            f"Produced event to topic {msg.topic()}, key = {msg.key().decode('utf-8')}, value = {msg.value().decode('utf-8')}",
        )
