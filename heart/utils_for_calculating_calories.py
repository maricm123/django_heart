from decimal import Decimal, ROUND_HALF_UP


def calculate_current_burned_calories(list_of_bpms, client, seconds):
    if not list_of_bpms:
        return 0

    average_bpm = calculate_average_heart_rate(list_of_bpms)
    weight = client.weight
    age = client.user.age
    gender = client.gender

    duration_in_minutes = seconds / 60

    # Ako je trajanje manje od sekunde, vrati 0
    if duration_in_minutes <= 0:
        return 0

    calories = formula_for_calculating_calories(gender, average_bpm, weight, age, duration_in_minutes)

    # Minimalna vrednost po minuti (npr. 0.8 kcal/min)
    min_calories = duration_in_minutes * 0.8

    # Uvek vraćaj barem minimalno, zaokruženo na 2 decimale
    return round(max(calories, min_calories), 2)


def calculate_average_heart_rate(list_of_bpms):
    return sum(list_of_bpms) / len(list_of_bpms)


def formula_for_calculating_calories(gender, average_bpm, weight, age, duration_in_minutes):
    average_bpm = Decimal(str(average_bpm or 0))
    weight = Decimal(str(weight or 0))
    age = Decimal(str(age or 0))
    duration_in_minutes = Decimal(str(duration_in_minutes or 0))

    if gender == 'Male':
        calories = ((Decimal('-55.0969') + (Decimal('0.6309') * average_bpm) +
                     (Decimal('0.1988') * weight) + (Decimal('0.2017') * age)) / Decimal('4.184')) * duration_in_minutes
    else:
        calories = ((Decimal('-20.4022') + (Decimal('0.4472') * average_bpm) -
                     (Decimal('0.1263') * weight) + (Decimal('0.074') * age)) / Decimal('4.184')) * duration_in_minutes

    return calories.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
