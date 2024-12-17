import requests
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"
DATABASE_URL = "sqlite:///trains_db.db"

from tt_create_db import StationJunction, JunctionStation

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
    for station in common_stations[:20]:
        print(station)
    print(f'common:{len(common_stations)}')
    return common_stations

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

result = get_intermediate_station(session, 'ned', 'csmt')