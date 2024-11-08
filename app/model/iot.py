from db_service import DbService

class IotDevice():
    def __init__(self, name: str):
        self.broker_address = "localhost"
        self.port = 1883
        self.name = name
        self.topic = name

        # Connect to PGSQL
        self.db_service = DbService()
        # Retrieve username/pwd
        self.passwd = self.db.query("SELECT psswd FROM INF6103.Sensor WHERE sensor_name='T_Temperature_TRTM';")[0]
        # Connect to the MQTT Broker