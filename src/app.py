from flask import Flask, jsonify, request
from database import Database
from scheduler import Scheduler
import time
from datetime import datetime, timedelta
import os
import consts
import sqlite3


scheduler = None
database = None


def create_app():

    app = Flask(__name__)

    if app.config["ENV"] == "production" or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        global scheduler
        global database

        database = Database(app.config["ENV"])
        scheduler = Scheduler(database)

    return app


app = create_app()


@app.route('/')
def index():
    return '''<h1>Welcome to Kyle Brainard\'s Pool Filter API</h1>
              <p>Documentation coming soon. Autogenerate doxygen?</p>'''


@app.route('/program/now', methods = ['GET'])
def get_current_program():
    try:
        with scheduler:
            return jsonify(scheduler.get_current_event())
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/program/all', methods = ['GET'])
def get_all_programs():
    try:
        return jsonify(database.get_all_programs())
    except Exception as e:
        return jsonify({"message": "SQLITE " + str(e)}), 500


@app.route('/seasons/', methods = ['GET'])
def get_season_dates():
    return jsonify(database.get_season_dates())


@app.route('/program/add', methods = ['POST'])
def post_new_program():
    speed = request.args.get(consts.SPEED)
    start = request.args.get(consts.START)
    summer_duration = request.args.get(consts.SUMMER_DURATION)
    winter_duration = request.args.get(consts.WINTER_DURATION)

    if speed is None or start is None or summer_duration is None or winter_duration is None:
        error_response = {
            consts.SPEED : speed is None,
            consts.START : start is None,
            consts.SUMMER_DURATION : summer_duration is None,
            consts.WINTER_DURATION : winter_duration is None,
        }
        return jsonify({"message": "Insufficient information provided to create new program", "parameter": error_response}), 400

    # TODO: Check for correct formatting here

    try:
        database.add_program(speed, start, summer_duration, winter_duration)
    except sqlite3.IntegrityError:
        return jsonify({"message": "Start times must be unique"}), 400

    with scheduler:
        scheduler.update_next_event()

    return jsonify({"message": "Successfully added new program"})


@app.route('/program/update', methods = ['PUT'])
def put_update_program():
    pass


@app.route('/override', methods = ['PUT'])
def put_override():

    speed = request.args.get(consts.SPEED)
    duration = request.args.get(consts.DURATION)

    if speed is None:
        return jsonify({"message": "Speed not provided to override"}), 400

    speed = int(speed)
    if speed != 0 and duration is None:
        return jsonify({"message": "Duration not provided to overrride when trying to turn on filter"}), 400

    try:

        with scheduler:
            if speed != 0:
                time = datetime.strptime(duration, "%H:%M:%S")
                delta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
                scheduler.override_current_event(Scheduler.StartEvent(datetime.now(), delta, int(speed)))
            else:
                scheduler.override_current_event(Scheduler.StopEvent(datetime.now()))

    except Exception as e:
        return jsonify({"message": "Failed to override current event: " + str(e)}), 500

    return jsonify({"message": "Overwrote current program"})


@app.route('/program/delete', methods = ['DELETE'])
def delete_program():
    program_id = request.args.get(consts.ID)

    if program_id is None:
        return jsonify({"message": "Did not provide id of program to delete"}), 400

    if not database.delete_program(int(program_id)):
        return jsonify({"message": "Passed id was not valid"}), 400

    with scheduler:
        scheduler.update_next_event()
    return jsonify({"message": "Sucessfully deleted program"})


if __name__ == "__main__":
    app.run()