from flask import Flask
import database
from scheduler import Scheduler


def start_up():
    database.initialize_sql()
    scheduler = Scheduler()

    app.run()

app = Flask(__name__)


@app.route('/')
def index():
    return '''<h1>Welcome to Kyle Brainard\'s Pool Filter API</h1>
              <p>Documentation coming soon. Autogenerate doxygen?</p>'''


@app.route('/program/now', methods = ['GET'])
def get_current_program():
    pass


@app.route('/program/all', methods = ['GET'])
def get_all_programs():
    pass


@app.route('/seasons/', methods = ['GET'])
def get_season_dates():
    pass


@app.route('/program/add', methods = ['POST'])
def post_new_program():
    pass


@app.route('/program/update', methods = ['PUT'])
def put_update_program():
    pass


@app.route('/override', methods = ['PUT'])
def put_override():
    pass


@app.route('/override/stop', methods = ['PUT'])
def put_stop_override():
    pass


@app.route('/program/delete', methods = ['DELETE'])
def delete_program():
    pass


if __name__ == "__main__":
    start_up()
