import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect

from flask import Flask, json, jsonify

#######################################################################
# Database Setup
#######################################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#######################################################################
# Flask Setup
#######################################################################
app = Flask(__name__)

#######################################################################
# Flask Routes
#######################################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    session = Session(engine)
    return (
        f"Welcome to the Homepage of the Climate App<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date/"
    )

# JSON representation of dictionary
@app.route('/api/v1.0/precipitation/')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    first_date = last_date - dt.timedelta(days=365)
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).all()

    return jsonify(last_year_data)

# JSON-list of stations 
@app.route('/api/v1.0/stations/')
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    
    return jsonify(stations)


# JSON-list of Tobs from the previous year
@app.route('/api/v1.0/tobs/')
def tobs():
    session = Session(engine)
    stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = stations[0][0]
    station_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).all()
    station_data = list(np.ravel(station_data))

    return jsonify(station_data)


# JSON list of TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route('/api/v1.0/<start_date>/')
def calc_temps_start(start_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))
    results = results.filter(Measurement.date > start_date).all()
    temps = list(np.ravel(results))

    return jsonify(temps)


# JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
@app.route('/api/v1.0/<start_date>/<end_date>/')
def calc_temps_start_end(start_date, end_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    results = results.filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps = list(np.ravel(results))

    return jsonify(temps)


if __name__ == "__main__":
    app.run(debug=True)