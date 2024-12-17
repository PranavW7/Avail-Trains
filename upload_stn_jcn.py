import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tt_create_db import StationJunction  # Assuming your model definitions are in models.py

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Path to the CSV file for Station Junction
csv_file_path = "updated_stn_jcn.csv"  # Replace with your actual file path

# Open and read the CSV file
with open(csv_file_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    # Loop through each row in the CSV
    for row in reader:
        # Find the station junction by station_code
        station_junction = session.query(StationJunction).filter_by(station_code=row['station_code']).first()
        
        if station_junction:
            # Update junction_info if the station junction exists
            station_junction.junction_info = row['junction_info']
        else:
            # If station junction does not exist, create a new entry
            station_junction = StationJunction(
                station_code=row['station_code'],
                junction_info=row['junction_info']
            )
            # Add the new station junction to the session
            session.add(station_junction)

    # Commit all updates and new records to the database
    session.commit()

# Close the session
session.close()

print("Station Junction information updated successfully!")
