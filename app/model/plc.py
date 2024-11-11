from app.model.iot import Iot
from app.enums.sensor_names import SensorNames
from app.enums.actuator_names import ActuatorNames
import time

class PLC(Iot):
    def __init__(self, name: str, password: str):
        super().__init__(name)
        self.is_connected = False
        self.client.username_pw_set(username=self.name, password=password)
        self.curr_state = {}
        self.ideal_state = {}
        ideal_values = self.db_service.command("SELECT sensor_name, ideal_value FROM INF6103.Sensor")
        for ideal_value in ideal_values:
            self.curr_state[ideal_value[0]] = 0
            self.ideal_state[ideal_value[0]] = ideal_value[1]
        print(self.curr_state)
        print(self.ideal_state)

    # Callback functions
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("Connection result code:", rc)
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.topic)
            iot_arr = self.db_service.command("SELECT sensor_name AS name FROM INF6103.Sensor UNION ALL SELECT actuator_name as name FROM INF6103.Actuator;")
            for iot in iot_arr:
                self.client.subscribe(f"{iot[0]}")
            self.is_connected = True
        else:
            print(f"Failed to connect, return code {rc}")
    
    def on_message(self, client, userdata, message):
        print(f"Received message: {message.payload.decode()} on topic {message.topic}")
        
        # The PLC will receive all the data from the sensors
        if message.topic in self.current_state:
            self.curr_state[message.topic] = message.payload.decode()

            # Deal the treated tank first cause it's the easiest
            if self._is_ideal(SensorNames.TREATED_TANK_TEMP) and \
                self._is_ideal(SensorNames.TREATED_TANK_CONDUCTIVITY) and \
                self._is_ideal(SensorNames.TREATED_TANK_DISSOLVED_OX) and \
                self._is_ideal(SensorNames.TREATED_TANK_TURBIDITY) and \
                self._is_ideal(SensorNames.TREATED_TANK_PH):
                pass

        else:
            print(f"Error! {message.topic} doesn't exist")

    def _is_ideal(self, sensor: str):
        return self._almost_equal(self.curr_state[sensor], self.ideal_state[sensor])

    def _almost_equal(self, first, second):
        if abs(first - second) < 1:
            return True
        return False

    def _manage_pipe(self, pipe_type: str, pump_debit: float, valve_position: float):
        if pipe_type == PipeType.UNTREATED_INPUT:
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value, valve_position)
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value, pump_debit)
            # self.mqtt_publish(SensorNames.UNTREATED_TANK_INPUT_PIPE_DEBIT.value, pump_debit)
        elif pipe_type == PipeType.UNTREATED_OUTPUT:
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_PUMP.value, pump_debit)
            # self.mqtt_publish(SensorNames.UNTREATED_TANK_OUTPUT_PIPE_DEBIT.value, pump_debit)
        elif pipe_type == PipeType.RETREATEMENT:
            self.mqtt_publish(ActuatorNames.RETREATEMENT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.RETREATEMENT_PIPE_PUMP.value, pump_debit)
            # self.mqtt_publish(SensorNames.RETREATEMENT_PIPE_DEBIT.value, pump_debit)
        elif pipe_type == PipeType.TREATED_OUTPUT:
            self.mqtt_publish(ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.TREATED_TANK_OUTPUT_PIPE_PUMP.value, pump_debit)
            # self.mqtt_publish(SensorNames.TREATED_TANK_OUTPUT_PIPE_DEBIT.value, pump_debit)

    def mqtt_publish(self, topic, message):
        if self.client.is_connected():
            result = self.client.publish(topic, message)
            status = result.rc
            if status == 0:
                print(f"Message `{message}` sent to topic `{self.topic}`")
            else:
                print(f"Failed to send message to topic `{self.topic}`")

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

plc = PLC("plc_usr", "plc_passwd")
plc.connect()