import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 720, "height": 900})
        await page.goto("file:///c:/Users/Administrator/projects/WuHuaMiXin/part_4_Strategy_Sim/strategy_card.html")
        await page.wait_for_timeout(600)
        height = await page.evaluate("document.body.scrollHeight")
        await page.set_viewport_size({"width": 720, "height": int(height)})
        await page.screenshot(
            path="c:/Users/Administrator/projects/WuHuaMiXin/part_4_Strategy_Sim/strategy_card.png",
            full_page=True
        )
        await browser.close()
        print("done", height)

asyncio.run(main())
