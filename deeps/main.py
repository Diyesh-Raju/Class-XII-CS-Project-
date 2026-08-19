import flet as ft

# Import all my screens
from screens.home import build_home
from screens.map import build_map
from screens.run import build_run
from screens.city import build_city
from screens.profile import build_profile

def main(page: ft.Page):
    # Basic app settings
    page.title = "RunCraft"
    page.bgcolor = "#0d0d0d"
    page.padding = 0

    # This holds what screen is currently showing
    content_area = ft.Column(expand=True)

    # Function to switch between screens
    def switch_screen(screen_name):
        content_area.controls.clear()

        if screen_name == "home":
            content_area.controls.append(build_home())
        elif screen_name == "map":
            content_area.controls.append(build_map())
        elif screen_name == "run":
            content_area.controls.append(build_run())
        elif screen_name == "city":
            content_area.controls.append(build_city())
        elif screen_name == "profile":
            content_area.controls.append(build_profile())

        page.update()

    # Function called when user taps a nav button
    def nav_click(e):
        switch_screen(e.control.data)

    # Bottom navigation bar with 5 buttons
    nav_bar = ft.Row(
        controls=[
            ft.TextButton("🏠 Home",    data="home",    on_click=nav_click),
            ft.TextButton("🗺 Map",     data="map",     on_click=nav_click),
            ft.TextButton("🏃 Run",     data="run",     on_click=nav_click),
            ft.TextButton("🏰 City",    data="city",    on_click=nav_click),
            ft.TextButton("👤 Profile", data="profile", on_click=nav_click),
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    # Put everything on the page: content on top, nav bar at bottom
    page.add(
        ft.Column(
            controls=[content_area, nav_bar],
            expand=True,
        )
    )

    # Start on the home screen
    switch_screen("home")

ft.app(target=main, view=ft.AppView.FLET_APP)