import logging
from typing import Optional

from django.conf import settings

from integrations.base import BaseClient
from integrations.location.dataclass import GoogleRouteRequest

logger = logging.getLogger(__name__)


class GoogleRoutesService(BaseClient):
    DEFAULT_TIMEOUT = 30

    def __init__(self, timeout: Optional[int] = None):
        super().__init__()
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.base_url = settings.GOOGLE_MAPS_ROUTE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline'
        }

        if not self.api_key:
            raise Exception("Google Maps API key is missing")

    def compute_route(self, data: GoogleRouteRequest):
        """
        Calls the Google Routes API to get route info between origin and destination
        """
        payload = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": data.origin_latitude,
                        "longitude": data.origin_longitude
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": data.destination_latitude,
                        "longitude": data.destination_longitude
                    }
                }
            },
            "travelMode": "DRIVE"
        }

        logger.info(
            f"Requesting route from {data.origin_latitude},"
            f"{data.origin_longitude} to {data.destination_latitude},"
            f"{data.destination_longitude},")
        response, status_code = self._make_request("POST", f"{self.base_url}:computeRoutes", payload)
        return response, status_code
