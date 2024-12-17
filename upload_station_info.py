import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tt_create_db import StationInfo  # Assuming your model definitions are in a file named models.py

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Path to the CSV file
csv_file_path = "updated_station_info_fixed.csv"  # Replace with your actual file path

# Open and read the CSV file
with open(csv_file_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    # Loop through each row in the CSV
    for row in reader:
        # Find the station by station_code
        station = session.query(StationInfo).filter_by(station_code=row['station_code']).first()
        
        if station:
            # Update fields if the station exists
            station.station_name = row['station_name']
            station.city_name = row['city_name']
            station.state = row['state']
            station.latitude = row['latitude']
            station.longitude = row['longitude']
            station.tier = row['tier']
            station.airport_availability = bool(int(row['airport_availability']))
            station.station_category = row['station_category']
        else:
            # If station does not exist, create a new entry
            station = StationInfo(
                station_name=row['station_name'],
                station_code=row['station_code'],
                city_name=row['city_name'],
                state=row['state'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                tier=row['tier'],
                airport_availability=bool(int(row['airport_availability'])),
                station_category=row['station_category']
            )
            # Add the new station to the session
            session.add(station)

    # Commit all updates and new records to the database
    session.commit()

# Close the session
session.close()

print("Station information updated successfully!")
