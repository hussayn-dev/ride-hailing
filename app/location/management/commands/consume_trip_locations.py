import asyncio
import json

from aiokafka import AIOKafkaConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Consume trip location updates from Kafka and broadcast via channels"

    def handle(self, *args, **kwargs):
        asyncio.run(self.consume())

    async def consume(self):
        consumer = AIOKafkaConsumer(
            'trip_location_updates',
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id="trip_location_group",
            auto_offset_reset="earliest"
        )
        await consumer.start()
        self.stdout.write(self.style.SUCCESS("Kafka consumer started"))
        channel_layer = get_channel_layer()

        try:
            async for msg in consumer:
                value = json.loads(msg.value)
                room_name = value.get('room_name')
                message = value.get('message')
                self.stdout.write(self.style.WARNING(f"Broadcast received: {message}"))
                # Send to channels group
                await channel_layer.group_send(
                    room_name,
                    {
                        "type": "trip.location.update",
                        "message": message
                    }
                )
        finally:
            await consumer.stop()
            self.stdout.write(self.style.WARNING("Kafka consumer stopped"))
