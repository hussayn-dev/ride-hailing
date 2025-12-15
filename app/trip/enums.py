from common.enums import CustomEnum


class TripStatus(CustomEnum):
    Completed = 'Completed'
    Ongoing = 'Ongoing'
    Failed = 'Failed'
    Initiated = 'Initiated'


def default_state():
    return []
