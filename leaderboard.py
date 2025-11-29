from datetime import datetime, timezone, timedelta
from logging import info
import asyncio
from playwright.async_api import async_playwright
from config import config, LB_TTL

last_fetched = datetime.fromtimestamp(0, timezone.utc)
fetch_lock = asyncio.Lock()

async def fetch_images(ctx=None):
    global last_fetched

    if (datetime.now(timezone.utc) - last_fetched) < timedelta(seconds=LB_TTL):
        info("Using cached images")
        return
    
    if ctx is not None:
        await ctx.defer()

    # mutex the entire function so all simultaneous calls will wait on the one fetch
    async with fetch_lock:
        # check again in case it's been fetched in the meantime
        if (datetime.now(timezone.utc) - last_fetched) < timedelta(seconds=LB_TTL):
            info("Using cached images")
            return

        async with async_playwright() as p:
            pathToExtension = "./advent-of-code-charts/build"
            context = await p.chromium.launch_persistent_context(
                "./.browser_data",
                channel="chromium",
                args=[
                    '--enable-logging',
                    '--log-level=DEBUG',
                    '--log-file=./log.txt',
                    f"--disable-extensions-except={pathToExtension}",
                    f"--load-extension={pathToExtension}"
                ]
            )
        
            await context.add_cookies([{
                "name": "session",
                "value": config["AOC_SESSION_TOKEN"],
                "domain": ".adventofcode.com",
                "path": "/",
                "httpOnly": True,
                "secure": True
            }])

            page = await context.new_page()
            await page.goto(config["AOC_LB_URL"])

            # show everyone on podium
            if (await page.evaluate("localStorage.getItem('aoc-flag-v1-show-all');") != 'true'):
                await page.evaluate("localStorage.setItem('aoc-flag-v1-show-all', 'true');")
                await page.reload()

            # hide kick buttons
            await page.evaluate("document.querySelectorAll('.privboard-delbtn').forEach(el => el.hidden = true);")

            info("Loading Page")
            info(f"Loaded: {await page.title()}")
        
            # LB
            await page.locator("article > form").screenshot(path="./fetched_images/leaderboard.png")
            info("Got leaderboard")
            # Podium
            await page.locator("#aoc-extension-medals > table").screenshot(path="./fetched_images/podium.png")
            info("Got podium")
            # Graph
            await page.locator("canvas[title=\"Points over time per member.\"]").screenshot(path="./fetched_images/graph.png")
            info("Got graph")

            # Overview delta view
            await page.click("#aoc-extension-perDayLeaderBoard > h3 > a[data-key=\"overview\"]")
            await page.locator("#aoc-extension-perDayLeaderBoard > table[style*='display: table']").screenshot(path="./fetched_images/delta.png")
            info("Got delta overview")
            
            # Daily delta view
            for i in range(1, 26):
                if not await page.is_visible(f"#aoc-extension-perDayLeaderBoard > h3 > a[data-key=\"{i}\"]"):
                    break

                await page.click(f"#aoc-extension-perDayLeaderBoard > h3 > a[data-key=\"{i}\"]")
                await page.locator("#aoc-extension-perDayLeaderBoard > table[style*='display: table']").screenshot(path=f"./fetched_images/delta_day_{i}.png")
            info("Got daily deltas")

            await context.close()

        last_fetched = datetime.now(timezone.utc)


if __name__ == "__main__":
    asyncio.run(fetch_images())
