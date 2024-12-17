import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import JunctionStation  # Assuming your model definitions are in models.py

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Path to the CSV file for Junction Stations
csv_file_path = "updated_jcn_stn.csv"  # Replace with your actual file path

# Open and read the CSV file
with open(csv_file_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    # Loop through each row in the CSV
    for row in reader:
        # Find the junction station by station_code
        station = session.query(JunctionStation).filter_by(station_code=row['station_code']).first()
        
        if station:
            # Update junction_info if the station exists
            station.junction_info = row['junction_info']
        else:
            # If station does not exist, create a new entry
            station = JunctionStation(
                station_code=row['station_code'],
                junction_info=row['junction_info']
            )
            # Add the new station to the session
            session.add(station)

    # Commit all updates and new records to the database
    session.commit()

# Close the session
session.close()

print("Junction station information updated successfully!")
