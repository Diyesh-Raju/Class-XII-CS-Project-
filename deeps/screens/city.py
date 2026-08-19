import flet as ft

def build_city():
    # Dummy data - Student 1 will give us real values from server
    city_name   = "Bangalore"
    city_health = 75
    coins       = 500
    my_defenses = ["🧱 Stone Wall", "🗼 Watch Tower"]

    # Items in the shop
    shop_items = [
        {"name": "🧱 Stone Wall",   "cost": 100},
        {"name": "🗼 Watch Tower",   "cost": 200},
        {"name": "💣 Cannon",        "cost": 350},
        {"name": "🛡 Magic Shield",  "cost": 500},
    ]

    title       = ft.Text(f"🏰 {city_name}", size=28, color="#f5c518", weight=ft.FontWeight.BOLD)
    health_label = ft.Text(f"City Health: {city_health}%", size=14, color="#aaaaaa")
    health_bar   = ft.ProgressBar(value=city_health / 100, color="#4caf50", bgcolor="#333333", width=300)
    coins_text   = ft.Text(f"🪙 Your coins: {coins}", size=16, color="#f5c518")

    # Show current defenses
    defense_label = ft.Text("Your defenses:", size=14, color="#aaaaaa")
    defense_list  = ft.Text("  " + ",  ".join(my_defenses), size=13, color="white")

    # Message shown after buying
    buy_message = ft.Text("", size=13, color="#4caf50")

    shop_title = ft.Text("🛒 Defense Shop", size=20, color="white", weight=ft.FontWeight.BOLD)

    # Function called when user taps Buy
    def buy_item(e):
        item_name = e.control.data["name"]
        item_cost = e.control.data["cost"]
        buy_message.value = f"Bought {item_name} for {item_cost} coins! (dummy - no real deduction yet)"
        e.page.update()

    # Build one row per shop item
    shop_rows = []
    for item in shop_items:
        row = ft.Row(controls=[
            ft.Text(f"{item['name']}  —  {item['cost']} coins", size=13, color="white", expand=True),
            ft.ElevatedButton("Buy", data=item, on_click=buy_item, bgcolor="#f5c518", color="black"),
        ], width=320)
        shop_rows.append(row)

    return ft.Column(
        controls=[title, health_label, health_bar, coins_text, defense_label, defense_list,
                  ft.Divider(color="#333333"),
                  shop_title] + shop_rows + [buy_message],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        expand=True,
    )
