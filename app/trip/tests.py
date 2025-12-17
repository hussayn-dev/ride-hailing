from unittest.mock import patch

from django.contrib.gis.geos import Point, LineString
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from trip.models import Trip


class TripViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.encoded_polyline = (
            "shyf@q_sSf@S\\xATnA?HGR_ATIhCYtAKVmClCq@x@{@p@}@b@oC`AkDfBk@`@"
            "fDvDb@l@rAtAr@j@nCnAmDhIk@h@c@RsA^yDvAJ~@E|Bm@jF_JDuHH{AF]AiB@kAEiG`@}k"
            "@XwKDeTNs_@T{gAj@}MFgDCkBE{EW}Ee@_Dk@wBi@yFsB}CuA{Aw@yCkBaHqEe[eSwP}K_@]yQ"
            "mL{E_DyEgDy@a@uJkG{GqEiEoCIi@{AcAUq@E_@Jk@HQRQXM`@Gf@F\\PRTNf@@^Qv@gKrHeHd"
            "FUFi@p@IR_[tTeJxGsFzDsCvBeYdSmJlGgLhIyBxAyD|BeFbCcFfBgDbAuGzAsEv@qDd@yEb@eFVs"
            "FwECsDKcDUoCUkAUyC_@{E_AeHgB_DaAuCiAqCmAkDiBgDqB}DqC}BkBqCcCqAsA}CsDsAgBqCiEyBu"
            "DgAwBkGaOyDoJwAoDeDiIgD_IuA_DcNa\\iB}DoA{C]s@}@wBqAsCqAiCkC{E{AmC}D}F_DgEeAqAsBcC"
            "qByBsDoDoE{DiEiDuCqB{DeCiF{CkCsAcFaCgGeCuFoBiEqAqB_@kl@gQcqAc`@sJgCMsBvC`@rAHHJr@DpCv@jL"
            "hE|Br@nChA`@T^Xd@HhQdF~LrD"
        )
        self.trip = Trip.objects.create(
            starting_location=Point(3.3792, 6.5244, srid=4326),
            destination_location=Point(3.421, 6.431, srid=4326),
            route_geometry=self.encoded_polyline,  # Use the stored polyline
            route_geometry_decoded=LineString([
                (3.3792, 6.5244),
                (3.421, 6.431)
            ], srid=4326),
            distance=5000,
            duration=600,
            available_seats=3,
            is_ride_requests_allowed=True
        )
        self.trip_id = self.trip.id

    @patch("trip.v1.serializers.compute_route_polyline")
    def test_create_trip_success(self, mock_compute_route):
        mock_compute_route.return_value = {
            "success": True,
            "polyline": self.encoded_polyline,
            "route_geometry_decoded": LineString(
                [(3.3792, 6.5244), (3.421, 6.431)],
                srid=4326
            ),
            "distance_m": 5000,
            "duration_s": "600s",
        }
        url = "/api/trips/"
        payload = {
            "starting_latitude": 6.5244,
            "starting_longitude": 3.3792,
            "destination_latitude": 6.431,
            "destination_longitude": 3.421,
            "available_seats": 2,
            "is_ride_requests_allowed": True
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("route_geometry", response.data)
        self.assertEqual(response.data["available_seats"], 2)

    @patch("trip.v1.serializers.compute_route_polyline")
    def test_update_trip_coordinates(self, mock_compute_route):
        mock_compute_route.return_value = {
            "success": True,
            "polyline": self.encoded_polyline,
            "route_geometry_decoded": LineString(
                [(3.3792, 6.5244), (3.421, 6.431)],
                srid=4326
            ),
            "distance_m": 5000,
            "duration_s": "600s",
        }

        url = f"/api/trips/{self.trip_id}/"
        payload = {
            "starting_latitude": 6.5245,
            "starting_longitude": 3.3795
        }
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["route_geometry"], self.encoded_polyline)

    def test_retrieve_trip(self):
        url = f"/api/trips/{self.trip_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.trip_id))

    def test_delete_trip(self):
        url = f"/api/trips/{self.trip_id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Trip.objects.filter(id=self.trip_id).exists())

    def test_list_matching_trips(self):
        url = "/api/trips/matches/"
        params = {
            "starting_latitude": 6.5244,
            "starting_longitude": 3.3792,
            "destination_latitude": 6.431,
            "destination_longitude": 3.421,
            "number_of_seats": 1
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_matches", response.data)
