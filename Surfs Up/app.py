# This script provides a Flask API for accessing weather data from Hawaii.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import datetime as dt

# Connect to the Hawaii weather database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

# Create a Flask app
app = Flask(__name__)

# Define Flask routes
@app.route('/')
def home():
    return (
        'Welcome to the Hawaii weather API!<br>'
        'Available routes:<br>'
        '/api/v1.0/precipitation<br>'
        '/api/v1.0/stations<br>'
        '/api/v1.0/tobs<br>'
        '/api/v1.0/<start><br>'
        '/api/v1.0/<start>/<end><br>'
    )

@app.route('/api/v1.0/precipitation')
def get_precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()

    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route('/api/v1.0/stations')
def get_stations():
    session = Session(engine)
    results = session.query(station.station).distinct().all()
    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def get_tobs():
    session = Session(engine)
    recent_date = dt.date(2017, 8, 23)
    query_date = recent_date - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= query_date).\
        order_by(measurement.date).all()
    session.close()

    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
def get_temps(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    temperature_data = [func.min(measurement.tobs),
                        func.avg(measurement.tobs),
                        func.max(measurement.tobs)]
    results = session.query(*temperature_data).\
        filter(measurement.date >= start_date).all()
    session.close()

    temp_data = list(np.ravel(results))
    return jsonify(temp_data)

@app.route('/api/v1.0/<start>/<end>')
def get_temps_date_range(start, end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    temperature_data = [func.min(measurement.tobs),
                        func.avg(measurement.tobs),
                        func.max(measurement.tobs)]
    results = session.query(*temperature_data).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).all()
    session.close()

 
