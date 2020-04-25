from flask import Flask
import database


def start_up():
    database.initialize_sql()

    app.run()

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello!</h1>'

if __name__ == "__main__":
    start_up()