from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import threading
import time
import json
import requests

app = Flask(__name__)

BOT_TOKEN = "8379910934:AAGnipbcXU-Yo0tB44Ard9_58rzjvgmV3wE"
CHAT_ID = "7377945904"

live_matches = []
notified_matches = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)

def fetch_flashscore_live():
    global live_matches, notified_matches
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    while True:
        try:
            driver.get("https://www.flashscore.com/")
            time.sleep(5)

            matches = driver.find_elements(By.CSS_SELECTOR, ".event__match")
            updated = []

            for match in matches:
                try:
                    match_id = match.get_attribute("id")
                    home = match.find_element(By.CSS_SELECTOR, ".event__participant--home").text
                    away = match.find_element(By.CSS_SELECTOR, ".event__participant--away").text
                    score_home = match.find_element(By.CSS_SELECTOR, ".event__score--home").text
                    score_away = match.find_element(By.CSS_SELECTOR, ".event__score--away").text
                    minute = match.find_element(By.CSS_SELECTOR, ".event__stage--block").text.replace("'", "")

                    score_home = int(score_home) if score_home.isdigit() else 0
                    score_away = int(score_away) if score_away.isdigit() else 0
                    minute = int(minute) if minute.isdigit() else 0

                    total_corners = 0  # Placeholder
                    yellow_cards = 0   # Placeholder
                    goal_diff = score_away - score_home

                    conditions = []
                    if total_corners >= 13:
                        conditions.append("13+ szöglet")
                    if goal_diff == 1:
                        conditions.append("hazai hátrány")
                    if yellow_cards > 0:
                        conditions.append("sárga lap")

                    if conditions and match_id not in notified_matches:
                        notified_matches.add(match_id)
                        msg = f"⚽ {home} vs {away}\n⏱ {minute}. perc | Állás: {score_home}-{score_away}\n"
                        msg += f"Feltételek: {', '.join(conditions)}"
                        send_telegram_message(msg)

                    updated.append({
                        "home": home,
                        "away": away,
                        "minute": minute,
                        "score": f"{score_home}-{score_away}",
                        "corners": total_corners,
                        "yellow": yellow_cards
                    })

                except Exception:
                    continue

            live_matches = updated

        except Exception as e:
            print("Selenium hiba:", e)

        time.sleep(60)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/matches")
def api_matches():
    return jsonify(live_matches)

threading.Thread(target=fetch_flashscore_live, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
