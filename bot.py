import requests
import time
import difflib
from bs4 import BeautifulSoup
import re

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

NOISE_PATTERNS = [
    "wix-essential-viewer-model",
    "thunderbolt",
    "viewerModel",
    "static.parastorage.com",
    "siteAssets",
    "fleetConfig",
    "componentsLibrariesTopology",
    "ssr",
    "experiments"
]

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # видаляємо шумні теги
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    # прибираємо зайві пробіли
    text = re.sub(r"\s+", " ", text)

    return text


def is_noise(text: str) -> bool:
    text_lower = text.lower()
    return any(pat.lower() in text_lower for pat in NOISE_PATTERNS)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,uk;q=0.8",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

def extract_useful_content(html: str) -> str | None:
    cleaned = clean_html(html)

    # якщо це технічний Wix-мусор — ігноруємо
    if is_noise(cleaned):
        return None

    return cleaned

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
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 429:
            print("429 Too Many Requests — чекаю довше...")
            time.sleep(600)  # 10 хв
            continue
        content = extract_useful_content(response.text)

        if content is None:
            continue

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
        time.sleep(180)

    except Exception as e:
        print("Error:", e)
        time.sleep(180)
