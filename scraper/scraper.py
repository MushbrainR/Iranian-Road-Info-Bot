import json
import re
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

ROAD_INFO_URL = "ROAD_INFO_URL" # you can use the url of the official website

def get_last_update(soup, data_list):
    try:
        update = soup.find('h6', class_="sub-categori-news")
        if update:
            update_data = re.findall(r'\((.*?)\)', update.text)[0]
            logging.info(f"Last update found: {update_data}")
            data_list.append(update_data)
            save_data(data_list)
        else:
            logging.warning("Could not find the last update.")
    except (AttributeError, IndexError) as e:
        logging.error(f"Error extracting last update: {e}")


def get_road_names(road_info_list):
    road_names = []
    try:
        for line in road_info_list:
            words = line.split()
            targets = ['آزادراه', 'محور', 'جاده']
            for i in range(len(words) - 1):
                for target in targets:
                    if words[i] == target:
                        if len(words) > i + 2 and words[i + 2] == '–':  # Check for correct dash character
                            road_names.append(f'{target} {words[i + 1]} – {words[i + 3]}')
                        elif len(words[i + 1]) >= 3:
                            road_names.append(f'{target} {words[i + 1]}')
        logging.info(f"Extracted road names: {road_names}")
    except IndexError as e:
        logging.error(f"Error processing road names: {e}")
    return road_names


def get_road_data(soup, data_list, element):
    try:
        data = {}
        roads_information = soup.find_all('div', class_=element)
        if not roads_information:
            logging.warning(f"No road information found for element class: {element}")
            return

        for road_info in roads_information:
            road_info_list = road_info.text.splitlines()
            road_names = get_road_names(road_info_list)
            for item in road_info_list:
                for road in road_names:
                    if road in item:
                        data[road] = item
                    else:
                        data['(اطلاعات دیگر)'] = item
        logging.info(f"Road data extracted: {data}")
        data_list.append(data)
        save_data(data_list)
    except Exception as e:
        logging.error(f"Error extracting road data: {e}")


def get_road_closures(soup, data_list):
    try:
        roads_information = soup.find_all('div', class_='last-state-block mb-2')
        if not roads_information:
            logging.warning("No road closure information found.")
            return

        for road_info in roads_information:
            logging.info(f"Road closure information: {road_info.text}")
            data_list.append(road_info.text)
            save_data(data_list)
    except Exception as e:
        logging.error(f"Error extracting road closures: {e}")


def save_data(data):
    try:
        with open('data/data.json', 'w') as file:
            json.dump(data, file, indent=4)
        logging.info("Data successfully saved to data.json")
    except IOError as e:
        logging.error(f"Error saving data to file: {e}")


def create_webdriver():
    options = Options()
    options.headless = True  # Run the browser in headless mode
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)  # Set a timeout for page loading
        logging.info("WebDriver successfully initialized.")
        return driver
    except WebDriverException as e:
        logging.error(f"Error initializing WebDriver: {e}")
        return None


def main():
    max_retries = 5  # Maximum number of retries before quitting
    retry_count = 0
    wait_time = 30  # Initial wait time in seconds (for retry backoff)
    max_wait_time = 1800  # Maximum wait time (30 minutes)
    driver = None  # Initialize driver to None to avoid referencing it before assignment

    while True:
        try:
            logging.info("Starting data scraping loop...")

            # Create WebDriver
            driver = create_webdriver()
            if not driver:
                raise Exception("Failed to initialize WebDriver.")

            driver.get(ROAD_INFO_URL)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            data_list = []

            # Extract last update information
            get_last_update(soup, data_list)

            # Extract road data for different elements
            elements = ['last-state-news-body-north-append d-flex flex-column',
                        'last-state-news-body-extra last-status-news-style my-4 p-3']
            for element in elements:
                get_road_data(soup, data_list, element)

            # Extract road closure information
            get_road_closures(soup, data_list)

            # Reset retry count after successful scraping
            retry_count = 0
            wait_time = 30  # Reset wait time to the initial value

            # Wait for the next cycle (30 minutes)
            time_wait_minutes = 5
            logging.info(f"Sleeping for {time_wait_minutes} minutes before the next scrape...")
            time.sleep(time_wait_minutes * 60)

        except (TimeoutException, NoSuchElementException, WebDriverException, Exception) as e:
            logging.error(f"An error occurred: {e}")
            retry_count += 1

            # Retry with exponential backoff
            if retry_count <= max_retries:
                logging.info(f"Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, max_wait_time)  # Exponential backoff
            else:
                logging.error(f"Max retries ({max_retries}) exceeded. Exiting.")
                break  # Exit the loop after too many retries

        finally:
            # Close the driver if it exists
            if driver:
                driver.quit()
                driver = None  # Reset the driver to None after quitting




if __name__ == '__main__':
    main()