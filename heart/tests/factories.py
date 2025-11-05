import factory
from django.utils import timezone
from ..models.heart_rate_record import HeartRateRecord
from user.tests.factories import ClientFactory
from training_session.tests.factories import TrainingSessionFactory  # if you have one


class HeartRateRecordFactory(factory.django.DjangoModelFactory):
    """
    Factory for HeartRateRecord for testing.
    """

    client = factory.SubFactory(ClientFactory)
    device_id = factory.Sequence(lambda n: f"device_{n}")
    bpm = factory.Faker("random_int", min=50, max=180)
    timestamp = factory.LazyFunction(timezone.now)
    session_timestamp = factory.LazyFunction(timezone.now)
    training_session = factory.SubFactory(TrainingSessionFactory)

    class Meta:
        model = HeartRateRecord
