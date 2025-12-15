import json
import logging
from typing import Awaitable
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from common.kafka_producer import KafkaProducerService

logger = logging.getLogger(__name__)
CACHE_TIMEOUT = 60 * 60  # 1 hour


class TripLocationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time trip location tracking.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_trips = None
        self.session_id = None
        self.subscribed_trips = set()

    async def connect(self):
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)

        self.session_id = params.get("session_id", [None])[0]

        if not self.session_id:
            await self.close(code=4001)
            return
        # TODO validate session id in cache
        self.client_trips = await self.get_client_trips(self.session_id)

        cache_key = f"client_subscribed_{self.session_id}"
        subscribed = self.client_trips.subscribed_to or []
        cache.set(cache_key, subscribed, CACHE_TIMEOUT)

        self.subscribed_trips = set(subscribed)
        await self.accept()
        logger.info(
            f"WebSocket connected {self.channel_name} "
            f"session={self.session_id} trips={self.subscribed_trips}"
        )

    async def disconnect(self, code):
        """
        On disconnect:
        - Remove socket from channel groups
        - Do NOT touch DB or cache
        """
        for trip_id in self.subscribed_trips:
            await self.channel_layer.group_discard(
                f"trip_{trip_id}",
                self.channel_name
            )

        self.subscribed_trips = set()

        logger.info(
            f"WebSocket disconnected {self.channel_name} "
            f"session={self.session_id}" f"trips={self.subscribed_trips}"
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            msg_type = data.get("type")
            payload = data.get("data", {})

            match msg_type:
                case "PUBLISH_LOCATION":
                    await self.handle_publish_location(payload)

                case "SUBSCRIBE_TO_TRIP_LOCATION":
                    await self.handle_subscribe(payload)

                case "UNSUBSCRIBE_FROM_TRIP_LOCATION":
                    await self.handle_unsubscribe(payload)

                case _:
                    await self.send_error(f"Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")

        except Exception as e:
            logger.exception("WebSocket error")
            await self.send_error(str(e))

    async def handle_subscribe(self, payload):
        trip_id = payload.get("trip_id")
        if not trip_id:
            await self.send_error("trip_id is required")
            return

        trip = await self.get_trip(trip_id)
        if not trip:
            await self.send_error(f"Trip {trip_id} not found")
            return

        if trip_id in self.subscribed_trips:
            await self.send_error("Already subscribed to this trip")
            return

        await self.channel_layer.group_add(
            f"trip_{trip_id}",
            self.channel_name
        )

        self.subscribed_trips.add(trip_id)
        trip = await self.add_trip_to_subscribed_trips(trip_id)
        if not trip:
            await self.send_error(f"Trip id {trip_id} does not exist")
            return

        await self.send(json.dumps({
            "type": "SUBSCRIPTION_CONFIRMED",
            "data": {"trip_id": trip_id}
        }))

    async def handle_unsubscribe(self, payload):
        trip_id = payload.get("trip_id")
        if not trip_id:
            await self.send_error("trip_id is required")
            return

        trip = await self.get_trip(trip_id)
        if not trip:
            await self.send_error(f"Trip {trip_id} not found")
            return
        if trip_id not in self.subscribed_trips:
            await self.send_error("Not subscribed to this trip")
            return

        await self.channel_layer.group_discard(
            f"trip_{trip_id}",
            self.channel_name
        )

        self.subscribed_trips.remove(trip_id)
        await self.remove_trip_from_subscribed_trips(trip_id)

        await self.send(json.dumps({
            "type": "UNSUBSCRIPTION_CONFIRMED",
            "data": {"trip_id": trip_id}
        }))

    async def handle_publish_location(self, payload):
        trip_id = payload.get("trip_id")
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        timestamp = payload.get("timestamp") or timezone.now().isoformat()

        if not all([trip_id, latitude, longitude]):
            await self.send_error("trip_id, latitude and longitude are required")
            return

        if not self.validate_coordinates(latitude, longitude):
            await self.send_error("Invalid coordinates")
            return

        trip = await self.get_trip(trip_id)
        if not trip:
            await self.send_error(f"Trip {trip_id} not found")
            return

        await self.update_trip_current_location(
            trip_id=trip_id,
            longitude=float(longitude),
            latitude=float(latitude),
            timestamp=timestamp
        )

        location_data = {
            "trip_id": trip_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "timestamp": timestamp,
        }

        await self.broadcast_location_update(trip_id, location_data)

        await self.send(json.dumps({
            "type": "LOCATION_PUBLISHED",
            "status": "success",
            "data": location_data
        }))

    @database_sync_to_async
    def get_client_trips(self, session_id):
        from trip.models import ClientSubscribedTrip
        client_trip, _ = ClientSubscribedTrip.objects.get_or_create(session_id=session_id)
        print(client_trip.subscribed_to)
        return client_trip

    @database_sync_to_async
    def add_trip_to_subscribed_trips(self, trip_id) -> Awaitable[None]:
        if trip_id not in self.client_trips.subscribed_to:
            self.client_trips.subscribed_to.append(trip_id)
            self.client_trips.save()

        cache.set(
            f"client_subscribed_{self.session_id}",
            self.client_trips.subscribed_to,
            CACHE_TIMEOUT
        )
        return self.client_trips

    @database_sync_to_async
    def update_trip_current_location(self, trip_id, longitude, latitude, timestamp) -> Awaitable[None]:
        from trip.models import Trip
        self.save_location_history(trip_id, longitude, latitude, timestamp)
        with transaction.atomic():
            Trip.objects.filter(id=trip_id).update(
                current_location=Point(longitude, latitude)
            )
        return trip_id

    @database_sync_to_async
    def get_trip(self, trip_id):
        from trip.models import Trip
        return Trip.objects.filter(id=trip_id).only("id").first()

    @database_sync_to_async
    def remove_trip_from_subscribed_trips(self, trip_id) -> Awaitable[None]:
        if trip_id in self.client_trips.subscribed_to:
            self.client_trips.subscribed_to.remove(trip_id)
            self.client_trips.save()

        cache.set(
            f"client_subscribed_{self.session_id}",
            self.client_trips.subscribed_to,
            CACHE_TIMEOUT
        )
        return self.client_trips

    @database_sync_to_async
    def save_location_history(self, trip_id, longitude, latitude, timestamp):
        from trip.models import TripLocationHistory
        return TripLocationHistory.objects.create(
            trip_id=trip_id,
            location=Point(longitude, latitude),
            timestamp=timestamp,
        )

    async def send_error(self, message):
        await self.send(json.dumps({
            "type": "ERROR",
            "message": message
        }))

    @staticmethod
    def validate_coordinates(latitude, longitude) -> bool:
        try:
            lat = float(latitude)
            lon = float(longitude)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (TypeError, ValueError):
            return False

    async def broadcast_location_update(self, trip_id, location_data):
        room_name = f"trip_{trip_id}"
        message = {
            "type": "trip.location.update",
            "message": location_data,
        }

        await self.send_location_update({
            'room_name': room_name,
            'message': message
        })

    @staticmethod
    async def send_location_update(message: dict):
        producer_service = KafkaProducerService(topic="trip_location_updates")
        await producer_service.send(message)
