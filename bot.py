import requests
import time

TOKEN = "8656408586:AAF7DDvVlBs2PC-XtdtR884Ym3kYoK4Q3aY"
CHAT_ID = "1936329519"

URL = "https://www.digitalcircus.movie/"

last_content = None
first_check_done = False

WATCHLIST = {
    "ukraine": "🇺🇦 Ukraine",
    "europe": "🌍 Europe",
    "russia": "🇷🇺 Russia",
    "belarus": "🇧🇾 Belarus",
    "kazakhstan": "🇰🇿 Kazakhstan",
    "poland": "🇵🇱 Poland",
    "germany": "🇩🇪 Germany"
}

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

def extract_countries(text):
    text = text.lower()
    return {name for key, name in WATCHLIST.items() if key in text}

def diff_score(a, b):
    return len(a.symmetric_difference(b))

send_message("Да працюю я, не лізь")

while True:
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        content = response.text

        current = extract_countries(content)
        previous = extract_countries(last_content or "")

        added = current - previous
        removed = previous - current
        changes = diff_score(current, previous)

        if not first_check_done:
            send_message("👀 Перша перевірка завершена")
            first_check_done = True

        else:
            # 🟢 РІВЕНЬ 1 — важливі країни
            if added:
                send_message("Ух єбать, збагачений уран: " + ", ".join(added))

            # 🟡 РІВЕНЬ 2 — великі зміни
            elif changes >= 3:
                msg = "Шось інтересне, глянь:\n"

                if added:
                    msg += "➕ Додано: " + ", ".join(added) + "\n"
                if removed:
                    msg += "➖ Видалено: " + ", ".join(removed)

                send_message(msg)

            # 🔴 РІВЕНЬ 3 — нічого важливого
            else:
                pass

        last_content = content
        time.sleep(120)

    except Exception as e:
        print("Error:", e)
        time.sleep(120)
