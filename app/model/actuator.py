from app.model.iot import Iot
import time
from app.meta.decorators.logging import log_with_attributes

class Actuator(Iot):
    def __init__(self, name: str, broker_address: str= "localhost", port: int = 1883, db_host: str = "localhost"):
        super().__init__(name, broker_address, port, db_host, iot_type="actuator")
        self.is_connected = False
    
    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()  # Start the network loop

        # Keep the script running
        try:
            while True:
                if not self.is_connected:
                    print("Waiting for connection...")
                    time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()

    # Callback functions
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("Connection result code:", rc)
        if rc == 0:
            log_with_attributes(f"Connected to MQTT Broker with topic: {self.topic}")
            client.subscribe(self.topic)
            self.is_connected = True
        else:
            print(f"Failed to connect, return code {rc}")
    
    def on_message(self, client, userdata, message):
        log_with_attributes(f"Received message: {message.payload.decode()} on topic {message.topic}")
        self.update_actuator_value(float(message.payload.decode()))
    
    def update_actuator_value(self, new_value: float):
        try:
            # SQL query with parameterization
            query = "UPDATE INF6103.Actuator SET current_value = %s WHERE actuator_name = %s"
            params = (new_value, self.name)  # Correct tuple for parameters

            # Execute the query and commit changes
            self.db_service.command(query, params=params, modify=True)
            log_with_attributes(f"Actuator {self.name} updated to {new_value} with {query} and {params}")

        except Exception as e:
            log_with_attributes(f"Error updating actuator: {e}", level="error")