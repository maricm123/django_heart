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
    if gender == 'Male':
        calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * weight) + (
                0.2017 * age)) / 4.184) * duration_in_minutes
        return round(calories, 2)
    elif gender == 'Female':
        calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * weight) + (
                0.2017 * age)) / 4.184) * duration_in_minutes
        return calories
