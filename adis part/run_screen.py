"""
RunCity — Student 3: Run Screen (Flet UI)
Dark fitness/game aesthetic.
Plug this view into Student 2's ft.View navigation as route "/run".

Usage from Student 2's navigation:
    from ui.run_screen import build_run_view
    page.views.append(build_run_view(page, user_id=session["user_id"]))
    await page.update_async()
"""

import asyncio
import flet as ft
from gps.tracker import GpsTracker
from db.local_db import get_runs_for_user


# ── Palette ────────────────────────────────────────────────────────────────
BG        = "#0D0F14"
SURFACE   = "#161A22"
CARD      = "#1E2533"
ACCENT    = "#00FF87"      # neon green = "running"
DANGER    = "#FF4757"      # red = stop / invalid
GOLD      = "#FFD700"      # currency
TEXT      = "#E8EAF0"
SUBTEXT   = "#7A8099"
INACTIVE  = "#2A2F3F"


def _stat_tile(label: str, value_ref: ft.Ref, unit: str = "") -> ft.Container:
    """One live stat block — label on top, big number below."""
    return ft.Container(
        bgcolor=CARD,
        border_radius=16,
        padding=ft.padding.symmetric(vertical=18, horizontal=12),
        expand=True,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(label, size=11, color=SUBTEXT, weight=ft.FontWeight.W_500),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=2,
                    controls=[
                        ft.Text(ref=value_ref, size=26,
                                color=TEXT, weight=ft.FontWeight.BOLD),
                        ft.Text(unit, size=11, color=SUBTEXT),
                    ],
                ),
            ],
        ),
    )


