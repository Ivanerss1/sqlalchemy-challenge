# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import datetime as dt


#################################################
# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine)
#################################################


# reflect an existing database into a new model

# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


# Save references to each table


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Flask Routes

# 1. Home route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# 2. Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last data point
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary with date as the key and prcp as the value
    precip_dict = {date: prcp for date, prcp in precip_data}

    return jsonify(precip_dict)

# 3. Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations = session.query(Station.station).all()

    # Convert list of tuples into a list
    station_list = list(np.ravel(stations))

    return jsonify(station_list)

# 4. Temperature Observations (TOBS) route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the last data point
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query temperature observations for the most active station in the last year of data
    most_active_station = 'USC00519281'  # Replace with the actual station ID if different
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the list of tuples into a list
    tobs_list = list(np.ravel(tobs_data))

    return jsonify(tobs_list)

# 5. Start/End range route for temperatures
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=None):
    # If no end date is provided, calculate stats from the start date to the end of the data set
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    else:
        # If an end date is provided, calculate stats between start and end dates
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    temps_list = list(np.ravel(results))

    return jsonify(temps_list)

# Close session
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
  