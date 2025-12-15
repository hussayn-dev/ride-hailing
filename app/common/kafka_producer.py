import json
import logging

from aiokafka import AIOKafkaProducer
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaProducerService:
    def __init__(self, topic: str):
        self.topic = topic
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER_URL
        )
        self.started = False

    async def start(self):
        if not self.started:
            await self.producer.start()
            self.started = True

    async def stop(self):
        if self.started:
            await self.producer.stop()
            self.started = False

    async def send(self, message: dict):
        await self.start()
        try:
            await self.producer.send_and_wait(
                self.topic,
                json.dumps(message).encode("utf-8")
            )
            logger.info(f"Message sent to Kafka topic {self.topic}")
        except Exception as e:
            logger.exception(f"Failed to send message to Kafka: {e}")
