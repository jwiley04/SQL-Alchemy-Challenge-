import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Calculate the date one year from the last date in data set.
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data from the last 12 months"""

    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= year_ago).order_by(Measurement.date).all()

    session.close()

    precipitation_data = []

    for date, prcp in results:
        prcp_data = {}

        prcp_data["Date"] = date
        prcp_data["Precipitation"] = prcp

        precipitation_data.append(prcp_data)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    """Return a list of all station data"""

    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        station = {}

        station["Station"] = station
        station["Name"] = name
        station["Latitude"] = latitude
        station["Longitude"] = longitude
        station["Elevation"] = elevation

        all_stations.append(station)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    """Return a list of all tobs from the most active station for the previous year of data"""
 
    most_active = session.query(Measurement.station, func.count(Measurement.station)).group_by(
        Measurement.station).order_by(func.count(Measurement.station).desc()).all()


    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active[0][0]).filter(Measurement.date >= year_ago).all()

    session.close()


    most_active_tobs = []
    for date, tobs in results:
        most_active_data = {}

        most_active_data['Date'] = date
        most_active_data['Tobs'] = tobs

        most_active_tobs.append(most_active_data)

    return jsonify(most_active_tobs)


@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    """Return a list of min, avg, and max temperatures for a specified start date"""

    results = session.query(func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    start_date_data = []
    for tmin_tobs, tavg_tobs, tmax_tobs in results:
        start_date = {}

        start_date['Min_Tobs'] = tmin_tobs
        start_date['Avg_Tobs'] = tavg_tobs
        start_date['Max_Tobs'] = tmax_tobs

        start_date_data.append(start_date)

    return jsonify(start_date_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    """Return a list of min, avg, and max temperatures for a specified start and end date"""

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    start_end_data = []
    for tmin_tobs, tavg_tobs, tmax_tobs in results:
        start_end = {}

        start_end['Min_Tobs'] = tmin_tobs
        start_end['Avg_Tobs'] = tavg_tobs
        start_end['Max_Tobs'] = tmax_tobs

        start_end_data.append(start_end)

    return jsonify(start_end_data)


if __name__ == "__main__":
    app.run(debug=True)