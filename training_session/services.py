import logging
import math
from datetime import timedelta
from training_session.caches import get_cached_training_session, set_cached_training_session
from django.db import  transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


def process_training_session_metrics(session, bucket_seconds=10, ema_alpha=0.3):
    """
    Reads raw heart rate records from session,
    generates chart points + summary, stores metrics,
    deletes raw samples.
    """
    samples_qs = session.heart_rate_records.order_by('timestamp').values_list('timestamp', 'bpm')
    samples = list(samples_qs)

    if not samples:
        session.metrics = {"summary": {}, "points": []}
        session.save()
        return session  # return the updated session

    max_hr = get_client_max_heart_rate(session.client, samples)

    start_ts = session.start or samples[0][0]
    end_ts = session.end or samples[-1][0]
    total_seconds = int(math.ceil((end_ts - start_ts).total_seconds()))
    num_buckets = max(1, (total_seconds // bucket_seconds) + 1)

    buckets = [[] for _ in range(num_buckets)]
    for ts, bpm in samples:
        idx = int((ts - start_ts).total_seconds() // bucket_seconds)
        idx = max(0, min(idx, num_buckets - 1))
        buckets[idx].append(int(bpm))

    bucket_avgs = [
        (sum(b) / len(b)) if b else None
        for b in buckets
    ]

    # --- Interpolate missing ---
    def interpolate(arr):
        n = len(arr)
        i = 0
        while i < n:
            if arr[i] is None:
                j = i + 1
                while j < n and arr[j] is None:
                    j += 1
                left = arr[i-1] if i > 0 else None
                right = arr[j] if j < n else None

                if left is None and right is None:
                    for k in range(i, j):
                        arr[k] = 0
                elif left is None:
                    for k in range(i, j):
                        arr[k] = right
                elif right is None:
                    for k in range(i, j):
                        arr[k] = left
                else:
                    steps = j - i + 1
                    for s, k in enumerate(range(i, j)):
                        arr[k] = left + (right - left) * (s + 1) / (steps)
                i = j
            else:
                i += 1
        return arr

    bucket_avgs = interpolate(bucket_avgs)

    # --- EMA smoothing ---
    ema = [bucket_avgs[0]]
    for v in bucket_avgs[1:]:
        ema.append(ema_alpha * v + (1 - ema_alpha) * ema[-1])

    # --- Build points ---
    points = [
        { "ts": (start_ts + timedelta(seconds=i * bucket_seconds)).isoformat(), "bpm": round(bpm) }
        for i, bpm in enumerate(ema)
    ]

    # --- Summary ---
    avg_hr = round(sum(p["bpm"] for p in points) / len(points))
    max_hr_point = max(p["bpm"] for p in points)
    duration_seconds = int(session.duration or total_seconds)
    calories = float(session.calories_burned) if session.calories_burned else None

    # HR zones
    zones = {"z1": 0, "z2": 0, "z3": 0, "z4": 0, "z5": 0}
    for p in points:
        pct = p["bpm"] / max_hr
        if pct < 0.60:
            zones["z1"] += bucket_seconds
        elif pct < 0.70:
            zones["z2"] += bucket_seconds
        elif pct < 0.80:
            zones["z3"] += bucket_seconds
        elif pct < 0.90:
            zones["z4"] += bucket_seconds
        else:
            zones["z5"] += bucket_seconds

    summary = {
        "avg_hr": avg_hr,
        "max_hr": max_hr_point,
        "duration_seconds": duration_seconds,
        "calories": calories,
        "hr_zones_seconds": zones
    }

    # store final metrics
    session.summary_metrics = {
        "summary": summary,
        "points": points,
        "points_per_minute": int(60 / bucket_seconds)
    }
    session.save()

    session.heart_rate_records.all().delete()

    return session


def get_client_max_heart_rate(client, samples):
    """
    Return client's max heart rate.

    Logic:
    - If client has no stored max HR -> use 220 - age
    - Compare stored HR with current session HR
    - If current session HR is higher -> update client's stored HR
    - Return the final max HR value
    """
    heart_rates_from_current_session = [bpm for (_, bpm) in samples]
    max_heart_rate_from_current_session = max(heart_rates_from_current_session)

    # 1) Determine baseline client max HR
    if client.max_heart_rate is None:
        client_max_heart_rate = 220 - client.user.age
    else:
        client_max_heart_rate = client.max_heart_rate

    # 2) If the current session's max is higher, update the client
    if max_heart_rate_from_current_session > client_max_heart_rate:
        client_max_heart_rate = max_heart_rate_from_current_session
        client.max_heart_rate = client_max_heart_rate
        client.save(update_fields=["max_heart_rate"])

    return client_max_heart_rate


@transaction.atomic
def end_training_session(training_session, calories_at_end, duration, bucket_seconds=10):
    """
    Ends a training session and computes metrics.
    """
    now = timezone.now()

    # Update base fields
    training_session.duration = duration
    training_session.calories_burned = calories_at_end
    training_session.is_active = False
    training_session.end = now
    training_session.save(update_fields=["duration", "calories_burned", "is_active", "end"])

    # Metrics handled separately
    safely_process_metrics(training_session, bucket_seconds)

    return training_session


def safely_process_metrics(session, bucket_seconds=10):
    try:
        process_training_session_metrics(session, bucket_seconds=bucket_seconds)
    except Exception as e:
        logger.exception(f"Failed to process metrics for session {session.pk}: {e}")
        raise
