from typing import Any
import asyncio
import psycopg2
from psycopg2 import sql

class DbService:
    # Params used to connect to db
    db_params = {
        "host": "localhost",
        "port": "5432",
        "database": "mydb",
        "user": "myuser",
        "password": "mypassword"
    }

    def __init__(self):
        try:
            self._connection = psycopg2.connect(**self.db_params)
            self._cursor = self._connection.cursor()
            
            # Establish and test connection to db
            self._cursor.execute("SELECT version();")
            db_version = self._cursor.fetchone()
            print(f"Connected to PostgreSQL database. Version: {db_version}")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def query(self, command: str):
        try:
            self._cursor.execute(command)
            return self._cursor.fetchall()
        except Exception as e:
            print(f"Error seeding the database: {e}")

    def close_connection(self):
        self._cursor.close()
        self._connection.close()
        print("Database connection closed.")