from django.core.cache import cache
from django.core.management.base import BaseCommand

from trip.models import TripSettingsConfig


class Command(BaseCommand):
    help = "Seed TripSettingsConfig with default values"

    def handle(self, *args, **options):
        radius_meters = 500
        speed_kmh = 30
        speed_mps = speed_kmh * 1000 / 3600

        settings_obj, created = TripSettingsConfig.objects.get_or_create(
            is_active=True,
            defaults={
                'radius': radius_meters,
                'speed': speed_kmh,
                'speed_mps': speed_mps,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"TripSettingsConfig created: radius={radius_meters}m, speed={speed_kmh}km/h ({speed_mps:.2f} m/s)"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "Active TripSettingsConfig already exists"
            ))

        cache.set('active_trip_settings', settings_obj, timeout=None)
