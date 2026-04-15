import requests
import time

TOKEN = "8656408586:AAF7DDvVlBs2PC-XtdtR884Ym3kYoK4Q3aY"
CHAT_ID = "1936329519"

URL = "https://www.digitalcircus.movie/"

last_content = ""

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

send_message("✅ Бот запущений")

while True:
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        content = response.text

        if last_content and content != last_content:
            if "Ukraine" in content or "Europe" in content:
                send_message("🇺🇦🔥 МОЖЛИВО КВИТКИ!")
            else:
                send_message("🔄 Сайт оновився")

        last_content = content
        time.sleep(120)

    except Exception as e:
        print("Error:", e)
        time.sleep(120)
