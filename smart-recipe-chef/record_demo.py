import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

FRONTEND_URL = "https://smart-recipe-chef-frontend-1046395960831.us-east1.run.app"
ARTIFACTS_DIR = Path("/config/.gemini/antigravity/brain/e51639ab-b7a9-4277-9160-9b9d9768e0e6")
TEMP_VIDEO_DIR = Path("./temp_demo_video")

async def record_demo():
    TEMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(TEMP_VIDEO_DIR),
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print(f"Opening {FRONTEND_URL}...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 1. First Prompt: Find pasta recipes (tests global recipe search tool)
        prompt1 = "Find pasta recipes with garlic and olive oil"
        print(f"Sending Prompt 1: {prompt1}")
        await page.fill("#input", prompt1)
        await page.click("form button")

        # Wait for agent response to Prompt 1
        print("Waiting for Agent response to Prompt 1...")
        await page.wait_for_selector(".msg-row.agent:nth-of-type(2) .bubble:not(:has-text('…'))", timeout=60000)
        await page.wait_for_timeout(4000)

        # 2. Second Prompt: Generate dish photo / video
        prompt2 = "Generate a photo of a gourmet Margherita pizza"
        print(f"Sending Prompt 2: {prompt2}")
        await page.fill("#input", prompt2)
        await page.click("form button")

        print("Waiting for Agent response to Prompt 2...")
        await page.wait_for_selector(".msg-row.agent:nth-of-type(4) .bubble:not(:has-text('…'))", timeout=90000)
        await page.wait_for_timeout(6000)

        # Close page and context to finalize video recording
        video_path_obj = await page.video.path()
        await page.close()
        await context.close()
        await browser.close()

        target_path = ARTIFACTS_DIR / "smart_recipe_chef_demo.webm"
        if video_path_obj and os.path.exists(video_path_obj):
            shutil.copy(video_path_obj, target_path)
            print(f"Demo video successfully saved to {target_path}")
            return str(target_path)
        else:
            print("Video path not found!")
            return None

if __name__ == "__main__":
    asyncio.run(record_demo())
