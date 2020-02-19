# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"
    )
#########################################################################################


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""


#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    lastDate = (session.query(Measurement.date)
            .order_by(Measurement.date.desc())
            .first())[0]
    lastDate = dt.datetime.strptime(lastDate, '%Y-%m-%d')


# Calculate the date 1 year ago from the last data point in the database
    oneYearBefore = lastDate - dt.timedelta(days=365)

# Perform a query to retrieve precipitation data
    preciData = (session.query(Measurement.date, Measurement.prcp)
             .filter(Measurement.date > oneYearBefore)
             .all())

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in preciData:
        row = {}
        row["date"] = preciData[0]
        row["prcp"] = preciData[1]
        rain_totals.append(row)

    return jsonify(rain_totals)


#########################################################################################
@app.route("/api/v1.0/stations")
def stations():

    stations_query = session.query(Station.name, Station.station)

    all_stations = []
    for name, station in stations_query:
        station_dict = {}
        station_dict["name"] = name
        station_dict["station"] = station
        all_stations.append(station_dict)
    return jsonify(all_stations)


#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#    * Query for the dates and temperature observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#           * Return the json representation of your dictionary.
    lastDate = (session.query(Measurement.date)
            .order_by(Measurement.date.desc())
            .first())[0]
    lastDate = dt.datetime.strptime(lastDate, '%Y-%m-%d')


# Calculate the date 1 year ago from the last data point in the database
    oneYearBefore = lastDate - dt.timedelta(days=365)

# Perform a query to retrieve temperature data
    temperature = (session.query(Measurement.date, Measurement.tobs)
             .filter(Measurement.date > oneYearBefore)
             .order_by(Measurement.date).all())

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)

    
#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):

 # go back one year from start date and go to end of data for Min/Avg/Max temp
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start, end):

  # go back one year from start/end date and get Min/Avg/Max temp
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################


if __name__ == '__main__':
    app.run(debug=True)
