"""
Automate high-resolution screenshots of SignBridge AI in Light Theme and Dark Theme
using Chrome DevTools Protocol (CDP) via Python asyncio and websockets.
"""

import asyncio
import json
import os
import subprocess
import time
import urllib.request
import base64
from pathlib import Path
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = Path(r"d:\Projects\SignBridge\Final_Report_Deliverables\Project_Screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def send_cmd(ws, method, params=None, req_id=1):
    msg = {"id": req_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == req_id:
            return data.get("result", {})

async def capture_all():
    port = 9222
    temp_profile = Path(r"d:\Projects\SignBridge\Final_Report_Deliverables\Supporting_Files\chrome_temp_profile")
    temp_profile.mkdir(parents=True, exist_ok=True)

    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={temp_profile}",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1366,850",
        "http://localhost:3000"
    ]

    print("Launching Chrome headless process...")
    proc = subprocess.Popen(cmd)
    time.sleep(3)

    try:
        req = urllib.request.urlopen(f"http://localhost:{port}/json")
        targets = json.loads(req.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]
        print(f"Connected to page target: {ws_url}")

        async with websockets.connect(ws_url, max_size=100*1024*1024) as ws:
            # Enable Page and Runtime
            await send_cmd(ws, "Page.enable", req_id=1)
            await send_cmd(ws, "Runtime.enable", req_id=2)

            async def click_tab(label_text):
                js = f"""
                (() => {{
                    const btns = Array.from(document.querySelectorAll('nav button'));
                    const target = btns.find(b => b.textContent.includes('{label_text}'));
                    if (target) {{ target.click(); return true; }}
                    return false;
                }})()
                """
                await send_cmd(ws, "Runtime.evaluate", {"expression": js}, req_id=10)
                await asyncio.sleep(1.2)

            async def set_theme(theme_mode):
                js = f"""
                (() => {{
                    localStorage.setItem('sb_theme', '{theme_mode}');
                    if ('{theme_mode}' === 'dark') {{
                        document.documentElement.classList.add('dark');
                    }} else {{
                        document.documentElement.classList.remove('dark');
                    }}
                }})()
                """
                await send_cmd(ws, "Runtime.evaluate", {"expression": js}, req_id=20)
                await asyncio.sleep(0.8)

            async def take_screenshot(filename):
                res = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, req_id=30)
                b64 = res.get("data", "")
                if b64:
                    out_path = OUTPUT_DIR / filename
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(b64))
                    print(f"Saved screenshot: {filename} ({out_path.stat().st_size} bytes)")

            # 1. Dashboard Dark
            print("Capturing Dashboard (Dark)...")
            await set_theme("dark")
            await click_tab("Dashboard")
            await take_screenshot("dashboard_dark.png")

            # 2. Dashboard Light
            print("Capturing Dashboard (Light)...")
            await set_theme("light")
            await take_screenshot("dashboard_light.png")

            # 3. Live Translator Light
            print("Capturing Live Translator (Light)...")
            await click_tab("Live Translator")
            await take_screenshot("live_translator_light.png")

            # 4. Live Translator Dark
            print("Capturing Live Translator (Dark)...")
            await set_theme("dark")
            await take_screenshot("live_translator_dark.png")

            # 5. Text to Sign Light
            print("Capturing Text to Sign (Light)...")
            await set_theme("light")
            await click_tab("Text to Sign")
            await take_screenshot("text_to_sign_light.png")

            # 6. Text to Sign Dark
            print("Capturing Text to Sign (Dark)...")
            await set_theme("dark")
            await take_screenshot("text_to_sign_dark.png")

            # 7. Vocabulary (109) Light
            print("Capturing Vocabulary 109 (Light)...")
            await set_theme("light")
            await click_tab("Vocabulary")
            await take_screenshot("vocab_catalog_light.png")

            # 8. Vocabulary (109) Dark
            print("Capturing Vocabulary 109 (Dark)...")
            await set_theme("dark")
            await take_screenshot("vocab_catalog_dark.png")

            # 9. Settings Light
            print("Capturing Settings (Light)...")
            await set_theme("light")
            await click_tab("Settings")
            await take_screenshot("settings_light.png")

            # 10. Model Admin Dark
            print("Capturing Model Admin (Dark)...")
            await set_theme("dark")
            await click_tab("Model Admin")
            await take_screenshot("admin_dark.png")

    finally:
        proc.terminate()
        print("Chrome process terminated.")

if __name__ == "__main__":
    asyncio.run(capture_all())
