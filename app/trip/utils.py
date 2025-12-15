import polyline
from django.contrib.gis.geos import LineString
from django.core.cache import cache

from integrations.location.dataclass import GoogleRouteRequest
from integrations.location.google import GoogleRoutesService
from trip.models import TripSettingsConfig


def convert_polyline_to_linestring(encoded_polyline: str) -> LineString:
    """
    Converts Google encoded polyline to GeoDjango LineString
    """
    coordinates = polyline.decode(encoded_polyline)
    return LineString([(lng, lat) for lat, lng in coordinates], srid=4326)


def get_active_trip_settings() -> TripSettingsConfig:
    settings_obj = cache.get('active_trip_settings')
    if not settings_obj:
        settings_obj = TripSettingsConfig.objects.filter(is_active=True).first()
        if settings_obj:
            cache.set('active_trip_settings', settings_obj, timeout=None)
    return settings_obj


def compute_route_polyline(
        origin_longitude: float,
        origin_latitude: float,
        destination_longitude: float,
        destination_latitude: float,
) -> dict:
    """Compute route using Google Routes API and return polyline, LineString, distance, and duration."""
    service = GoogleRoutesService()
    print("service")
    payload = GoogleRouteRequest(
        origin_longitude=origin_longitude,
        origin_latitude=origin_latitude,
        destination_longitude=destination_longitude,
        destination_latitude=destination_latitude,
    )
    response, status_code = service.compute_route(payload)
    if not response or str(status_code) != "200":
        return {"success": False, "message": "Unable to compute route"}

    routes = response.get("routes", [])
    if not routes:
        return {"success": False, "message": "No route found for the given coordinates"}

    route = routes[0]
    encoded_poly = route.get("polyline", {}).get("encodedPolyline")
    if not encoded_poly:
        return {"success": False, "message": "Something went wrong while creating the trip"}

    return {
        "success": True,
        "message": "Route computed successfully",
        "distance_m": route.get("distanceMeters"),
        "duration_s": route.get("duration"),
        "polyline": encoded_poly,
        "route_geometry_decoded": convert_polyline_to_linestring(encoded_poly),
    }
