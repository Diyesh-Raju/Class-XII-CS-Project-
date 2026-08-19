import flet as ft

def build_profile():
    # Dummy data - Student 1 will send real player data later
    player_name   = "Player1"
    level         = 5
    total_km      = 42.3
    cities_owned  = ["Bangalore", "Mysore"]
    attacks_won   = 3
    attacks_lost  = 1

    title = ft.Text("👤 Profile", size=28, color="#f5c518", weight=ft.FontWeight.BOLD)

    name_text  = ft.Text(f"Username: {player_name}", size=16, color="white")
    level_text = ft.Text(f"Level: {level}", size=16, color="white")
    km_text    = ft.Text(f"Total distance run: {total_km} km", size=16, color="white")

    cities_text = ft.Text(
        "Cities owned: " + ", ".join(cities_owned),
        size=14, color="#aaaaaa"
    )

    attack_text = ft.Text(
        f"Attacks won: {attacks_won}   |   Attacks lost: {attacks_lost}",
        size=14, color="#aaaaaa"
    )

    # Logout button - just shows a message for now
    def logout(e):
        logout_msg.value = "Logged out! (dummy - no real logout yet)"
        e.page.update()

    logout_btn = ft.OutlinedButton("Logout", on_click=logout, width=200)
    logout_msg = ft.Text("", size=13, color="#ff6666")

    return ft.Column(
        controls=[title, name_text, level_text, km_text, cities_text, attack_text,
                  ft.Divider(color="#333333"),
                  logout_btn, logout_msg],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        expand=True,
    )
