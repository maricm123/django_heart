import factory
from decimal import Decimal

from training_session.models import TrainingSession
from user.tests.factories import CoachFactory, ClientFactory


class TrainingSessionFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("sentence", nb_words=3)
    gym = None
    coach = factory.SubFactory(CoachFactory)
    client = factory.SubFactory(ClientFactory)

    calories_burned = factory.LazyFunction(lambda: Decimal("350.00"))
    duration = factory.Faker("random_int", min=600, max=3600)  # duration in seconds

    summary_metrics = factory.LazyFunction(lambda: {
        "avg_hr": 140,
        "max_hr": 180,
        "duration_seconds": 1800,
        "calories": 350,
        "hr_zones": {
            "z1_minutes": 5,
            "z2_minutes": 10,
            "z3_minutes": 15,
            "z4_minutes": 8,
            "z5_minutes": 2
        }
    })

    class Meta:
        model = TrainingSession
