import sqlite3

DB_FILE_NAME = "database.db"

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

    # conn.execute('''INSERT INTO Seasons VALUES ('summer', 3, 15, 7, 15)''')
    # conn.execute('''INSERT INTO Seasonal VALUES ('summer', 'high', 8, '08:00', '11:00')''')

    conn.execute('''CREATE TABLE IF NOT EXISTS Override (
                        Speed int NOT NULL,
                        StartTime time NOT NULL,
                        EndTime time NOT NULL
                    )''')

    conn.commit()

    conn.close()