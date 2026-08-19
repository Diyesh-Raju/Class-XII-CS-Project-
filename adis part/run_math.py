"""
RunCity — Student 3: Run Math Utilities
Haversine distance, speed validation, currency calculation, pace.
Pure Python — no external dependencies.
"""

import math
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Game constants (change these to tune the game)
# ---------------------------------------------------------------------------
CURRENCY_PER_KM   = 10       # coins earned per km
MIN_SPEED_KMH     = 3.0      # below this → not counted (walking too slow / GPS drift)
MAX_SPEED_KMH     = 20.0     # above this → invalid segment (cheating / driving)
DAILY_CAP_KM      = 10.0     # max km that earn currency per day
GPS_INTERVAL_SEC  = 10       # how often a GPS point is recorded


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return the great-circle distance in kilometres between two GPS coordinates.
    Uses the Haversine formula — accurate to within ~0.3% for typical run distances.
    """
    R = 6371.0  # Earth's mean radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ---------------------------------------------------------------------------
# Segment / point dataclass
# ---------------------------------------------------------------------------

@dataclass
class GpsPoint:
    latitude:  float
    longitude: float
    timestamp: float   # Unix epoch seconds (float)
    altitude:  float | None = None
    accuracy:  float | None = None


@dataclass
class Segment:
    """Stats for the stretch between two consecutive GPS points."""
    distance_km:  float
    duration_sec: float
    speed_kmh:    float
    is_valid:     bool   # False if speed outside [MIN, MAX]


def compute_segment(p1: GpsPoint, p2: GpsPoint) -> Segment:
    """
    Calculate stats for one GPS segment.
    Marks invalid if speed is outside the allowed range.
    """
    dist_km = haversine_km(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
    dur_sec = p2.timestamp - p1.timestamp

    if dur_sec <= 0:
        return Segment(0.0, 0.0, 0.0, False)

    speed_kmh = (dist_km / dur_sec) * 3600
    valid = MIN_SPEED_KMH <= speed_kmh <= MAX_SPEED_KMH

    return Segment(dist_km, dur_sec, speed_kmh, valid)


# ---------------------------------------------------------------------------
# Full-run analysis
# ---------------------------------------------------------------------------

@dataclass
class RunStats:
    total_distance_km:  float
    valid_distance_km:  float   # only segments that pass speed check
    total_duration_sec: int
    avg_speed_kmh:      float
    avg_pace_minkm:     float   # minutes per km
    currency_earned:    int
    is_run_valid:       bool    # False if the whole run is under MIN_SPEED
    capped:             bool    # True if daily cap was hit mid-run
    segments:           list[Segment]


def analyse_run(
    points: list[GpsPoint],
    already_run_km_today: float = 0.0,
) -> RunStats:
    """
    Process a list of GPS points and return full run statistics.

    Parameters
    ----------
    points:
        Chronologically ordered GPS readings for this run.
    already_run_km_today:
        How many km the user has already logged today (for daily cap).
    """
    if len(points) < 2:
        return RunStats(0, 0, 0, 0, 0, 0, False, False, [])

    segments: list[Segment] = []
    for i in range(len(points) - 1):
        segments.append(compute_segment(points[i], points[i + 1]))

    total_distance   = sum(s.distance_km  for s in segments)
    total_duration   = sum(s.duration_sec for s in segments)
    valid_segments   = [s for s in segments if s.is_valid]
    valid_distance   = sum(s.distance_km for s in valid_segments)

    # Average speed over valid segments only
    valid_duration = sum(s.duration_sec for s in valid_segments)
    avg_speed = ((valid_distance / valid_duration) * 3600) if valid_duration > 0 else 0.0

    # Pace: minutes per km
    avg_pace = (valid_duration / 60) / valid_distance if valid_distance > 0 else 0.0

    # --- Daily cap ---
    remaining_cap = max(0.0, DAILY_CAP_KM - already_run_km_today)
    billable_km   = min(valid_distance, remaining_cap)
    capped        = valid_distance > remaining_cap

    currency = int(billable_km * CURRENCY_PER_KM)
    is_valid = valid_distance > 0

    return RunStats(
        total_distance_km  = round(total_distance, 4),
        valid_distance_km  = round(valid_distance, 4),
        total_duration_sec = int(total_duration),
        avg_speed_kmh      = round(avg_speed, 2),
        avg_pace_minkm     = round(avg_pace, 2),
        currency_earned    = currency,
        is_run_valid       = is_valid,
        capped             = capped,
        segments           = segments,
    )


# ---------------------------------------------------------------------------
# Formatting helpers (used by the UI)
# ---------------------------------------------------------------------------

def format_duration(seconds: int) -> str:
    """e.g. 3723 → '1:02:03'"""
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_pace(pace_minkm: float) -> str:
    """e.g. 5.5 → '5:30 /km'"""
    if pace_minkm <= 0:
        return "--:-- /km"
    mins   = int(pace_minkm)
    secs   = int((pace_minkm - mins) * 60)
    return f"{mins}:{secs:02d} /km"


def format_distance(km: float) -> str:
    """e.g. 0.523 → '523 m', 1.234 → '1.23 km'"""
    if km < 1.0:
        return f"{int(km * 1000)} m"
    return f"{km:.2f} km"
