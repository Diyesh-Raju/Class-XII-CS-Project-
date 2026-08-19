import flet as ft
import threading
import time

def build_run():
    # These will later come from Student 3's GPS module
    distance_km = 0.0
    is_running = False
    seconds_elapsed = 0

    # Labels that update as the run goes
    distance_text = ft.Text("0.00 km", size=48, color="#4caf50", weight=ft.FontWeight.BOLD)
    time_text     = ft.Text("00:00", size=24, color="white")
    coins_preview = ft.Text("🪙 Coins you'll earn: 0", size=16, color="#f5c518")

    title = ft.Text("🏃 Start Your Run", size=28, color="#f5c518", weight=ft.FontWeight.BOLD)

    # A simple timer that counts up every second while running
    def run_timer(page_ref):
        nonlocal seconds_elapsed, distance_km, is_running
        while is_running:
            time.sleep(1)
            seconds_elapsed += 1

            # Dummy: pretend user runs 0.01 km every second
            # Student 3 will replace this with real GPS distance
            distance_km += 0.01

            mins = seconds_elapsed // 60
            secs = seconds_elapsed % 60
            distance_text.value = f"{distance_km:.2f} km"
            time_text.value     = f"{mins:02}:{secs:02}"
            coins_preview.value = f"🪙 Coins you'll earn: {int(distance_km * 100)}"

            try:
                page_ref.update()
            except:
                break

    # Start button pressed
    def start_run(e):
        nonlocal is_running
        is_running = True
        start_btn.visible = False
        stop_btn.visible  = True
        e.page.update()

        # Run the timer in a background thread so the app doesn't freeze
        t = threading.Thread(target=run_timer, args=(e.page,))
        t.daemon = True
        t.start()

    # Stop button pressed
    def stop_run(e):
        nonlocal is_running
        is_running = False
        start_btn.visible = True
        stop_btn.visible  = False
        result_text.value = f"✅ Run saved! You earned {int(distance_km * 100)} coins."
        e.page.update()

    start_btn  = ft.ElevatedButton("▶ Start Run",  on_click=start_run, bgcolor="#4caf50", color="white", width=220)
    stop_btn   = ft.ElevatedButton("⏹ Stop Run",   on_click=stop_run,  bgcolor="#f44336", color="white", width=220, visible=False)
    result_text = ft.Text("", size=14, color="#4caf50")

    return ft.Column(
        controls=[title, distance_text, time_text, coins_preview, start_btn, stop_btn, result_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True,
    )
