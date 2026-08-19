"""
RunCity — Student 3: GPS Tracker
Wraps flet_geolocator to:
  • Request permissions on startup
  • Record a GPS point every GPS_INTERVAL_SEC (default 10 s)
  • Compute live distance / speed / pace after every new point
  • Save points to the local SQLite DB in real time
  • Call an optional on_update(stats) callback so the UI can refresh

Usage (inside a Flet view):
    tracker = GpsTracker(page, user_id=1)
    await tracker.request_permissions()
    run_id = await tracker.start_run()
    # ... user is running ...
    stats = await tracker.stop_run()
"""

import asyncio
import datetime
import flet as ft

try:
    import flet_geolocator as geo   # type: ignore
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False           # will use mock data in the emulator

from utils.run_math import (
    GpsPoint, analyse_run, format_distance, format_duration, format_pace,
    GPS_INTERVAL_SEC,
)
from db.local_db import (
    init_db, insert_run, insert_gps_point, finish_run, add_daily_km, get_daily_km,
)


class GpsTracker:
    """
    Manages a single run: permission → start → record loop → stop → save.
    Thread-safe: all DB writes happen on the asyncio event loop.
    """

    def __init__(self, page: ft.Page, user_id: int, on_update=None):
        """
        Parameters
        ----------
        page       : the Flet Page (needed to call geolocator)
        user_id    : local user ID (from login session)
        on_update  : optional async callable(live_stats: dict) — called each tick
        """
        self.page      = page
        self.user_id   = user_id
        self.on_update = on_update   # async callback for live UI updates

        self._run_id:    int | None    = None
        self._points:    list[GpsPoint] = []
        self._running:   bool           = False
        self._task:      asyncio.Task | None = None
        self._started_at: datetime.datetime | None = None

        init_db()   # ensure tables exist

    # ------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------

    async def request_permissions(self) -> bool:
        """Ask the OS for location permission. Returns True if granted."""
        if not GEO_AVAILABLE:
            print("[GPS] flet_geolocator not installed — mock mode active")
            return True

        gl = geo.Geolocator()
        self.page.overlay.append(gl)
        await self.page.update_async()

        status = await gl.request_permission_async()
        granted = status in (
            geo.GeolocatorPermissionStatus.ALWAYS,
            geo.GeolocatorPermissionStatus.WHILE_IN_USE,
        )
        if not granted:
            print(f"[GPS] Permission denied: {status}")
        return granted

    # ------------------------------------------------------------------
    # Start / Stop
    # ------------------------------------------------------------------

    async def start_run(self) -> int:
        """
        Open a new run_log row in SQLite, begin the GPS recording loop.
        Returns the local run_id.
        """
        if self._running:
            raise RuntimeError("A run is already in progress.")

        self._points    = []
        self._running   = True
        self._started_at = datetime.datetime.utcnow()

        self._run_id = insert_run(
            self.user_id,
            self._started_at.isoformat(),
        )
        print(f"[GPS] Run started  — run_id={self._run_id}")

        self._task = asyncio.create_task(self._recording_loop())
        return self._run_id

    async def stop_run(self) -> dict:
        """
        Stop the GPS loop, finalise stats, write the completed row, return summary.
        """
        if not self._running:
            raise RuntimeError("No run is in progress.")

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        ended_at = datetime.datetime.utcnow()
        today    = ended_at.strftime("%Y-%m-%d")

        already_today = get_daily_km(self.user_id, today)
        stats = analyse_run(self._points, already_today)

        finish_run(
            run_id         = self._run_id,
            ended_at       = ended_at.isoformat(),
            distance_km    = stats.valid_distance_km,
            duration_sec   = stats.total_duration_sec,
            currency_earned= stats.currency_earned,
            avg_speed_kmh  = stats.avg_speed_kmh,
            avg_pace_minkm = stats.avg_pace_minkm,
            is_valid       = int(stats.is_run_valid),
            notes          = "daily cap reached" if stats.capped else "",
        )

        if stats.is_run_valid and stats.valid_distance_km > 0:
            add_daily_km(self.user_id, today, stats.valid_distance_km)

        summary = self._build_summary(stats)
        print(f"[GPS] Run finished — {summary}")
        return summary

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    async def _recording_loop(self):
        """Record one GPS point every GPS_INTERVAL_SEC while running."""
        gl = None
        if GEO_AVAILABLE:
            gl = geo.Geolocator()
            self.page.overlay.append(gl)
            await self.page.update_async()

        while self._running:
            await asyncio.sleep(GPS_INTERVAL_SEC)
            if not self._running:
                break

            point = await self._get_position(gl)
            if point is None:
                continue

            self._points.append(point)
            recorded_at = datetime.datetime.utcfromtimestamp(point.timestamp).isoformat()
            insert_gps_point(
                run_id      = self._run_id,
                recorded_at = recorded_at,
                latitude    = point.latitude,
                longitude   = point.longitude,
                altitude_m  = point.altitude,
                accuracy_m  = point.accuracy,
            )

            # Compute live stats and notify the UI
            if self.on_update and len(self._points) >= 2:
                stats = analyse_run(self._points)
                live  = self._build_live(stats)
                await self.on_update(live)

    async def _get_position(self, gl) -> GpsPoint | None:
        """
        Fetch the current GPS position.
        Falls back to a deterministic mock if flet_geolocator is unavailable.
        """
        import time

        if GEO_AVAILABLE and gl is not None:
            try:
                pos = await gl.get_current_position_async()
                return GpsPoint(
                    latitude  = pos.latitude,
                    longitude = pos.longitude,
                    timestamp = time.time(),
                    altitude  = getattr(pos, "altitude", None),
                    accuracy  = getattr(pos, "accuracy", None),
                )
            except Exception as e:
                print(f"[GPS] position error: {e}")
                return None
        else:
            # ---------------------------------------------------------------
            # MOCK MODE — useful for desktop testing without a real device.
            # Simulates running at ~10 km/h along a straight path.
            # ---------------------------------------------------------------
            return self._mock_position()

    def _mock_position(self) -> GpsPoint:
        """
        Simulates movement: each call advances ~28 m east (≈10 km/h at 10 s intervals).
        Starting point: Bengaluru city centre (12.9716, 77.5946).
        """
        import time
        n       = len(self._points)
        base_lat = 12.9716
        base_lon = 77.5946
        # 0.00025 degrees ≈ 27.8 m longitude step (≈ 10 km/h @ 10 s)
        return GpsPoint(
            latitude  = base_lat + n * 0.00001,   # slight northward drift
            longitude = base_lon + n * 0.00025,
            timestamp = time.time(),
            altitude  = 920.0,
            accuracy  = 5.0,
        )

    # ------------------------------------------------------------------
    # Stat dictionaries (passed to UI / summary screen)
    # ------------------------------------------------------------------

    def _build_live(self, stats) -> dict:
        elapsed = int(
            (datetime.datetime.utcnow() - self._started_at).total_seconds()
        ) if self._started_at else 0
        return {
            "distance_str":  format_distance(stats.valid_distance_km),
            "distance_km":   stats.valid_distance_km,
            "duration_str":  format_duration(elapsed),
            "duration_sec":  elapsed,
            "speed_str":     f"{stats.avg_speed_kmh:.1f} km/h",
            "speed_kmh":     stats.avg_speed_kmh,
            "pace_str":      format_pace(stats.avg_pace_minkm),
            "currency":      stats.currency_earned,
            "points_count":  len(self._points),
        }

    def _build_summary(self, stats) -> dict:
        return {
            "run_id":           self._run_id,
            "distance_str":     format_distance(stats.valid_distance_km),
            "distance_km":      stats.valid_distance_km,
            "duration_str":     format_duration(stats.total_duration_sec),
            "duration_sec":     stats.total_duration_sec,
            "avg_speed_kmh":    stats.avg_speed_kmh,
            "avg_pace_str":     format_pace(stats.avg_pace_minkm),
            "currency_earned":  stats.currency_earned,
            "is_valid":         stats.is_run_valid,
            "capped":           stats.capped,
            "points_recorded":  len(self._points),
        }
