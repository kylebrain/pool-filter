import sqlite3
import json
import scheduler
from datetime import datetime, timedelta

DB_FILE_NAME = "database.db"
DEFAULT_FILE_NAME = "defaults.json"

SEASONS = "seasons"
SUMMER = "summer"
WINTER = "winter"
START = "start"
PEAK = "peak"


def get_defaults():
    defaults_file = open(DEFAULT_FILE_NAME)
    return json.load(defaults_file)


def get_month_day(date_string):
    return date_string.split('-')


def get_next_program():
    '''
    Returns the next program as StartEvent by querying the database
    Currently returns the event with the next start time (could change to reschedule the current event)
    '''
    return scheduler.Scheduler.StartEvent(datetime.now() + timedelta(seconds=5), timedelta(seconds=15), 4)


def initialize_sql():
    conn = sqlite3.connect(DB_FILE_NAME)

    conn.execute('''CREATE TABLE IF NOT EXISTS seasons (
                        season text PRIMARY KEY,
                        start_month int NOT NULL,
                        start_day int NOT NULL,
                        peak_month int NOT NULL,
                        peak_day int NOT NULL
                    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS programs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        speed int NOT NULL,
                        start_time time NOT NULL,
                        summer_duration time NOT NULL,
                        winter_duration time NOT NULL
                    )''')

    defaults = get_defaults()

    conn.execute('''INSERT OR IGNORE INTO Seasons VALUES (?, ?, ?, ?, ?)''', (SUMMER, *get_month_day(defaults[SEASONS][SUMMER][START]), *get_month_day(defaults[SEASONS][SUMMER][PEAK])))
    conn.execute('''INSERT OR IGNORE INTO Seasons VALUES (?, ?, ?, ?, ?)''', (WINTER, *get_month_day(defaults[SEASONS][WINTER][START]), *get_month_day(defaults[SEASONS][WINTER][PEAK])))

    conn.commit()

    conn.close()
