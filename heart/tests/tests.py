from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from heart.utils_for_calculating_calories import calculate_average_heart_rate, formula_for_calculating_calories
from user.tests.factories import CoachFactory
from user.models.client import Client

User = get_user_model()


@pytest.mark.django_db
class TestHeartRate:
    ####################################################################################################
    # Test functions for calories
    ####################################################################################################
    def test_calculate_average_heart_rate(self, tenant):
        coach = CoachFactory(gym=tenant)
        list_of_bpms = [
            123, 123, 123, 123, 123, 123
        ]
        average = calculate_average_heart_rate(list_of_bpms)
        assert average == 123

    def test_formula_for_calculating_calories(self):
        average_bpm = 140
        gender = 'Male'
        duration_in_minutes = 0.4
        age = 25
        weight = 80
        calories = formula_for_calculating_calories(gender, average_bpm, weight, age, duration_in_minutes)
        print(calories)
        assert round(calories, 2) == calories
