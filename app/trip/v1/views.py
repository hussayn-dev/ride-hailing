from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from trip.filters import TripFilter
from trip.models import Trip
from trip.v1.serializers import (
    GetTripsSerializer,
    CreateTripSerializer,
    UpdateTripSerializer,
    MatchingTripsSerializer,
    TripRouteMatchSerializer, TripMatchResponseSerializer,
)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = GetTripsSerializer
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TripFilter
    ordering_fields = ["created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateTripSerializer
        if self.action in ["update", "partial_update"]:
            return UpdateTripSerializer
        return super().get_serializer_class()

    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter("starting_longitude", description="Starting Longitude", required=True, type=float),
            OpenApiParameter("starting_latitude", description="Starting Latitude", required=True, type=float),
            OpenApiParameter("destination_latitude", description="Destination Latitude", required=True, type=float),
            OpenApiParameter("destination_longitude", description="Destination Longitude", required=True, type=float),
            OpenApiParameter("number_of_seats", description="Number of seats", required=True, type=int),
            OpenApiParameter("intersection_radius_meters", description="Intersection radius in meters", required=False,
                             type=int, default=500),
        ],
        methods=["GET"],
    )
    @action(
        detail=False,
        methods=["GET"],
        serializer_class=TripMatchResponseSerializer,
        url_path=r"matches",
        permission_classes=[AllowAny],
    )
    def list_matching_route_trips(self, request, pk=None):
        serializer = MatchingTripsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        matched_qs = serializer.get_matching_trips()
        page = self.paginate_queryset(matched_qs)
        if page is not None:
            serializer = TripMatchResponseSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data)
            response_data.data['total_matches'] = matched_qs.count()
            return response_data

        serializer = TripMatchResponseSerializer(matched_qs, many=True)
        return Response({
            'results': serializer.data,
            'total_matches': matched_qs.count()
        })
