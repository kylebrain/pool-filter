import sqlite3
import json
import scheduler
import os
import consts
from datetime import datetime, timedelta

DB_FOLDER_NAME = "database/"
PROD_NAME = "database.db"
TEST_NAME = "test_database.db"
DEFAULT_FILE_NAME = "defaults.json"

class Database():

    def __init__(self, database_type):

        self.DB_PATH = self._get_db_path(database_type)
        print("Initalizing database %s!" % (self.DB_PATH, ))
        conn = sqlite3.connect(self.DB_PATH)

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

        defaults = Database.get_defaults()

        conn.execute('''INSERT OR IGNORE INTO seasons VALUES (?, ?, ?, ?, ?)''',
                       (consts.SUMMER,
                       *Database.get_month_day(defaults[consts.SEASONS][consts.SUMMER][consts.START]),
                       *Database.get_month_day(defaults[consts.SEASONS][consts.SUMMER][consts.PEAK])))

        conn.execute('''INSERT OR IGNORE INTO seasons VALUES (?, ?, ?, ?, ?)''',
                       (consts.WINTER,
                       *Database.get_month_day(defaults[consts.SEASONS][consts.WINTER][consts.START]),
                       *Database.get_month_day(defaults[consts.SEASONS][consts.WINTER][consts.PEAK])))

        conn.commit()
        conn.close()

    def _get_db_path(self, database_type):
        database_file_name = ""
        if database_type == "production":
            database_file_name = PROD_NAME
        else:
            database_file_name = TEST_NAME

        return os.path.join(DB_FOLDER_NAME, database_file_name)

    @staticmethod
    def get_defaults():
        defaults_file = open(os.path.join(DB_FOLDER_NAME, DEFAULT_FILE_NAME))
        return json.load(defaults_file)

    @staticmethod
    def get_month_day(date_string):
        return date_string.split('-')


    def get_next_program(self):
        '''
        Returns the next program as StartEvent by querying the database
        Currently returns the event with the next start time (could change to reschedule the current event)
        '''
        return scheduler.Scheduler.StartEvent(datetime.now() + timedelta(seconds=5), timedelta(seconds=15), 4)


    def add_program(self, speed, start, summer_duration, winter_duration):
        conn = sqlite3.connect(self.DB_PATH)
        conn.execute('''INSERT INTO programs VALUES (NULL, ?, ?, ?, ?)''',
                       (speed,
                        start,
                        summer_duration,
                        winter_duration))
        conn.commit()
        conn.close()