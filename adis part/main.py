"""
RunCity — Student 3: Main entry point
Run this file directly to test the GPS run screen in isolation.
When Student 2 integrates, they import build_run_view from ui.run_screen.

Usage:
    python main.py
    python main.py --target android   (for mobile)
"""

import flet as ft
from db.local_db import init_db
from ui.run_screen import build_run_view

# A placeholder user_id for standalone testing.
# In the real app this comes from Student 1's JWT login.
TEST_USER_ID = 1


async def main(page: ft.Page):
    page.title  = "RunCity — GPS Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0D0F14"
    page.padding = 0

    init_db()   # create tables if needed

    # ── Simple router (Student 2 will replace this) ──────────────────────
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        if page.route == "/run" or page.route == "/":
            page.views.append(build_run_view(page, user_id=TEST_USER_ID))
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top = page.views[-1]
        page.go(top.route)

    page.on_route_change = route_change
    page.on_view_pop     = view_pop
    page.go("/run")


if __name__ == "__main__":
    ft.app(target=main)
