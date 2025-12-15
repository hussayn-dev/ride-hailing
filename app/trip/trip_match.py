from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.db.models.functions import Distance, Length
from django.db.models import F, ExpressionWrapper, FloatField, Func
from django.db.models import Value

from trip.models import TripSettingsConfig
from trip.utils import get_active_trip_settings


class LineLocatePoint(Func):
    function = "ST_LineLocatePoint"
    output_field = FloatField()


class TripRouteMatch:
    """Service for matching trips based on pickup/drop-off location and seats."""

    def __init__(self, pickup_point, drop_off_point, seats=1, radius=500):
        self.pickup = pickup_point
        self.drop_off = drop_off_point
        self.seats = seats
        self.radius = radius

    def match(self, trips):
        config: TripSettingsConfig = get_active_trip_settings()
        speed_mps = config.speed_mps or float((config.speed or 30) * 1000 / 3600)

        qs = trips.filter(
            is_ride_requests_allowed=True,
            available_seats__gte=self.seats,
            route_geometry_decoded__isnull=False,
        )

        qs = qs.annotate(
            pickup_distance_meters=ExpressionWrapper(
                Distance("route_geometry_decoded", self.pickup, geography=True),
                output_field=FloatField(),
            ),
            drop_off_distance_meters=ExpressionWrapper(
                Distance("route_geometry_decoded", self.drop_off, geography=True),
                output_field=FloatField(),
            ),
            #
            pickup_fraction=LineLocatePoint(
                F("route_geometry_decoded"),
                Value(self.pickup, output_field=GeometryField())
            ),
            drop_off_fraction=LineLocatePoint(
                F("route_geometry_decoded"),
                Value(self.drop_off, output_field=GeometryField())
            ),
            route_length_meters=Length("route_geometry_decoded")
        ).filter(
            pickup_distance_meters__lte=self.radius,
            drop_off_distance_meters__lte=self.radius,
            drop_off_fraction__gt=F("pickup_fraction"),
        ).annotate(
            rider_trip_distance_meters=ExpressionWrapper(
                (F("drop_off_fraction") - F("pickup_fraction")) * F("route_length_meters"),
                output_field=FloatField(),
            ),
            eta_minutes=ExpressionWrapper(
                (F("pickup_fraction") * F("route_length_meters")) / speed_mps, output_field=FloatField()
            ),
        )

        return qs
