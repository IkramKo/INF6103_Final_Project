from model.iot import Iot
import time

class Actuator(Iot):
    def __init__(self, name: str):
        super().__init__(name)
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
            client.loop_stop()
            client.disconnect()

    # Callback functions
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("Connection result code:", rc)
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.topic)
            self.is_connected = True
        else:
            print(f"Failed to connect, return code {rc}")
    
    def on_message(self, client, userdata, message):
        print(f"Received message: {message.payload.decode()} on topic {message.topic}")
        


