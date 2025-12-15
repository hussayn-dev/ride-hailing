from urllib.parse import urlparse

import redis
from django.conf import settings
from django.db import OperationalError, connections
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def readiness_check(request):
    response = {"database": "unknown", "redis": "unknown"}

    # Check database connection
    try:
        db_conn = connections["default"]
        db_conn.cursor()
        response["database"] = "ready"
    except OperationalError:
        response["database"] = "not ready"

    # Check Redis connection
    try:
        redis_url = urlparse(settings.REDIS_URL)
        r = redis.StrictRedis(
            host=redis_url.hostname,
            port=redis_url.port,
            password=redis_url.password,
            decode_responses=True,
        )
        r.ping()
        response["redis"] = "ready"
    except redis.ConnectionError:
        response["redis"] = "not ready"

    return Response(response)


@api_view(["GET"])
def health_check(request):
    response = {"status": True}
    return Response(response)
