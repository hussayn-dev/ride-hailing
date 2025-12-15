import django_filters as filters

from common.filter import DateFilter
from .models import Trip


class TripFilter(DateFilter):
    is_active = filters.BooleanFilter()

    class Meta:
        model = Trip
        fields = ("created_by",)
