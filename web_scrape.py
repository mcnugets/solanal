from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time


def setup_driver():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def fetch_coin_data():
    driver = setup_driver()
    try:
        # Navigate to the page
        url = "https://pump.fun/advanced"
        driver.get(url)

        # Wait for rows to load
        wait = WebDriverWait(driver, 30)  # Increased timeout
        try:
            rows = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr"))
            )
        except TimeoutException:
            print("Table rows not found or took too long to load.")
            return []

        # Extract data
        coins_data = []

        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:  # Check if 'cols' is not empty
                    coins_data.append(
                        {
                            "coin_name": cols[0].text.strip(),
                            "market_cap": cols[1].text.strip(),
                            "volume": cols[2].text.strip(),
                            "other_data": [col.text.strip() for col in cols[3:]],
                        }
                    )
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        return coins_data

    except Exception as e:
        print(f"Error extracting table data: {e}")
        return []

    finally:
        driver.quit()


if __name__ == "__main__":
    results = fetch_coin_data()
    print(f"Found {len(results)} coins:")
    for coin in results:
        print(coin)
