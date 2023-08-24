# Import the dependencies.
import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/messa/SQLalchemy-challenge/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Use lowercase table names as they are in the database
Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - datetime.timedelta(days=365)

    # Query to retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary where the date is the key and prcp is the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query to retrieve the list of stations
    stations_list = session.query(Station.station).all()

    # Convert the list of tuples to a flat list
    stations_flat = [station[0] for station in stations_list]

    # Return the JSON list of station names
    return jsonify(stations_flat)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - datetime.timedelta(days=365)

    # Query to find the station with the most observations
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]

    # Query to retrieve temperature observations for the most-active station for the previous year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()

    # Create a list of temperature observations
    tobs_list = [tobs for date, tobs in tobs_data]

    # Return the JSON list of temperature observations
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
    # Query to calculate min, avg, and max temperatures for the specified date range
    if end is None:
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    else:
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start, Measurement.date <= end).all()

    # Extract the temperature statistics
    min_temperature, avg_temperature, max_temperature = temperature_data[0]

    # Prepare a response based on the availability of data
    response = {
        "min_temperature": min_temperature if min_temperature is not None else "No data",
        "avg_temperature": avg_temperature if avg_temperature is not None else "No data",
        "max_temperature": max_temperature if max_temperature is not None else "No data"
    }

    # Return the JSON representation of the response
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
