import os
import time
import json
import logging
import itertools

from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright

HEADERS = [
    'STATION_CODE',
    'STATION_NAME',
    'STATE',
    'NAME2'
]
OUT_FILE_NAME = 'out.csv'

def write_to_csv(data, filename=OUT_FILE_NAME):
    if len(data) == 0:
        return
    df = pd.DataFrame(data)
    df.columns = HEADERS
    with open(filename, "a", newline="", encoding="utf-8") as f:
        write_header = f.tell() == 0  # Check if the file is empty
        df.to_csv(f, index=False, header=write_header)

CONFIG_FILE = 'conf.bin'
def get_last_comb():
    if not os.path.exists(CONFIG_FILE):
        return ('a', 'a')
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
        return tuple(data['last_comb'])

def set_last_comb(comb):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'last_comb': comb}, f)

def scrape_site(url):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    combinations = itertools.combinations_with_replacement(alphabet, 2)
    
    
    with sync_playwright() as p:
        # Launch the browser and open a new page
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to the target website
        page.goto(url)

        results = []
        last_comb = get_last_comb()
        check_last_comb = True
        
        # Loop through all 2-length combinations
        for comb in combinations:
            if check_last_comb and last_comb != comb:
                print(f'check_last_comb: {check_last_comb} {last_comb} != {comb}')
                continue
            check_last_comb = False
            set_last_comb(comb)
            search_query = ''.join(comb)
            
            # Find the search bar and type the query
            page.fill('[role="searchbox"]', search_query)
            
            # Wait for results to load (adjust timeout as needed)
            selector = 'div ul#pr_id_1_list'
            page.wait_for_selector(selector, timeout=5000)  # Replace with actual results element selector

            # Wait for the result list to appear
            page.wait_for_selector('[role="listbox"]', timeout=5000)

            # Extract all the list items
            station_list_tag = page.query_selector_all('[role="listbox"]')[0]
            html_text = station_list_tag.inner_html()
            soup = BeautifulSoup(html_text, features="html.parser")
            rows = soup.select('li')

            for item in rows:
                try:
                    # Extract station name and location
                    name_code = item.find('span', class_='ng-star-inserted').contents[0].strip()
                    nam_code_list = name_code.split('-')
                    if len(nam_code_list) != 2:
                        continue
                    station_name, station_code = nam_code_list
                    station_name, station_code = station_name.strip(), station_code.strip()
                    name2 = item.find('strong').text.strip()
                    state = item.find('span', style="font-size: 80%;").find('strong').text.strip()
                    # Append the data to the list
                    data = {
                        'station_code': station_code,
                        'station_name': station_name,
                        'state': state,
                        'name2': name2
                    }
                    print(data)
                    # results.append(data)
                    write_to_csv([[station_code, station_name, state, name2]])
                except Exception as err:
                    logging.error(f'Error: {err}', exc_info=True)
            
            # Optional: clear the search bar after each query
            page.fill('[role="searchbox"]', '')
            time.sleep(1)

        browser.close()

    return

# Example usage
url = 'https://www.irctc.co.in/nget/train-search'  # Replace with the target URL
# url = 'https://www.irctc.co.in/'
scrape_site(url)
