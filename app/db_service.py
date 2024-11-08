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

    def command(self, command: str, params=None, fetch=True, modify=False):
        print("Query:", command)
        print("Params:", params)
        try:
            self._cursor.execute(command, params) # Use parameterized queries

            if modify:
                self._connection.commit()  # Commit changes for INSERT, UPDATE, DELETE
                return None  # Or return a success message

            if fetch:
                return self._cursor.fetchall()
            else: 
                return None # For queries that don't return results (e.g., CREATE TABLE)

        except Exception as e:
            self._connection.rollback() # Rollback on error for modify operations
            print(f"Database query error: {e}")
            return None # Return None to indicate an error

    def close_connection(self):
        self._cursor.close()
        self._connection.close()
        print("Database connection closed.")