from app.service.db_service import DbService
import paho.mqtt.client as mqtt

class Iot():
    def __init__(self, name: str):
        self.broker_address = "localhost"
        self.port = 1883
        self.name = name
        self.topic = name

        # Connect to PGSQL
        self.db_service = DbService()
        # Retrieve username/pwd
        self.passwd_rows = self.db_service.command(f"SELECT psswd FROM INF6103.Sensor WHERE sensor_name=%s", params=(f"{self.name}",))
        if self.passwd_rows: # IMPORTANT: Check for errors/None result
            self.passwd = self.passwd_rows[0][0]  # Extract the password string from the result
        else:
             self.passwd = None  # Or handle the error appropriately
             # For example, raise an exception or use a default password.
             
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(self.name, self.passwd)
    
    def mqtt_connect(self):
        pass

    def mqtt_publish(self, message: str):
        pass