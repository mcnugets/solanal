from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Initialize Selenium WebDriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode for performance
driver = webdriver.Chrome(service=service, options=options)

# Open the website
url = "https://pump.fun/advanced"
driver.get(url)

# Wait for the dynamic content to load
wait = WebDriverWait(driver, 10)
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "tbody[data-testid='virtuoso-item-list']")
    )
)

# Locate the table
table = driver.find_element(By.CSS_SELECTOR, "tbody[data-testid='virtuoso-item-list']")

# Extract table headers
headers = [header.text for header in table.find_elements(By.TAG_NAME, "th")]

# Extract table rows
rows = table.find_elements(By.TAG_NAME, "tr")
data = []
for row in rows[1:]:  # Skip header row
    cols = row.find_elements(By.TAG_NAME, "td")
    data.append([col.text for col in cols])

# Close the browser
driver.quit()

# Create a Pandas DataFrame
df = pd.DataFrame(data, columns=headers)

# Clean and Filter Data
df = df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"))
# df = df[
#     ["coin_name", "coin_address", "coin_market_cap", "coin_volume"]
# ]  # Filter relevant columns

# Save to CSV for further processing
df.to_csv("coin_data.csv", index=False)

print("Scraping complete. Data saved to 'coin_data.csv'.")
