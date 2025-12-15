from dataclasses import asdict
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Dict


@dataclass
class GoogleRouteRequest:
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float
    travelMode: str = "DRIVE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
