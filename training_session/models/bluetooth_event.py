from core.models.behaviours import TimeStampable
from django.db import models


class BluetoothEvent(TimeStampable):
    EVENT_TYPES = [
        ("CONNECT", "Connect"),
        ("DISCONNECT", "Disconnect"),
        ("RECONNECT", "Reconnect"),
        ("ERROR", "Error"),
    ]

    training_session = models.ForeignKey(
        "TrainingSession",
        on_delete=models.CASCADE,
        related_name="connection_events"
    )

    device_id = models.UUIDField()

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["training_session"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["timestamp"]),
        ]
