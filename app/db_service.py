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
        # print("Query:", command)
        # print("Params:", params)
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
        
    # example use to print the current reading of specific sensor: 
        # print(self.db_service.get_sensor_attributes("current_reading", SensorNames.UNTREATED_TANK_LEVEL.value)[0])
    # example use to print current reading, unit and id of specific sensor:
        # print(self.db_service.get_single_sensor_attributes("current_reading, unit, id", SensorNames.UNTREATED_TANK_LEVEL.value))
    def get_single_sensor_attributes(self, attributes: str, sensor_name: str):
        return self.command(f"SELECT {attributes} FROM INF6103.Sensor WHERE sensor_name=%s", params=(sensor_name,))[0]

    def get_single_actuator_attributes(self, attributes: str, actuator_name: str):
        return self.command(f"SELECT {attributes} FROM INF6103.Actuator WHERE actuator_name=%s", params=(actuator_name,))[0]

    def update_single_sensor_current_reading(self, value: float, sensor_name: str):
        return self.command(f"UPDATE INF6103.Sensor SET current_reading = %s WHERE sensor_name = %s", params=(value, sensor_name), modify=True)
    
    def update_single_actuator_current_value(self, value: float, actuator_name: str):
        return self.command(f"UPDATE INF6103.Actuator SET current_value = %s WHERE actuator_name = %s", params=(value, actuator_name), modify=True)

    # Reset simulation by setting all current readings of sensors and current values of actuators to 0
    def reset_all_current_values(self):
        self.command(f"UPDATE INF6103.Sensor SET current_reading = 0;", modify=True)
        self.command(f"UPDATE INF6103.Actuator SET current_value = 0;", modify=True)

    def close_connection(self):
        self._cursor.close()
        self._connection.close()
        print("Database connection closed.")