import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_train_data(train_no):
    url = f'https://www.confirmtkt.com/train-schedule/{train_no}'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, features="html.parser")
    rows = soup.select('tbody tr')
    processed_rows = []
    running_days_spans = soup.select('div.days-run span')
    running_days_spans = {day.text: day['class'][0] == 'running' for day in running_days_spans}
    running_days_in_order = [
        int(running_days_spans['Mon']),
        int(running_days_spans['Tue']),
        int(running_days_spans['Wed']),
        int(running_days_spans['Thu']),
        int(running_days_spans['Fri']),
        int(running_days_spans['Sat']),
        int(running_days_spans['Sun'])
    ]
    train_name = soup.select('div.train-details__tName')[0].text.strip(' \n')
    for row in rows:
        values = row.select('td')
        values = [value.text.strip(' \n') for value in values]
        if len(values) != 8:
            if len(values)>1:
                print(len(values))
                print(values)
                exit(0)
            continue
        try:
            sr_no, name_code, arrival, departure, halt_time ,distance, avg_delay, day = values
        except Exception as err:
            print(err)
            print(values)
            exit(0)
        name, code = name_code.split('-')
        name, code = name.strip(), code.strip()
        values = [train_no, train_name, sr_no, name, code, arrival, departure, distance, avg_delay, *running_days_in_order]
        processed_rows.append(values)
    if len(processed_rows)==0:
        write_to_csv_missing_train('missing_trains.csv', [f"{int(train_no):05d}"])
        print(f'no data for train {train_no}')
    return processed_rows

# url = 'https://www.confirmtkt.com/train-schedule/1001'
# print(get_train_data(url))

data = pd.DataFrame(
    {
        'SR_NO': [],
        'NAME': [],
        'CODE': [],
        'ARRIVAL': [],
        'DEPARTURE': [],
        'HALT_TIME': [],
        'DISTANCE': [],
        'AVG_DELAY': [],
        'DAY': []
    }
)

OUTPUT_FILE = 'out.csv'

def get_last():
    if not os.path.exists(OUTPUT_FILE):
        return 1001
    df = pd.read_csv(OUTPUT_FILE, header=None)
    if df.shape[0] == 0:
        return 1001
    last_row = df.iloc[-1]
    return int(last_row[0])

TOTAL_WORKERS = 50
START_TRAIN_NUMBER = get_last() + 1
LAST_TRAIN_NUMBER = 99999
HEADERS = [
    'TRAIN_NUMBER',
    'TRAIN_NAME',
    'SR_NO',
    'STATION_NAME',
    'STATION_CODE',
    'ARRIVAL',
    'DEPARTURE',
    'DISTANCE',
    'AVG_DELAY',
    'MON',
    'TUE',
    'WED',
    'THU',
    'FRI',
    'SAT',
    'SUN'
]

# Function to lazily generate URLs with 5-digit train numbers
def train_number():
    for i in range(START_TRAIN_NUMBER, LAST_TRAIN_NUMBER + 1):  # +1 to include LAST_TRAIN_NUMBER
        yield f"{i:05d}" 

# Function to write a batch of results to a CSV file
def write_to_csv(filename, data):
    if len(data) == 0:
        return
    df = pd.DataFrame(data)
    df.columns = HEADERS
    df['SR_NO'] = df['SR_NO'].astype(int)
    df = df.sort_values(by=['TRAIN_NUMBER', 'SR_NO'])
    with open(filename, "a", newline="", encoding="utf-8") as f:
        write_header = f.tell() == 0  # Check if the file is empty
        df.to_csv(f, index=False, header=write_header)

def write_to_csv_missing_train(filename, data):
    df = pd.DataFrame(data)
    df.columns = ['MISSING_TRAINS']
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
            futures.append(executor.submit(get_train_data, train_number))
            
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

process_and_save(train_number(), OUTPUT_FILE)
