from app.service.db_service import DbService
import paho.mqtt.client as mqtt

class Iot():
    def __init__(self, name: str, broker_address: str= "localhost", port: int = 1883, db_host: str = "localhost", iot_type: str = "sensor"):
        self.broker_address = broker_address
        self.port = port
        self.name = name
        self.topic = name

        # Connect to PGSQL
        self.db_service = DbService(db_host=db_host)
        # Retrieve username/pwd
        table = "INF6103.Sensor" if iot_type == "sensor" else "INF6103.Actuator"
        column = "sensor_name" if iot_type == "sensor" else "actuator_name"
        self.passwd_rows = self.db_service.command(f"SELECT psswd FROM {table} WHERE {column}=%s", params=(f"{self.name}",))

        if self.passwd_rows: # IMPORTANT: Check for errors/None result
            self.passwd = self.passwd_rows[0][0]  # Extract the password string from the result
        else:
             self.passwd = None  # Or handle the error appropriately
             # For example, raise an exception or use a default password.
        print(self.name, self.passwd)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(self.name, self.passwd)
    
    def mqtt_connect(self):
        pass

    def mqtt_publish(self, message: str):
        pass