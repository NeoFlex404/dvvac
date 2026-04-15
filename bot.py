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

send_message("Не лізь, я працюю")

last_content = None
first_check_done = False

# список країн які тебе цікавлять
WATCHLIST = {
    "ukraine": "🇺🇦 Ukraine",
    "europe": "🌍 Europe",
    "russia": "🇷🇺 Russia",
    "belarus": "🇧🇾 Belarus",
    "kazakhstan": "🇰🇿 Kazakhstan",
    "poland": "🇵🇱 Poland",
    "germany": "🇩🇪 Germany"
}

while True:
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        content = response.text.lower()

        # формуємо знайдені країни
        found = [name for key, name in WATCHLIST.items() if key in content]

        if last_content and content != last_content:
            if found:
                send_message("Ух єбать, збагачений уран?: " + ", ".join(found))
            else:
                send_message("Глянь ануно, тут шось нове")

        # після першої перевірки
        if not first_check_done:
            send_message("Глянув, нічого інтересного")
            first_check_done = True

        last_content = content
        time.sleep(120)

    except Exception as e:
        print("Error:", e)
        time.sleep(120)
