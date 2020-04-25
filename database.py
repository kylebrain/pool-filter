import sqlite3
import json

DB_FILE_NAME = "database.db"
DEFAULT_FILE_NAME = "defaults.json"

SEASONS = "seasons"
SEASONAL_FILTERS = "seasonal_filters"
SUMMER = "summer"
WINTER = "winter"
HIGH = "high"
LOW = "low"
START = "start"
PEAK = "peak"
LOW = "low"


def get_defaults():
    defaults_file = open(DEFAULT_FILE_NAME)
    return json.load(defaults_file)

def get_month_day(date_string):
    return date_string.split('-')


def initialize_sql():
    conn = sqlite3.connect(DB_FILE_NAME)

    conn.execute('''CREATE TABLE IF NOT EXISTS Seasons (
                        Season text PRIMARY KEY,
                        StartMonth int NOT NULL,
                        StartDay int NOT NULL,
                        PeakMonth int NOT NULL,
                        PeakDay int NOT NULL
                    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS Seasonal (
                        Season text PRIMARY KEY,
                        Level text NOT NULL,
                        Speed int NOT NULL,
                        StartTime time NOT NULL,
                        EndTime time NOT NULL,
                        FOREIGN KEY (Season) REFERENCES Seasons (Season)
                    )''')

    defaults = get_defaults()

    conn.execute('''INSERT OR IGNORE INTO Seasons VALUES (?, ?, ?, ?, ?)''', (SUMMER, *get_month_day(defaults[SEASONS][SUMMER][START]), *get_month_day(defaults[SEASONS][SUMMER][PEAK])))
    conn.execute('''INSERT OR IGNORE INTO Seasons VALUES (?, ?, ?, ?, ?)''', (WINTER, *get_month_day(defaults[SEASONS][WINTER][START]), *get_month_day(defaults[SEASONS][WINTER][PEAK])))
    # conn.execute('''INSERT INTO Seasonal VALUES ('summer', 'high', 8, '08:00', '11:00')''')

    conn.execute('''CREATE TABLE IF NOT EXISTS Override (
                        Speed int NOT NULL,
                        StartTime time NOT NULL,
                        EndTime time NOT NULL
                    )''')

    conn.commit()

    conn.close()
