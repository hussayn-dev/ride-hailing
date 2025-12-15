from cuid2 import Cuid

CUID_GENERATOR: Cuid = Cuid(length=24)


def generate_unique_id() -> str:
    return CUID_GENERATOR.generate()

