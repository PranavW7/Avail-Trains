from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection details
DATABASE_URL = "mysql+pymysql://root:praj9994@localhost/wayport"

# Create engine and base
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define tables
class StationInfo(Base):
    __tablename__ = "station_info_tbl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(64), nullable=True)
    station_code = Column(String(16), nullable=True, unique=True)
    city_name = Column(String(64), nullable=True)
    state = Column(String(64), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    tier = Column(String(8), nullable=True)
    airport_availability = Column(Boolean, nullable=True)
    station_category = Column(String(8), nullable=True)


class TrainInfo(Base):
    __tablename__ = "train_info_tbl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    train_number = Column(Integer, nullable=False)
    train_name = Column(String(64), nullable=False)
    train_stn_no = Column(Integer, nullable=False)
    station_name = Column(String(64), nullable=False)
    station_code = Column(String(16), nullable=False)
    arrival = Column(String(16), nullable=False)
    departure = Column(String(16), nullable=False)
    distance = Column(Integer, nullable=False)
    avg_delay = Column(Integer, nullable=True)
    mon = Column(Boolean, nullable=False)
    tue = Column(Boolean, nullable=False)
    wed = Column(Boolean, nullable=False)
    thu = Column(Boolean, nullable=False)
    fri = Column(Boolean, nullable=False)
    sat = Column(Boolean, nullable=False)
    sun = Column(Boolean, nullable=False)


class StationJunction(Base):
    __tablename__ = "stn_jcn_tbl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_code = Column(String(16), nullable=False, unique=True)
    junction_info = Column(JSON, nullable=False)


class JunctionStation(Base):
    __tablename__ = "jcn_stn_tbl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_code = Column(String(16), nullable=False, unique=True)
    junction_info = Column(JSON, nullable=False)


# Create tables in the database
Base.metadata.create_all(engine)

print("Tables created successfully in the database.")
