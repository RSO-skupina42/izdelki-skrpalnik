import psycopg2
import sys
import os


class Database:
    def __init__(self):
        self.connection, self.cur = self.connect()

    def connect(self):
        try:
            hostname = os.getenv("DB_HOSTNAME")
            username = os.getenv("DB_USERNAME")
            password = os.getenv("DB_PASSWORD")
            database = os.getenv("DB_DATABASE")
            connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
            cur = connection.cursor()
            return connection, cur
        except psycopg2.OperationalError as e:
            print(f"Could not connect to Database: {e}")
            sys.exit(1)

    def disconnect_db(self):
        self.cur.close()
        self.connection.close()

    def get_table(self, query):
        try:
            self.cur.execute(query)
            rows = self.cur.fetchall()
            return rows
        except Exception:
            self.connection, self.cur = self.connect()

        return None


db = Database()


def get_db():
    return db


def close_db():
    db.disconnect_db()
