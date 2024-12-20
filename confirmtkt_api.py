import requests
import json
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"
DATABASE_URL = "sqlite:///trains_db.db"

from tt_create_db import StationJunction, JunctionStation, StationInfo

# """ Format of arguments"""
# from_station = "NDLS"
# to_station = "MMCT"
# date_of_journey = "18-12-2024"


def get_train_booking_data(fromStnCode, toStnCode, doj):
   
    url = "https://securedapi.confirmtkt.com/api/platform/trainbooking/tatwnstns"
    params = {
        "fromStnCode": fromStnCode,
        "destStnCode": toStnCode,
        "doj": doj,
        "token": "368223F820EBEB8BFA467209CD49702C69606FF2E32B502EA377C65EA9A2031E",  # Your token
        "quota": "GN",
        "appVersion": "290"
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Return the JSON response
        
        return response.json()
    else:
        # Return an error message if the request failed
        return {"error": f"Error: {response.status_code}"}


def get_intermediate_station(session, source_stn, destination_stn):
    # query db for after joining tables stn_jcn and jcn_stn
    # 
    source_record = session.query(StationJunction).filter_by(station_code=source_stn).first()
    if not source_record:
        print(f'Error: station not found {source_stn}')
        exit(0)
    dest_record = session.query(JunctionStation).filter_by(station_code=destination_stn).first()
    if not dest_record:
        print(f'Error: station not found {source_stn}')
        exit(0)
    soruce_to_junction_info = eval(source_record.junction_info)
    junction_info_to_dest = eval(dest_record.junction_info)
    common_stations = []
    for station, data in soruce_to_junction_info.items():
        if station in junction_info_to_dest:
            dest_record = junction_info_to_dest[station]
            data['time'] = int(data['time'] + dest_record['time'])
            data['distance'] = int(data['distance'] + dest_record['distance'])
            common_stations.append((station, data))
    common_stations.sort(key=lambda e: e[1]['time'])
    intermediate_list_5 = []
    for station in common_stations[:5]:
        intermediate_list_5.append(session.query(StationInfo.city_name, StationInfo.state).filter_by(station_code=station[0]).first())
    intermediates= []
    for i in intermediate_list_5:
        print(i)
        a = session.query(StationInfo.station_code).filter_by(city_name=i[0], state=i[1]).first()
        if a:
            intermediates.append(a[0])
    print(intermediates)
    return intermediates

def find_trains(session, source_stn, destination_stn, datetime_obj):
    intermediates = get_intermediate_station(session, source_stn, destination_stn)
    results = []
    for intermediate in intermediates:
        # source_stn => intermediate (same day)
        # intermediate => destination_stn (same day, next day, next to next day)
        DATETIME_FORMAT = "%d-%m-%Y"
        today = datetime_obj.strftime(DATETIME_FORMAT)
        tomorrow = (datetime_obj+timedelta(days=1)).strftime(DATETIME_FORMAT)
        day_after_tomorrow = (datetime_obj+timedelta(days=2)).strftime(DATETIME_FORMAT)
        
        source_stn = source_stn.upper()
        intermediate = intermediate.upper()
        destination_stn = destination_stn.upper()
        first_journey = get_train_booking_data(source_stn, intermediate, today)
        second_journey = []
        second_journey.append(get_train_booking_data(intermediate, destination_stn, today))
        second_journey.append(get_train_booking_data(intermediate, destination_stn, tomorrow))
        second_journey.append(get_train_booking_data(intermediate, destination_stn, day_after_tomorrow))
        results.append((first_journey, second_journey))
    return results

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# result = get_intermediate_station(session, 'cmnr', 'sc')
tomorrow = datetime.now()+timedelta(days=1)
results = find_trains(session, 'ned', 'rk', tomorrow)
with open('output.json', 'w') as f:
    json.dump(results, f, indent=4)
for result in results:
    print(len(result))
