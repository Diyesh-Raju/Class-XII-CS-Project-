import flet as ft

def build_home():
    # Dummy data - later Student 1 will send us real numbers from the server
    player_name = "Player1"
    coins = 500
    city_health = 80
    active_quest = "Run 5km to reclaim Mysore City"
    deadline = "2h 30m left"

    # Title text at the top
    title = ft.Text("⚔️ RunCraft", size=32, color="#f5c518", weight=ft.FontWeight.BOLD)

    # Show player name and coins
    stats = ft.Text(f"👤 {player_name}   |   🪙 {coins} coins", size=16, color="white")

    # City health shown as a progress bar
    health_label = ft.Text(f"🏰 City Health: {city_health}%", size=14, color="#aaaaaa")
    health_bar = ft.ProgressBar(value=city_health / 100, color="#4caf50", bgcolor="#333333", width=300)

    # Active quest box
    quest_box = ft.Container(
        content=ft.Column(controls=[
            ft.Text("📜 Active Quest", size=14, color="#f5c518"),
            ft.Text(active_quest, size=13, color="white"),
            ft.Text(f"⏰ {deadline}", size=12, color="#ff6666"),
        ]),
        bgcolor="#1a1a1a",
        border_radius=10,
        padding=15,
        width=320,
    )

    # Put it all together in a column
    return ft.Column(
        controls=[title, stats, health_label, health_bar, quest_box],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True,
    )