def build_run_view(page: ft.Page, user_id: int) -> ft.View:
    """
    Build and return the full Run Screen ft.View.
    Call this from Student 2's router.
    """

    # ── Refs (live-updating controls) ──────────────────────────────────────
    r_distance  = ft.Ref[ft.Text]()
    r_duration  = ft.Ref[ft.Text]()
    r_speed     = ft.Ref[ft.Text]()
    r_pace      = ft.Ref[ft.Text]()
    r_currency  = ft.Ref[ft.Text]()
    r_points    = ft.Ref[ft.Text]()
    r_status    = ft.Ref[ft.Text]()    # status bar message
    r_btn_label = ft.Ref[ft.Text]()
    r_btn_icon  = ft.Ref[ft.Icon]()

    # ── Progress ring ──────────────────────────────────────────────────────
    progress_ring = ft.ProgressRing(
        width=160, height=160,
        stroke_width=8,
        color=ACCENT,
        bgcolor=INACTIVE,
        value=0,     # 0–1 mapped to daily cap progress
    )
    r_progress_label = ft.Ref[ft.Text]()

    # ── State ──────────────────────────────────────────────────────────────
    is_running    = [False]
    tracker: list[GpsTracker | None] = [None]
    perm_granted  = [False]

    # ── Summary overlay ────────────────────────────────────────────────────
    summary_sheet = ft.BottomSheet(
        open=False,
        content=ft.Container(
            bgcolor=SURFACE,
            border_radius=ft.border_radius.only(top_left=24, top_right=24),
            padding=30,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Text("Run Complete 🎉", size=22,
                            color=ACCENT, weight=ft.FontWeight.BOLD),
                    ft.Divider(color=INACTIVE, height=1),
                    ft.Text(ref=ft.Ref(), size=14, color=TEXT),  # filled dynamically
                ],
            ),
        ),
    )

    # ── History list ───────────────────────────────────────────────────────
    history_list = ft.ListView(spacing=8, padding=ft.padding.symmetric(vertical=4))

    def _load_history():
        history_list.controls.clear()
        runs = get_runs_for_user(user_id, limit=10)
        if not runs:
            history_list.controls.append(
                ft.Text("No runs yet — lace up!", color=SUBTEXT, size=13,
                        text_align=ft.TextAlign.CENTER)
            )
            return
        for run in runs:
            synced_icon = "☁️" if run["synced"] else "📲"
            valid_color = ACCENT if run["is_valid"] else DANGER
            history_list.controls.append(
                ft.Container(
                    bgcolor=CARD,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        f"{run['started_at'][:10]}  "
                                        f"{run['distance_km']:.2f} km",
                                        size=13, color=TEXT, weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Text(
                                        f"{run['duration_sec']//60} min  •  "
                                        f"{run['avg_speed_kmh']:.1f} km/h  "
                                        f"{synced_icon}",
                                        size=11, color=SUBTEXT,
                                    ),
                                ],
                            ),
                            ft.Text(
                                f"+{run['currency_earned']} 🪙",
                                size=14, color=valid_color, weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                )
            )

    # ── Callbacks ──────────────────────────────────────────────────────────

    async def on_live_update(live: dict):
        """Called every 10 s by the tracker — refreshes stat tiles."""
        r_distance.current.value = live["distance_str"]
        r_duration.current.value = live["duration_str"]
        r_speed.current.value    = f"{live['speed_kmh']:.1f}"
        r_pace.current.value     = live["pace_str"].replace(" /km", "")
        r_currency.current.value = str(live["currency"])
        r_points.current.value   = str(live["points_count"])

        # Daily progress ring (value 0-1 capped at 1)
        progress_ring.value = min(live["distance_km"] / 10.0, 1.0)
        r_progress_label.current.value = live["distance_str"]

        await page.update_async()

    async def on_start_stop(_):
        if not perm_granted[0]:
            r_status.current.value = "⚠️  Requesting GPS permission…"
            await page.update_async()
            t = GpsTracker(page, user_id, on_update=on_live_update)
            granted = await t.request_permissions()
            perm_granted[0] = granted
            if not granted:
                r_status.current.value = "❌  GPS permission denied — cannot run"
                await page.update_async()
                return
            tracker[0] = t

        if not is_running[0]:
            # ── START ──
            is_running[0] = True
            r_btn_label.current.value = "STOP RUN"
            r_btn_icon.current.name   = ft.icons.STOP_CIRCLE_ROUNDED
            r_status.current.value    = "🟢  GPS active — go run!"
            # Reset tiles
            for ref, val in [
                (r_distance, "0 m"), (r_duration, "0:00"),
                (r_speed, "0.0"), (r_pace, "--:--"),
                (r_currency, "0"), (r_points, "0"),
            ]:
                ref.current.value = val
            progress_ring.value = 0
            r_progress_label.current.value = "0 m"
            await page.update_async()

            if tracker[0] is None:
                tracker[0] = GpsTracker(page, user_id, on_update=on_live_update)
            await tracker[0].start_run()

        else:
            # ── STOP ──
            is_running[0] = False
            r_btn_label.current.value = "START RUN"
            r_btn_icon.current.name   = ft.icons.PLAY_CIRCLE_ROUNDED
            r_status.current.value    = "⏳  Saving run…"
            await page.update_async()

            summary = await tracker[0].stop_run()
            tracker[0] = None
            perm_granted[0] = False   # fresh permission next run

            _show_summary(summary)
            _load_history()
            r_status.current.value = "✅  Run saved!"
            await page.update_async()

    def _show_summary(s: dict):
        lines = [
            f"📏 Distance:   {s['distance_str']}",
            f"⏱️  Duration:   {s['duration_str']}",
            f"💨 Avg Speed:  {s['avg_speed_kmh']:.1f} km/h",
            f"🏃 Avg Pace:   {s['avg_pace_str']}",
            f"🪙 Currency:   +{s['currency_earned']} coins",
            "",
            "⚠️  Daily cap reached — no more coins today." if s["capped"] else "",
            "❌  Run invalid (speed outside 3–20 km/h)." if not s["is_valid"] else "",
        ]
        summary_sheet.content.content.controls[2].value = "\n".join(
            l for l in lines if l != ""
        )
        summary_sheet.open = True
        asyncio.create_task(page.update_async())

    async def on_close_summary(_):
        summary_sheet.open = False
        await page.update_async()

    # ── Load history on view open ──────────────────────────────────────────
    _load_history()

    # ── Layout ────────────────────────────────────────────────────────────
    view = ft.View(
        route="/run",
        bgcolor=BG,
        padding=0,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            # App bar
            ft.AppBar(
                title=ft.Text("RUN", size=18, weight=ft.FontWeight.W_800,
                              color=ACCENT, letter_spacing=4),
                bgcolor=BG,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
                    icon_color=TEXT,
                    on_click=lambda _: page.go("/dashboard"),
                ),
            ),

            ft.Container(
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                content=ft.Column(
                    spacing=20,
                    controls=[

                        # ── Status bar ─────────────────────────────────
                        ft.Container(
                            bgcolor=SURFACE,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            content=ft.Text(
                                ref=r_status,
                                value="Press START to begin tracking your run",
                                size=13, color=SUBTEXT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),

                        # ── Progress ring + label ──────────────────────
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Stack(
                                    width=180, height=180,
                                    controls=[
                                        ft.Container(
                                            width=180, height=180,
                                            content=progress_ring,
                                            alignment=ft.alignment.center,
                                        ),
                                        ft.Column(
                                            width=180, height=180,
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                ft.Text(
                                                    ref=r_progress_label,
                                                    value="0 m",
                                                    size=22, color=TEXT,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    "/ 10 km daily",
                                                    size=10, color=SUBTEXT,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),

                        # ── Stat tiles row 1 ───────────────────────────
                        ft.Row(
                            spacing=10,
                            controls=[
                                _stat_tile("DURATION",  r_duration),
                                _stat_tile("SPEED",     r_speed, "km/h"),
                            ],
                        ),

                        # ── Stat tiles row 2 ───────────────────────────
                        ft.Row(
                            spacing=10,
                            controls=[
                                _stat_tile("PACE",      r_pace, "/km"),
                                _stat_tile("CURRENCY",  r_currency, "🪙"),
                            ],
                        ),

                        # ── GPS points counter ─────────────────────────
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.icons.GPS_FIXED, color=ACCENT, size=14),
                                ft.Text(ref=r_points, value="0", size=12, color=SUBTEXT),
                                ft.Text(" GPS points recorded",
                                        size=12, color=SUBTEXT),
                            ],
                        ),

                        # ── Start / Stop button ────────────────────────
                        ft.Container(
                            on_click=on_start_stop,
                            bgcolor=ACCENT,
                            border_radius=50,
                            padding=ft.padding.symmetric(horizontal=40, vertical=18),
                            alignment=ft.alignment.center,
                            content=ft.Row(
                                tight=True,
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(
                                        ref=r_btn_icon,
                                        name=ft.icons.PLAY_CIRCLE_ROUNDED,
                                        color=BG, size=28,
                                    ),
                                    ft.Text(
                                        ref=r_btn_label,
                                        value="START RUN",
                                        size=16, color=BG,
                                        weight=ft.FontWeight.W_800,
                                        letter_spacing=2,
                                    ),
                                ],
                            ),
                        ),

                        # ── Recent runs ───────────────────────────────
                        ft.Text("Recent Runs", size=15, color=TEXT,
                                weight=ft.FontWeight.BOLD),
                        history_list,

                    ],
                ),
            ),

            # ── Summary bottom sheet ──────────────────────────────────
            summary_sheet,
        ],
    )

    return view
