from model.iot import Iot

class Sensor(Iot):
    def __init__(self, name: str):
        super().__init__(name)
    
    def mqtt_publish(self):
        self.client.connect(self.broker_address, self.port)
        message = self.db_service.command(f"SELECT current_reading FROM INF6103.Sensor WHERE sensor_name=%s", params=(f"{self.name}",))[0][0]
        result = self.client.publish(self.topic, message)
        status = result.rc
        if status == 0:
            print(f"Message `{message}` sent to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic `{self.topic}`")
        self.client.disconnect()
