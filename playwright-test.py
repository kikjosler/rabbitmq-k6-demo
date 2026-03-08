from playwright.async_api import async_playwright
import asyncio
import time

async def test_rabbitmq_queue():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)  # Медленно + видим
        page = await browser.new_page()
        
        print("Открываем RabbitMQ UI...")
        await page.goto("http://localhost:15672")
        
        # Универсальный способ — ждём любой input
        print("Ждём форму логин...")
        await page.wait_for_selector("input[type='text'], input", timeout=15000)
        
        # Логин по placeholder или label
        try:
            await page.fill("input[type='text'], input:first-child", "guest")
            await page.fill("input[type='password'], input:nth-child(2)", "guest")
        except:
            # Fallback — первый и второй input
            inputs = await page.query_selector_all("input")
            await inputs[0].fill("guest")
            await inputs[1].fill("guest")
        
        # Кнопка логин (любая кнопка или ссылка)
        await page.click("button, input[type='submit'], a:has-text('Login')")
        
        print("Ждём дашборд...")
        # Ждём любой текст интерфейса
        await page.wait_for_selector("body:has-text('Overview')", timeout=20000)
        print("Логин успешен!")
        
        # Скриншот дашборда
        await page.screenshot(path="rabbitmq-login-success.png")
        
        # Идём в Queues
        try:
            await page.click("text=Queues", timeout=5000)
            await page.wait_for_load_state("networkidle")
            
            # Проверяем очередь orders
            orders_count = await page.locator("text=orders").count()
            if orders_count > 0:
                print(f"Очередь 'orders' найдена! ({orders_count} штук)")
            else:
                print("Очередь orders пуста (запусти k6 тест)")
                
            await page.screenshot(path="rabbitmq-queues.png")
        except:
            print("Вкладка Queues не найдена — k6 тест ещё не запущен")
        
        print("Скриншоты: rabbitmq-login-success.png, rabbitmq-queues.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_rabbitmq_queue())
