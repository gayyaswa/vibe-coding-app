"""Generate docs/demo.gif by screenshotting every tab of the Streamlit app."""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).parent.parent
APP_URL = "http://localhost:8501"
OUTPUT = ROOT / "docs" / "demo.gif"

TABS = [
    "Portfolio Overview",
    "Allocation Dashboard",
    "Rebalancing Engine",
    "Sector Breakdown",
    "Gain / Loss",
    "AI Insights",
]

# Milliseconds each frame is shown in the GIF
FRAME_DURATION_MS = 2500


def wait_for_server(url: str, timeout: int = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"Server ready at {url}")
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Server at {url} did not become ready within {timeout}s")


def capture_screenshots(proc: subprocess.Popen) -> list[Image.Image]:
    images: list[Image.Image] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(APP_URL, wait_until="networkidle")

        # Give Streamlit's initial render time to settle
        page.wait_for_timeout(3000)

        for tab_name in TABS:
            print(f"  Capturing: {tab_name}")
            # Click the tab by its visible text
            tab = page.get_by_role("tab", name=tab_name)
            tab.click()
            page.wait_for_timeout(1500)

            png_bytes = page.screenshot(full_page=False)
            from io import BytesIO
            img = Image.open(BytesIO(png_bytes)).convert("RGBA")
            images.append(img)

        browser.close()

    return images


def stitch_gif(images: list[Image.Image], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = [img.convert("P", palette=Image.ADAPTIVE) for img in images]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
    )


def main() -> None:
    print("Starting Streamlit app …")
    env = os.environ.copy()
    # Suppress Streamlit's welcome message and analytics prompts
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.headless", "true",
         "--server.port", "8501"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_server(APP_URL)
        print(f"Capturing {len(TABS)} tabs …")
        images = capture_screenshots(proc)
    finally:
        proc.terminate()
        proc.wait()

    print(f"Stitching GIF → {OUTPUT}")
    stitch_gif(images, OUTPUT)

    size_kb = OUTPUT.stat().st_size // 1024
    print(f"Done: {OUTPUT}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
