from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

header = extend_schema(
    parameters=[
        OpenApiParameter(
            "X-Api-Key", OpenApiTypes.STR, OpenApiParameter.HEADER, required=True
        )
    ]
)
