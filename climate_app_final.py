import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
measurement = Base.classes.measurement
Station = Base.classes.station

# Identification of last date of data
session = Session(engine)
last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

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
        f"4. Temperature data from your chosen start date. Please insert the start date as 'YYYY-MM-DD' - /api/v1.0/<start><br/><br/>"
        f"5. Temperature data for a specified period. Please insert the start and dates as 'YYYY-MM-DD, YYYY-MM-DD' - /api/v1.0/<start>/<end><br/><br/>"
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

    """Return all stations"""
    # Query data for all stations

    all_stations = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(all_stations))

    return jsonify(station_list)

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

@app.route("/api/v1.0/<start_date>")
def start_stats(start_date):

	start_temps = session.query(
		func.min(measurement.tobs), 
		func.avg(measurement.tobs),
		func.max(measurement.tobs)
	).filter(
		measurement.date >= start_date
	).all()


	temp_stats = list()
	for tmin, tavg, tmax in start_temps:
		temp_stats_dict = {}
		temp_stats_dict["Min Temp"] = tmin
		temp_stats_dict["Max Temp"] = tavg
		temp_stats_dict["Avg Temp"] = tmax
		temp_stats.append(temp_stats_dict)

	return jsonify (temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def tstartend(start,end):         
    """ When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive. """    
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),func.max(measurement.tobs)).\
                  filter(measurement.date >= start, measurement.date <= end).order_by(measurement.date.desc()).all()
    print(f"Temperature Analysis for the dates greater than or equal to the start date and lesser than or equal to the end date")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)   

if __name__ == '__main__':
    app.run(debug=True)