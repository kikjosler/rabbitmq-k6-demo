from playwright.async_api import async_playwright
import asyncio


async def test_rabbitmq_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # RabbitMQ Management UI
        await page.goto("http://localhost:15672")
        await page.fill("input[name='user']", "guest")
        await page.fill("input[name='pwd']", "guest")
        await page.click("button:has-text('Log in')")

        # Проверяем очередь orders
        await page.wait_for_selector("text=orders")
        queue_count = await page.locator("text=orders").count()
        assert queue_count > 0, "Orders queue not found!"

        messages = await page.locator("td:has-text('order-')").count()
        print(f"✅ Found {messages} orders in RabbitMQ!")

        await browser.close()


asyncio.run(test_rabbitmq_ui())
