import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tt_create_db import TrainInfo  # Assuming your model definitions are in a file named models.py

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Path to the CSV file
csv_file_path = "all_trains_lowercase.csv"

# Open and read the CSV file
with open(csv_file_path, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    
    # Loop through each row in the CSV
    for row in reader:
        # Convert booleans for weekdays to True/False
        mon = bool(int(row['mon']))
        tue = bool(int(row['tue']))
        wed = bool(int(row['wed']))
        thu = bool(int(row['thu']))
        fri = bool(int(row['fri']))
        sat = bool(int(row['sat']))
        sun = bool(int(row['sun']))
        
        # Create a new TrainInfo object and insert it into the database
        train_info = TrainInfo(
            train_number=row['train_number'],
            train_name=row['train_name'],
            train_stn_no=row['train_stn_no'],
            station_name=row['station_name'],
            station_code=row['station_code'],
            arrival=row['arrival'],
            departure=row['departure'],
            distance=row['distance'],
            avg_delay=row['avg_delay'],
            mon=mon,
            tue=tue,
            wed=wed,
            thu=thu,
            fri=fri,
            sat=sat,
            sun=sun
        )

        # Add the object to the session
        session.add(train_info)

    # Commit all records to the database
    session.commit()

# Close the session
session.close()

print("All train data inserted successfully!")
