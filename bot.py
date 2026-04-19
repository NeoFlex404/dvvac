import requests
import time
import difflib

TOKEN = "8656408586:AAF7DDvVlBs2PC-XtdtR884Ym3kYoK4Q3aY"
CHAT_ID = "1936329519"

URL = "https://www.digitalcircus.movie/"

WATCHLIST = {
    "ukraine": "🇺🇦 Ukraine",
    "europe": "🌍 Europe",
    "russia": "🇷🇺 Russia",
    "belarus": "🇧🇾 Belarus",
    "kazakhstan": "🇰🇿 Kazakhstan",
    "poland": "🇵🇱 Poland",
    "germany": "🇩🇪 Germany"
}

last_content = None
first_check_done = False

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text[:4000]}  # ліміт Telegram
    )

send_message("Да працюю я, не лізь")

def clean_html(text):
    # трохи чистимо шум
    return text.replace("\n", "").replace("\t", "")

def extract_watchlist(text):
    text = text.lower()
    return {name for key, name in WATCHLIST.items() if key in text}

while True:
    try:
        response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        content = clean_html(response.text)

        current_watch = extract_watchlist(content)
        previous_watch = extract_watchlist(last_content or "")

        added_watch = current_watch - previous_watch

        if not first_check_done:
            send_message("Глянув я, нормально?")
            first_check_done = True

        else:
            # 🔥 ОСОБЛИВИЙ ТРИГЕР
            if added_watch:
                send_message("Ух єбать, збагачений уран!!!: " + ", ".join(added_watch))

            # 🔄 ЗВИЧАЙНИЙ DIFF
            elif last_content and content != last_content:

                diff = list(difflib.unified_diff(
                    last_content.split(),
                    content.split(),
                    lineterm=""
                ))

                changes = [line for line in diff if line.startswith("+") or line.startswith("-")]

                if changes:
                    msg = "Ось шо найшов:\n"
                    msg += "\n".join(changes[:50])
                    send_message(msg)
                else:
                    send_message("Шось таки є (Не багато)")

        last_content = content
        time.sleep(120)

    except Exception as e:
        print("Error:", e)
        time.sleep(120)
