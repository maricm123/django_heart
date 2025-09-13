from django.utils import timezone


# def calculate_burned_calories():
#     pass
#
#
# def calculate_calories_at_end_of_session(
#     training_session,
#     client_gender,
#     client_age,
#     client_weight,
#     client_height,
#     training_session_start_time
# ):
#     list_of_bpms = [record.bpm for record in training_session.heart_rate_records.all()]
#     print(list_of_bpms, "LIST OF BPMS")
#     if len(list_of_bpms) != 0:
#         average_bpm = calculate_average_heart_rate(list_of_bpms)
#
#         duration_in_minutes = calculate_current_duration_in_minutes(training_session_start_time)
#         print(duration_in_minutes, "DURATION AT END")
#
#         if client_gender == 'Male':
#             calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * client_weight) + (0.2017 * client_age)) / 4.184) * duration_in_minutes
#         else:
#             calories = ((-20.4022 + (0.4472 * average_bpm) - (0.1263 * client_weight) + (0.074 * client_age)) / 4.184) * duration_in_minutes
#
#         print(max(round(calories, 2), 0), "CALORIES")
#         return max(round(calories, 2), 0)
#
#
# def calculate_average_heart_rate(list_of_bpms):
#     average = sum(list_of_bpms) / len(list_of_bpms)
#     return average


# def calculate_current_duration_in_minutes(start):
#     end = timezone.now()
#     duration = (end - start).total_seconds() / 60
#     return duration


def calculate_current_burned_calories(list_of_bpms, client, training_session, current_timestamp):
    if not list_of_bpms:
        print("No bpms given")
        return 0

    average_bpm = calculate_average_heart_rate(list_of_bpms)
    weight = client.weight
    age = client.user.get_age_from_birth_date()
    duration_in_minutes = calculate_current_duration_in_minutes(training_session.start, current_timestamp)
    print(duration_in_minutes, "CURRENT DURATION")

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


def calculate_current_duration_in_minutes(start, end):
    duration = (end - start).total_seconds() / 60
    return duration
