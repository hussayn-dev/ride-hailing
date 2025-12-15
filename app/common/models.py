from common.kgs import generate_unique_id
from django.db import models
from django.utils.timezone import now


class AuditableModel(models.Model):
    id = models.CharField(
        max_length=50,
        primary_key=True,
        default=generate_unique_id,
        editable=False,
        db_index=True,
    )
    created_at = models.DateTimeField(default=now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
