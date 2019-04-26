import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"<br/>"
        f"For these, you must enter the start and/or end date in YYYY-MM-DD format<br>"
        f"Latest entry recorded 2017-08-23<br>"
        f"/api/v1.0/start_date<br>"
        f"/api/v1.0/start_date/end_date<br>"
    )


@app.route("/api/v1.0/precipitation")
def names():
    """Return a list of 1 year of precipitation values from the latest entry"""
    # Query 1 year of precipitation data
    last_data_point = session.query(Measurement.id, Measurement.station, Measurement.date, Measurement.prcp).order_by(Measurement.id.desc()).first()
    last_data_point_dt = dt.datetime.strptime(last_data_point.date, '%Y-%m-%d')

    
    year_before_last_point = last_data_point_dt - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >=(year_before_last_point)).\
                   filter(Measurement.date <=(last_data_point_dt)).all()
    
    precipitation_dict = {key: value for (key, value) in precipitation_data}
    # Convert list of tuples into key:value dictionary
    # Print as json
    
    return(jsonify(precipitation_dict))


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations and number of measurements each have"""
    # Query all list of stations and number of measurements each have
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                    distinct(Measurement.station).group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()
    
    return(jsonify(most_active_stations))

@app.route("/api/v1.0/tobs")
def tobs():
    """Show observed tempuratures for 1 year of data from the latest point"""

    last_data_point = session.query(Measurement.id, Measurement.station, Measurement.date, Measurement.prcp).order_by(Measurement.id.desc()).first()
    last_data_point_dt = dt.datetime.strptime(last_data_point.date, '%Y-%m-%d')
    year_before_last_point = last_data_point_dt - dt.timedelta(days=365)

    most_freq_station = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >=(year_before_last_point)).\
                   filter(Measurement.date <=(last_data_point_dt)).\
                       all()

    return(jsonify(most_freq_station))

@app.route("/api/v1.0/<start_date>")
#get tempurature data from a certain start date
def calc_temp(start_date):
    temps_data_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    return(jsonify(temps_data_query))

@app.route("/api/v1.0/<start_date>/<end_date>")
#get temperature data from a certain range from start date to end date
def calc_temp1(start_date, end_date):
    temps_data_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    return(jsonify(temps_data_query))



if __name__ == '__main__':
    app.run(debug=True)
