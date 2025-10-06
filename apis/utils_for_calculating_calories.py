

def calculate_current_burned_calories(list_of_bpms, client, training_session, seconds):
    if not list_of_bpms:
        print("No bpms given")
        return 0

    average_bpm = calculate_average_heart_rate(list_of_bpms)
    weight = client.weight
    age = client.user.get_age_from_birth_date()

    duration_in_minutes = seconds / 60

    # Ako je trajanje manje od sekunde, vrati 0
    if duration_in_minutes <= 0:
        return 0

    if client.gender == 'male':
        calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * weight) + (
                    0.2017 * age)) / 4.184) * duration_in_minutes
    else:
        calories = ((-20.4022 + (0.4472 * average_bpm) - (0.1263 * weight) + (
                    0.074 * age)) / 4.184) * duration_in_minutes

    # Minimalna vrednost po minuti (npr. 0.8 kcal/min)
    min_calories = duration_in_minutes * 0.8

    # Uvek vraćaj barem minimalno, zaokruženo na 2 decimale
    return round(max(calories, min_calories), 2)


def calculate_average_heart_rate(list_of_bpms):
    average = sum(list_of_bpms) / len(list_of_bpms)
    return average
