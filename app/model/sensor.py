from model.iot import Iot

class Sensor(Iot):
    def __init__(self, name: str):
        super().__init__(name)
    
    def mqtt_publish(self):
        if self.client.is_connected():
            message = self.db_service.command(f"SELECT current_reading FROM INF6103.Sensor WHERE sensor_name=%s", params=(f"{self.name}",))[0][0]
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
                if not self.is_connected:
                    print("Waiting for connection...")
                    time.sleep(1)
                else:
                    self.mqtt_publish()
                    time.sleep(1)
        except KeyboardInterrupt:
            client.loop_stop()
            client.disconnect()