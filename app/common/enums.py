from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return [c.value for c in cls]

    @classmethod
    def choices(cls):
        return [(c.value, c.value) for c in cls]
