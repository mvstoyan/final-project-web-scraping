import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(options=options)

def scrape_all_years(driver, start_url):
    driver.get(start_url)
    time.sleep(2)

    year_links = driver.find_elements(By.CSS_SELECTOR, "table a[href*='year']")  # adjust selector
    years = {link.text.strip(): link.get_attribute("href") for link in year_links}
    print(f"Found {len(years)} years to scrape.")

    for year, link in years.items():
        scrape_year(driver, year, link)

def scrape_year(driver, year, url):
    output_path = os.path.join(OUTPUT_DIR, f"mlb_almanac_{year}.csv")
    if os.path.exists(output_path):
        print(f"Already scraped {year}, skipping.")
        return

    print(f"Scraping MLB Almanac data for {year}...")
    driver.get(url)
    time.sleep(2)

    rows = []
    try:
        table = driver.find_element(By.CSS_SELECTOR, "table")  # adjust to correct table
        for tr in table.find_elements(By.TAG_NAME, "tr"):
            cells = tr.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            rows.append([cell.text.strip() for cell in cells])
    except NoSuchElementException:
        print(f"No data table found for {year}.")
        return

    header = [th.text.strip() for th in driver.find_elements(By.CSS_SELECTOR, "table tr th")]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header if header else [f"col{i+1}" for i in range(len(rows[0]))])
        writer.writerows(rows)
    print(f"Saved data to {output_path}.")

def main():
    START_URL = "https://www.baseball-almanac.com/yearmenu.shtml"
    driver = init_driver()
    try:
        scrape_all_years(driver, START_URL)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()