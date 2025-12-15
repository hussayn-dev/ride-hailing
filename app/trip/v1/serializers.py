from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import serializers

from trip.enums import TripStatus
from trip.models import Trip
from trip.trip_match import TripRouteMatch
from trip.utils import compute_route_polyline


class AbstractTripSerializer(serializers.Serializer):
    @staticmethod
    def validate_location_parameters(longitude, latitude):
        if latitude is None or longitude is None:
            raise serializers.ValidationError("Both 'latitude' and 'longitude' are required.")

        if not (-90 <= latitude <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        if not (-180 <= longitude <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")

        return latitude, longitude

    def validate_location(self, longitude, latitude):
        self.validate_location_parameters(longitude=longitude, latitude=latitude)
        return Point(longitude, latitude, srid=4326)


class CreateTripSerializer(serializers.ModelSerializer, AbstractTripSerializer):
    starting_latitude = serializers.FloatField(write_only=True, required=True)
    starting_longitude = serializers.FloatField(write_only=True, required=True)
    destination_latitude = serializers.FloatField(write_only=True, required=True)
    destination_longitude = serializers.FloatField(write_only=True, required=True)

    class Meta:
        model = Trip
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "route_geometry",
                            "current_location", "route_geometry_decoded", "trip_status",
                            "date_added", "date_last_updated", "distance", "duration",
                            "starting_location", "destination_location", "created_by"
                            )

    def validate(self, attrs):
        starting_longitude = attrs.pop("starting_longitude")
        starting_latitude = attrs.pop("starting_latitude")
        destination_latitude = attrs.pop("destination_latitude")
        destination_longitude = attrs.pop("destination_longitude")
        attrs['starting_location'] = self.validate_location(
            starting_longitude, starting_latitude
        )
        attrs['destination_location'] = self.validate_location(
            destination_longitude, destination_latitude
        )

        route_response = compute_route_polyline(
            origin_longitude=starting_longitude,
            origin_latitude=starting_latitude,
            destination_longitude=destination_longitude,
            destination_latitude=destination_latitude,
        )

        if not route_response.get("success", False):
            raise serializers.ValidationError(route_response['message'])

        attrs["route_geometry_decoded"] = route_response["route_geometry_decoded"]
        attrs["route_geometry"] = route_response["polyline"]
        attrs["distance"] = route_response["distance_m"]
        attrs["duration"] = route_response["duration_s"]

        return attrs


class UpdateTripSerializer(serializers.ModelSerializer, AbstractTripSerializer):
    starting_latitude = serializers.FloatField(required=False)
    starting_longitude = serializers.FloatField(required=False)
    destination_latitude = serializers.FloatField(required=False)
    destination_longitude = serializers.FloatField(required=False)

    class Meta:
        model = Trip
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "route_geometry",
                            "current_location", "route_geometry_decoded", "trip_status",
                            "date_added", "date_last_updated", "distance", "duration",
                            "starting_location", "destination_location", "created_by"
                            )

    def validate(self, attrs):
        instance = self.instance
        coordinates_changed = any(
            field in attrs
            for field in [
                "starting_latitude",
                "starting_longitude",
                "destination_latitude",
                "destination_longitude",
            ]
        )

        if coordinates_changed:
            starting_latitude = attrs.pop("starting_latitude", instance.starting_location.y)
            starting_longitude = attrs.pop("starting_longitude", instance.starting_location.x)
            destination_latitude = attrs.pop("destination_latitude", instance.destination_location.y)
            destination_longitude = attrs.pop("destination_longitude", instance.destination_location.x)

            attrs['starting_location'] = self.validate_location(starting_longitude, starting_latitude)
            attrs['destination_location'] = self.validate_location(destination_longitude, destination_latitude)

            route_response = compute_route_polyline(
                destination_longitude=destination_longitude,
                destination_latitude=destination_latitude,
                origin_longitude=starting_longitude,
                origin_latitude=starting_latitude,
            )

            if not route_response.get("success", False):
                raise serializers.ValidationError(route_response['message'])

            attrs["route_geometry_decoded"] = route_response["route_geometry_decoded"]
            attrs["route_geometry"] = route_response["polyline"]
            attrs["distance"] = route_response["distance_m"]
            attrs["duration"] = route_response["duration_s"]

        return attrs


class GetTripsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'


class TripRouteMatchSerializer(serializers.ModelSerializer):
    pickup_dist = serializers.FloatField(read_only=True)
    drop_off_dist = serializers.FloatField(read_only=True)
    route_distance = serializers.FloatField(read_only=True)
    eta_minutes = serializers.FloatField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id',
            'created_by',
            'starting_location',
            'destination_location',
            'route_geometry',
            'available_seats',
            'is_ride_requests_allowed',
            'date_added',
            'date_last_updated',
            'distance',
            'duration',
            'pickup_dist',
            'drop_off_dist',
            'route_distance',
            'eta_minutes',
        ]
        read_only_fields = fields


class TripMatchResponseSerializer(serializers.Serializer):
    """Serializer for trip match response."""
    trip_id = serializers.CharField(source='id')
    pickup_latitude = serializers.FloatField(source='starting_location.y')
    pickup_longitude = serializers.FloatField(source='starting_location.x')
    dropoff_latitude = serializers.FloatField(source='destination_location.y')
    dropoff_longitude = serializers.FloatField(source='destination_location.x')
    pickup_distance_meters = serializers.FloatField()
    drop_off_distance_meters = serializers.FloatField()
    rider_trip_distance_meters = serializers.FloatField()
    available_seats = serializers.IntegerField()
    eta_minutes = serializers.FloatField()


class MatchingTripsSerializer(AbstractTripSerializer):
    starting_latitude = serializers.FloatField(write_only=True, required=True)
    starting_longitude = serializers.FloatField(write_only=True, required=True)
    destination_latitude = serializers.FloatField(write_only=True, required=True)
    destination_longitude = serializers.FloatField(write_only=True, required=True)
    number_of_seats = serializers.IntegerField(write_only=True, required=True)
    intersection_radius_meters = serializers.IntegerField(
        write_only=True,
        required=False,
        default=500,
        min_value=1
    )

    def validate(self, attrs):
        attrs['starting_location'] = self.validate_location(
            attrs['starting_longitude'], attrs['starting_latitude']
        )
        attrs['destination_location'] = self.validate_location(
            attrs['destination_longitude'], attrs['destination_latitude']
        )
        return attrs

    def get_matching_trips(self):
        qs = Trip.objects.filter(
            trip_status__in=[TripStatus.Ongoing.value, TripStatus.Initiated.value],
            date_added__date=timezone.now().date()
        )
        service = TripRouteMatch(
            pickup_point=self.validated_data['starting_location'],
            drop_off_point=self.validated_data['destination_location'],
            seats=self.validated_data['number_of_seats'],
            radius=int(self.validated_data['intersection_radius_meters']),
        )
        return service.match(qs)
