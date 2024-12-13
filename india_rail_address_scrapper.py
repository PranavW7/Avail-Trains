import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
import pandas as pd


SEARCH_BASE_URL = 'https://indiarailinfo.com/shtml/list.shtml?LappGetStationList/{}/0/0/0?=&date={}&seq={}'
BASE_URL = 'https://indiarailinfo.com/departures/{}'

def retry(f):
    def decorated(*args, **kwargs):
        for _ in range(3):
            result = f(*args, **kwargs)
            if result != None:
                return result
        return []
    return decorated


def get_station_address(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    print(url, resp)
    soup = BeautifulSoup(resp.content, features="html.parser")
    address = soup.select('span#PlaceText')[0].text
    return address


@retry
def get_station_data(station_code):
    try:
        url = SEARCH_BASE_URL.format(station_code, int(time.time()), 1)
        resp = requests.get(url)
        if resp.status_code != 200:
            return None
        print(url, resp)
        soup = BeautifulSoup(resp.content, features="html.parser")
        rows = soup.select('table tr')
        row1_tds = rows[0].select('td')
        row2_tds = rows[1].select('td')
        station_detail_number = row1_tds[0].text
        station_code = row1_tds[1].text
        name_1 = row1_tds[2].text
        name_2 = row1_tds[3].text
        name_3 = row2_tds[2].text

        link = BASE_URL.format(station_detail_number)

        address = get_station_address(link)
    except Exception as err:
        print(f'Error: error in {url}')
        return None
    return [[station_code, name_1, name_2, name_3, address]]

# url = 'https://www.confirmtkt.com/train-schedule/1001'
# print(get_train_data(url))

OUTPUT_FILE = 'out.csv'

def get_last():
    if not os.path.exists(OUTPUT_FILE):
        return None
    df = pd.read_csv(OUTPUT_FILE, header=None)
    if df.shape[0] == 0:
        return None
    last_row = df.iloc[-1]
    return last_row[0]

TOTAL_WORKERS = 10
HEADERS = [
    'STATION_CODE',
    'NAME_1',
    'NAME_2',
    'NAME_3',
    'ADDRESS'
]

# Function to lazily generate URLs with 5-digit train numbers
def station_code_generator():
    START_STATION_CODE = get_last()
    stations = pd.read_csv('unique_station_codes.csv')
    for station_code in stations['STATION_CODE']:
        if START_STATION_CODE is not None and START_STATION_CODE != station_code:
            continue
        if START_STATION_CODE == station_code:
            START_STATION_CODE = None
            continue
        yield station_code

# Function to write a batch of results to a CSV file
def write_to_csv(filename, data):
    if len(data) == 0:
        return
    df = pd.DataFrame(data)
    df.columns = HEADERS
    with open(filename, "a", newline="", encoding="utf-8") as f:
        write_header = f.tell() == 0  # Check if the file is empty
        df.to_csv(f, index=False, header=write_header)


# Main function to process the generator and save results
def process_and_save(generator, filename, num_threads=TOTAL_WORKERS):
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        results = []
        
        for train_number in generator:
            print(f'{train_number}\r')
            # Submit train_number to thread pool
            futures.append(executor.submit(get_station_data, train_number))
            
            # Once we have TOTAL_WORKERS futures, process them
            if len(futures) >= TOTAL_WORKERS:
                for future in as_completed(futures):
                    results.extend(future.result())
                write_to_csv(filename, results)  # Save batch to CSV
                results = []  # Reset results
                futures = []  # Reset futures
                time.sleep(0.1)
        
        # Process remaining futures
        for future in as_completed(futures):
            results.append(future.result())
        if results:
            write_to_csv(filename, results)

process_and_save(station_code_generator(), OUTPUT_FILE)
