import asyncio
import difflib
import re
import time

import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

TOKEN = "8656408586:AAF7DDvVlBs2PC-XtdtR884Ym3kYoK4Q3aY"
CHAT_ID = "1936329519"

URL = "https://www.digitalcircus.movie/"

BASE_SLEEP = 300
BLOCKED_SLEEP = 900

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
        data={"chat_id": CHAT_ID, "text": text[:4000]}
    )


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text


def remove_noise_lines(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(
        line for line in lines
        if not any(pat.lower() in line.lower() for pat in NOISE_PATTERNS)
    )


def extract_useful_content(html: str) -> str | None:
    cleaned = clean_html(html)
    cleaned = remove_noise_lines(cleaned)
    if not cleaned or len(cleaned) < 50:
        return None
    return cleaned


def extract_watchlist(text: str) -> set:
    text = text.lower()
    return {name for key, name in WATCHLIST.items() if re.search(rf"\b{key}\b", text)}


async def fetch_page(url: str) -> str | None:
    """Завантажує сторінку через справжній браузер з JS-рендерингом."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-US",
            )
            page = await context.new_page()

            # Чекаємо поки мережа заспокоїться (JS завантажиться)
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Додатково чекаємо 2 секунди на динамічний контент
            await page.wait_for_timeout(2000)

            html = await page.content()
            await browser.close()
            return html

    except Exception as e:
        print(f"❌ Playwright error: {e}")
        return None


async def main():
    last_content = None
    first_check_done = False

    send_message("Да працюю я, не лізь")

    while True:
        try:
            print("🔁 New loop iteration")

            html = await fetch_page(URL)

            if not html:
                print("⚠️ Failed to fetch page")
                time.sleep(BASE_SLEEP)
                continue

            content = extract_useful_content(html)

            if not content:
                print("⚠️ No usable content")
                time.sleep(BASE_SLEEP)
                continue

            print(f"✅ Got content ({len(content)} chars)")

            current_watch = extract_watchlist(content)
            previous_watch = extract_watchlist(last_content or "")
            added_watch = current_watch - previous_watch

            if not first_check_done:
                send_message("Глянув я, нормально?")
                first_check_done = True
            else:
                if added_watch:
                    send_message("Ух єбать, збагачений уран!!!: " + ", ".join(added_watch))

                if last_content and content != last_content:
                    diff = list(difflib.unified_diff(
                        last_content.splitlines(),
                        content.splitlines(),
                        lineterm=""
                    ))
                    changes = [
                        line for line in diff
                        if (line.startswith("+") or line.startswith("-"))
                        and not (line.startswith("+++") or line.startswith("---"))
                    ]
                    if changes:
                        msg = "Ось шо найшов:\n" + "\n".join(changes[:50])
                        send_message(msg)
                    else:
                        send_message("Шось таки є (Не багато)")

            last_content = content

        except Exception as e:
            print(f"❌ Error: {e}")
            send_message(f"❌ Помилка: {e}")

        time.sleep(BASE_SLEEP)


if __name__ == "__main__":
    asyncio.run(main())
