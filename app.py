import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Identification of last date of data
session = Session(engine)
last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

# Identification of first date for last 12 months
last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to our Honolulu, Hawaii climate data page.<br/><br/>"
        f"We provide the following climate data analysis:<br/><br/>"
        f"1. Precipitation for last 12 months - /api/v1.0/precipitation<br/><br/>"
        f"2. List of stations - /api/v1.0/stations<br/><br/>"
        f"3. Temperature Observations Data for the most active station for the last 12 months - /api/v1.0/tobs<br/><br/>"
        f"4. Temperature data from your chosen start date. Please insert the start date as 'YYYY-MM-DD' - /api/v1.0/start/<start><br/><br/>"
        f"5. Temperature data for a specified period. Please insert the start and dates as 'YYYY-MM-DD'/'YYYY-MM-DD' - /api/v1.0/period/<start>/<end><br/><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
# Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data for the last 12 months"""
    # Query precipitation for the last 12 months
    sel = [measurement.date, measurement.prcp]

    year_prcp = session.query(*sel).filter(measurement.date < '2017-08-23').filter(measurement.date >= '2016-08-23').order_by(measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    prcp_data = dict(year_prcp)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
# Create our session (link) from Python to the DB
    session = Session(engine)

    """List of stations from dataset"""
    # Query all stations
    station_name = session.query(station.id, station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = dict(station_name)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
# Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tobs for the most active station for the last 12 months"""
    # Query tobs for the most active station for last 12 months

    temp_tobs = (session.query(measurement.date, measurement.tobs).filter(measurement.date >= '2016-08-23', measurement.station == "USC00519281").all())

    session.close()

    # Convert list of tuples into normal list
    tobs_data = dict(temp_tobs)

    return jsonify(tobs_data)

@app.route("/api/v1.0/start/<start>")
def start(start=None):
# Create our session (link) from Python to the DB
    session = Session(engine)

    start_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    
    session.close()

    # Convert list of tuples into normal list
    start_list = list()
    for tmin, tavg, tmax in start_temps:
        start_dict = {}
        start_dict["Min Temp"] = tmin
        start_dict["Max Temp"] = tavg
        start_dict["Avg Temp"] = tmax
        start_list.append(start_dict)

    return jsonify ({'Data':start_list})

@app.route("/api/v1.0/period/<start>/<end>")
def period(start,end):
# Create our session (link) from Python to the DB
    session = Session(engine)

    period_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
    for temps in period_temps:
        period_temp_dict = {"Minimum Temp":period_temps[0][0],"Average Temp":period_temps[0][1],"Maximum Temp":period_temps[0][2]}

    return jsonify (period_temp_dict)

if __name__ == "__main__":
    app.run(debug=False)
