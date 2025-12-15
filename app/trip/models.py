from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GistIndex
from django.db import models
from django.utils import timezone

from common.models import AuditableModel
from trip.enums import TripStatus, default_state


class ClientSubscribedTrip(AuditableModel):
    session_id = models.CharField(max_length=255)
    subscribed_to = ArrayField(models.CharField(max_length=255), default=default_state)


class Trip(AuditableModel):
    """
    A Trip represents a DRIVER-created route that RIDERS can join.
    """

    created_by = models.ForeignKey('user.User', on_delete=models.PROTECT, related_name='created_trips',
                                   null=True, blank=True,
                                   help_text='User who created the trip, nullable for this assessment')
    starting_location = gis_models.PointField(
        geography=True,
        help_text="Starting location (longitude, latitude)"
    )
    destination_location = gis_models.PointField(
        geography=True,
        help_text="Destination location (longitude, latitude)"
    )
    current_location = gis_models.PointField(
        geography=True,
        help_text="Destination location (longitude, latitude)",
        null=True, blank=True
    )

    route_geometry = models.TextField(
        help_text="Encoded polyline from Google Directions API",
        blank=True,
        null=True
    )
    route_geometry_decoded = gis_models.LineStringField(
        geography=True, help_text="Route geometry as a LineString"
    )

    available_seats = models.PositiveSmallIntegerField(help_text="Number of seats available for riders")

    is_ride_requests_allowed = models.BooleanField(
        default=False, help_text="Whether new riders can request to join this trip"
    )
    trip_status = models.CharField(choices=TripStatus.choices(), default=TripStatus.Initiated.value)

    date_added = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    distance = models.DecimalField(decimal_places=5, max_digits=20, default=0.0)
    duration = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            GistIndex(fields=["starting_location"]),
            GistIndex(fields=["destination_location"]),
            GistIndex(fields=["route_geometry_decoded"]),
        ]

    def __str__(self):
        return f"Trip {self.id}"


class TripSettingsConfig(AuditableModel):
    radius = models.DecimalField(
        decimal_places=5, max_digits=20, default=0.0,
        help_text="Route radius in meters"
    )
    speed = models.DecimalField(
        decimal_places=5, max_digits=20, default=0.0,
        help_text="Speed in km/h"
    )
    speed_mps = models.DecimalField(
        decimal_places=5, max_digits=20, default=0.0,
        help_text="Speed in meters per second"
    )
    is_active = models.BooleanField(default=False)


class TripLocationHistory(models.Model):
    trip = models.ForeignKey(
        "Trip", on_delete=models.CASCADE, related_name="location_history"
    )
    location = gis_models.PointField(
        geography=True,
        help_text="location (longitude, latitude)"
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Trip {self.trip_id} @ {self.timestamp}"
