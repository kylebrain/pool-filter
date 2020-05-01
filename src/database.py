import sqlite3
import json
import scheduler
import os
import consts
from datetime import datetime, timedelta
import time

DB_FOLDER_NAME = "database/"
PROD_NAME = "database.db"
TEST_NAME = "test_database.db"
DEFAULT_FILE_NAME = "defaults.json"

class Database():

    def __init__(self, database_type):

        self.DB_PATH = self._get_db_path(database_type)
        print("Initalizing database %s!" % (self.DB_PATH, ))
        conn = sqlite3.connect(self.DB_PATH)

        conn.execute("CREATE TABLE IF NOT EXISTS seasons ("
                            + consts.SEASON + " text PRIMARY KEY,"
                            + consts.START_MONTH + " int NOT NULL,"
                            + consts.START_DAY + " int NOT NULL,"
                            + consts.PEAK_MONTH + " int NOT NULL,"
                            + consts.PEAK_DAY + " int NOT NULL)")

        conn.execute("CREATE TABLE IF NOT EXISTS programs ("
                            + consts.ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                            + consts.SPEED + " int NOT NULL,"
                            + consts.START + " time UNIQUE NOT NULL,"
                            + consts.SUMMER_DURATION + " time NOT NULL,"
                            + consts.WINTER_DURATION + " time NOT NULL)")

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
        programs = self.get_all_programs()
        next_program = None
        next_program_timedelta = None
        next_program_start = None

        now = datetime.now()

        for program in programs:
            program_start_time = datetime.strptime(program[consts.START], "%H:%M:%S")

            program_start = datetime.combine(now.date(), program_start_time.time())

            if program_start_time.time() < now.time():
                program_start += timedelta(days=1)

            program_timedelta = program_start - now

            if next_program is None or next_program_timedelta > program_timedelta:
                next_program = program
                next_program_timedelta = program_timedelta
                next_program_start = program_start

        return next_program, next_program_start


    def get_next_event(self):
        # TODO: Interpolate between summer and winter duration
        next_program, program_start = self.get_next_program()
        if next_program is None:
            return None

        duration = datetime.strptime(next_program[consts.SUMMER_DURATION], "%H:%M:%S")
        duration_delta = timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)
        return scheduler.Scheduler.StartEvent(program_start, duration_delta, int(next_program[consts.SPEED]))


    def add_program(self, speed, start, summer_duration, winter_duration):
        conn = sqlite3.connect(self.DB_PATH)

        # TODO: Prevent overlapping events

        conn.execute('''INSERT INTO programs VALUES (NULL, ?, ?, ?, ?)''',
                       (speed,
                        start,
                        summer_duration,
                        winter_duration))
        conn.commit()
        conn.close()


    def get_all_programs(self):
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()
        cur.execute('''SELECT * FROM programs ORDER BY start''')
        programs = cur.fetchall()
        conn.close()

        return [
            {
                consts.ID : program[0],
                consts.SPEED : program[1],
                consts.START : program[2],
                consts.SUMMER_DURATION : program[3],
                consts.WINTER_DURATION : program[4]
            }

            for program in programs
        ]

    
    def delete_program(self, program_id):
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM programs WHERE " + consts.ID + " = ?", (program_id, ))
        delete_count = cur.rowcount
        conn.commit()
        conn.close()

        if delete_count == 0:
            return False

        return True

    def update_program(self, program_id, speed=None, start=None, summer_duration=None, winter_duration=None):
        '''
        At least one value must be updated
        '''

        if speed is None and start is None and summer_duration is None and winter_duration is None:
            raise ValueError("Database update_program must be passed some value to update")

        update_string = "UPDATE programs SET "
        update_arguments = []

        if speed is not None:
            update_string += consts.SPEED + " = ?, "
            update_arguments.append(speed)

        if start is not None:
            update_string += consts.START + " = ?, "
            update_arguments.append(start)

        if summer_duration is not None:
            update_string += consts.SUMMER_DURATION + " = ?, "
            update_arguments.append(summer_duration)

        if winter_duration is not None:
            update_string += consts.WINTER_DURATION + " = ?, "
            update_arguments.append(winter_duration)

        # Remove final ", "
        update_string = update_string[0:-2]

        update_string += " WHERE " + consts.ID + " = ?"
        update_arguments.append(program_id)

        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()

        cur.execute(update_string, update_arguments)

        update_count = cur.rowcount
        conn.commit()
        conn.close()

        if update_count == 0:
            return False

        return True


    def get_season_dates(self):
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()
        cur.execute('''SELECT * FROM seasons''')

        seasons = {}

        for season in cur.fetchall():
            season_dict = {}
            season_dict[consts.START] = str(season[1]) + "-" + str(season[2])
            season_dict[consts.PEAK] = str(season[3]) + "-" + str(season[4])
            seasons[season[0]] = season_dict

        conn.close()

        return seasons


    def update_season(self, season, start=None, peak=None):
        if start is None and peak is None:
            raise ValueError("Database update_season must be passed some value to update")

        update_string = "UPDATE seasons SET "
        update_arguments = []

        if start is not None:
            update_string += consts.START_MONTH + " = ?, "
            update_string += consts.START_DAY + " = ?, "
            update_arguments.extend(self.get_month_day(start))

        if peak is not None:
            update_string += consts.PEAK_MONTH + " = ?, "
            update_string += consts.PEAK_DAY + " = ?, "
            update_arguments.extend(self.get_month_day(peak))

        # Remove final ", "
        update_string = update_string[0:-2]

        update_string += " WHERE " + consts.SEASON + " = ?"
        update_arguments.append(season)

        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()

        cur.execute(update_string, update_arguments)

        update_count = cur.rowcount
        conn.commit()
        conn.close()

        if update_count == 0:
            return False

        return True

