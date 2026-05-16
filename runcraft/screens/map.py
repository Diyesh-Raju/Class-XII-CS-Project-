import flet as ft

def build_map():
    # List of cities - later Student 4 will tell us which are locked/unlocked
    cities = [
        {"name": "Bangalore",  "unlocked": True,  "emoji": "🏙"},
        {"name": "Mysore",     "unlocked": True,  "emoji": "🏰"},
        {"name": "Chennai",    "unlocked": False, "emoji": "🔒"},
        {"name": "Hyderabad",  "unlocked": False, "emoji": "🔒"},
        {"name": "Mumbai",     "unlocked": False, "emoji": "🔒"},
    ]

    title = ft.Text("🗺 World Map", size=28, color="#f5c518", weight=ft.FontWeight.BOLD)
    subtitle = ft.Text("Tap a city to travel or attack", size=13, color="#aaaaaa")

    # Function that runs when user taps a city button
    def city_tapped(e):
        city_name = e.control.data
        print(f"Tapped city: {city_name}")   # later this will open attack/travel screen

    # Build one button for each city
    city_buttons = []
    for city in cities:
        color = "#f5c518" if city["unlocked"] else "#555555"
        btn = ft.ElevatedButton(
            text=f"{city['emoji']}  {city['name']}",
            data=city["name"],
            on_click=city_tapped,
            bgcolor="#1a1a1a",
            color=color,
            width=280,
        )
        city_buttons.append(btn)

    return ft.Column(
        controls=[title, subtitle] + city_buttons,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
        expand=True,
    )
