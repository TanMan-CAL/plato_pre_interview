import asyncio
import json
import logging
import os
from typing import List, Dict, Any

from scrapybara import Scrapybara
from undetected_playwright.async_api import async_playwright


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_scrapybara_browser():
    """ Creates a browser instance on a Scrapybara machine """
    api_key = os.getenv("SCRAPYBARA_API_KEY")
    if not api_key:
        raise ValueError("SCRAPYBARA_API_KEY environment variable not set")
    
    client = Scrapybara(api_key=api_key)
    browser = client.start_browser()
    logger.info("Scrapybara browser runs!")
    return browser

async def retrieve_menu_items(instance, start_url: str) -> list[dict]:
    """
    :args:
    instance: the scrapybara instance to use
    url: the initial url to navigate to
    
    :desc:
    this function navigates to {url}. then, it will collect the detailed data for each menu item
    in the store and return it. (hint: click a menu item, open dev tools -> network tab -> 
    filter for "https://www.doordash.com/graphql/itemPage?operation=itemPage")
    one way to do this is to scroll through the page and click on each menu item.
    determine the most efficient way to collect this data.
    
    :returns:
    a list of menu items on the page, represented as dictionaries
    """
    cdp_url = instance.get_cdp_url().cdp_url
    
    menu_items = []
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        context = await browser.new_context()
        page = await context.new_page()
        
        async def capture_item_data(response): # navigate to the url as per instruction
            if "graphql/itemPage?operation=itemPage" in response.url:
                try:
                    data = await response.json()
                    if data.get("data") and data["data"].get("itemPage"):
                        menu_items.append(data["data"]["itemPage"])
                except Exception as e:
                    print(f"Error processing response: {e}")
        
        page.on("response", capture_item_data)
        
        await page.goto(start_url)
        await page.wait_for_load_state("networkidle")
        
        try:
            cookie_button = page.locator('button:has-text("Accept All")')
            if await cookie_button.is_visible(timeout=5000):
                await cookie_button.click()
        except:
            pass
        
        # scroll
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        
        # finding MenuItem only
        cards = page.locator('[data-anchor-id^="MenuItem"]')
        count = await cards.count()
        
        # each item for a graphql req
        for i in range(count):
            try:
                item = page.locator('[data-anchor-id^="MenuItem"]').nth(i)
                await item.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
                
                await item.click()
                await page.wait_for_timeout(1000)
                
                close = page.locator('button[aria-label="Close"]').first
                await close.click()
                await page.wait_for_timeout(500)
                
            except Exception as e:
                print(f"Error with menu item {i+1}: {e}")
        
        return menu_items
    
async def main():
    try:
        browser = await get_scrapybara_browser()
        logger.info("Starting to search for items")
        
        stuff = await retrieve_menu_items(
            browser,
            "https://www.doordash.com/store/panda-express-san-francisco-980938/12722988/?event_type=autocomplete&pickup=false",
        )
        
        logger.info("Done scraping")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
    finally:
        if 'browser' in locals():
            browser.stop()
            logger.info("Scrapybara browser instance stopped")

if __name__ == "__main__":
    asyncio.run(main())
