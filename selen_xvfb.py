import asyncio
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display


async def cielo_scrap(wallet_address):
    display = Display(visible=0, size=(1280, 720))
    display.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')


    profile_path = "/root/.config/google-chrome/metamask_profile"

    options.add_argument(f"user-data-dir={profile_path}")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 5)
    driver.get(f"https://app.cielo.finance/profile/{wallet_address}?timeframe=1d&tab=tokenpnl&sortBy=trades_desc")

    print(driver.title)

    await asyncio.sleep(3)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div[4]/div/div")))
        html_daily_trades = driver.page_source
    except:
        html_daily_trades = "No daily trades"
        print(html_daily_trades)

    driver.get(f"https://app.cielo.finance/profile/{wallet_address}?timeframe=7d&tab=tokenpnl&sortBy=trades_desc")
    await asyncio.sleep(2)

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div[4]/div/div")))
        html_weekly_trades = driver.page_source
    except:
        html_weekly_trades = "No weekly trades"
        print(html_weekly_trades)

    driver.get(f"https://app.cielo.finance/profile/{wallet_address}?timeframe=30d&tab=tokenpnl&sortBy=trades_desc")
    await asyncio.sleep(2)

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div[4]/div/div")))
        html_monthly_trades = driver.page_source
    except:
        html_monthly_trades = "No monthly trades"
        print(html_monthly_trades)

    driver.quit()
    display.stop()

    # with open("html.txt", "w") as file:
    #     file.write(html_weekly_trades)

    return html_daily_trades, html_weekly_trades, html_monthly_trades


async def rugcheck_scrap(contract_address):
    display = Display(visible=0, size=(1280, 720))
    display.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')


    profile_path = "/root/.config/google-chrome/metamask_profile"
    options.add_argument(f"user-data-dir={profile_path}")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 5)
    driver.get(f'https://rugcheck.xyz/tokens/{contract_address}')

    print(driver.title)

    await asyncio.sleep(5)


    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[1]/section/div/div[2]")))
    except:
        pass

    html = driver.page_source

    driver.quit()
    display.stop()

    # with open("html.txt", "w", encoding="utf-8") as file:
    #     file.write(html)

    return html
