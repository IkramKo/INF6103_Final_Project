from app.model.iot import Iot
from app.enums.sensor_names import SensorNames
from app.enums.actuator_names import ActuatorNames
from app.enums.pipe_type import PipeType
from app.service.otel import Otel
from app.meta.decorators.logging import log_with_attributes

import time

class PLC(Iot):
    def __init__(self, name: str, password: str, broker_address: str= "localhost", port: int = 1883, db_host: str = "localhost"):
        super().__init__(name, broker_address, port, db_host)
        self.simulation_time_loop_in_seconds = 5
        self.is_connected = False
        self.client.username_pw_set(username=self.name, password=password)
        self.curr_state = {}
        self.ideal_state = {}
        ideal_values = self.db_service.command("SELECT sensor_name, ideal_value FROM INF6103.Sensor UNION ALL SELECT actuator_name, NULL FROM INF6103.Actuator;")
        for ideal_value in ideal_values:
            self.curr_state[ideal_value[0]] = 0
            self.ideal_state[ideal_value[0]] = float(ideal_value[1]) if ideal_value[1] else None
        self.meter = Otel().meter
        self.sensor_gauge = self.meter.create_gauge(f"sensor.value")
        self.sensor_histogram = self.meter.create_histogram(f"sensor.distribution")
        self.actuator_gauge = self.meter.create_gauge(f"actuator.value")
        self.actuator_histogram = self.meter.create_histogram(f"actuator.distribution")

    # Callback functions
    def on_connect(self, client, userdata, flags, rc, properties=None):
        log_with_attributes(f"Connection result code: {rc}", level="info", rc=rc)  # Includes 
        if rc == 0:
            log_with_attributes("Connected to MQTT")
            client.subscribe(self.topic)
            iot_arr = self.db_service.command("SELECT sensor_name AS name FROM INF6103.Sensor UNION ALL SELECT actuator_name as name FROM INF6103.Actuator;")
            for iot in iot_arr:
                self.client.subscribe(f"{iot[0]}")
                log_with_attributes(f"PLC is subscribed to: {iot[0]}")
            self.is_connected = True
            log_with_attributes(f"self.is_connected = {self.is_connected}")
        else:
            self.logger.error(f"Failed to connect, return code {rc}")
    
    def _on_empty_untreated_tank(self):
        """
        Fill untreated tank for treatment.
        Check if untreated tank empty.
        Open untreated input valve.
        """
        current_untreated_tank_level = self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value]
        if current_untreated_tank_level <= 0:
            untreated_tank_input_pump_debit = (self.ideal_state[SensorNames.UNTREATED_TANK_LEVEL.value] - current_untreated_tank_level)/self.simulation_time_loop_in_seconds
            log_with_attributes(f"_on_empty_untreated_tank - untreated_tank_input_pump_debit [{self.ideal_state[SensorNames.UNTREATED_TANK_LEVEL.value]} - {current_untreated_tank_level} / {self.simulation_time_loop_in_seconds}]: {untreated_tank_input_pump_debit}")
            self._manage_pipe(PipeType.UNTREATED_INPUT, untreated_tank_input_pump_debit, 1)
        return current_untreated_tank_level
    
    def _on_filled_untreated_tank(self):
        """
        Stops filling untreated tank.
        Close input pipe and retreatment pipe.
        """
        # Simulation automatically triggers water treatment when both pipes are closed.
        is_ideal = self._is_ideal(SensorNames.UNTREATED_TANK_LEVEL.value)
        log_with_attributes(f"_on_filled_untreated_tank - is_ideal: {is_ideal}")
        if is_ideal:
            self._manage_pipe(PipeType.UNTREATED_INPUT, 0, 0)
            self._manage_pipe(PipeType.RETREATEMENT, 0, 0)
        return is_ideal


    def _on_treated_water(self):
        """
        Check if untreated tank sensors values reached the ideal value.
        Open untreated tank output valve.
        """
        is_ideal = self._is_ideal(SensorNames.UNTREATED_TANK_TEMP.value) and \
            self._is_ideal(SensorNames.UNTREATED_TANK_CONDUCTIVITY.value) and \
            self._is_ideal(SensorNames.UNTREATED_TANK_DISSOLVED_OX.value) and \
            self._is_ideal(SensorNames.UNTREATED_TANK_TURBIDITY.value) and \
            self._is_ideal(SensorNames.UNTREATED_TANK_PH.value)
        
        log_with_attributes(f"_on_treated_water - {SensorNames.UNTREATED_TANK_TEMP.value}, {SensorNames.UNTREATED_TANK_CONDUCTIVITY.value}, {SensorNames.UNTREATED_TANK_DISSOLVED_OX.value},{SensorNames.UNTREATED_TANK_TURBIDITY.value}, {SensorNames.UNTREATED_TANK_PH.value} is ideal: {is_ideal}")
        if is_ideal:
            untreated_tank_output_pump_debit = (self.ideal_state[SensorNames.TREATED_TANK_LEVEL.value] - self.curr_state[SensorNames.TREATED_TANK_LEVEL.value])/self.simulation_time_loop_in_seconds
            log_with_attributes(f"untreated_tank_output_pump_debit [{self.ideal_state[SensorNames.TREATED_TANK_LEVEL.value]} - {self.curr_state[SensorNames.TREATED_TANK_LEVEL.value]} / {self.simulation_time_loop_in_seconds}]: {untreated_tank_output_pump_debit}")
            self._manage_pipe(PipeType.UNTREATED_OUTPUT, untreated_tank_output_pump_debit, 1)

    def _on_filled_treated_tank(self):
        """
        Stops filling treated tank.
        Close untreated output pipe.
        """
        is_ideal = self._is_ideal(SensorNames.TREATED_TANK_LEVEL.value)
        log_with_attributes(f"_on_filled_treated_tank - {SensorNames.TREATED_TANK_LEVEL.value} is ideal: {is_ideal}")
        if is_ideal:
            self._manage_pipe(PipeType.UNTREATED_OUTPUT, 0, 0)

    def _on_treated_tank_quality_check(self):
        """
        Check sensors in treated tank.
        If ANY sensor not at ideal value, open retreatment valve.
        If ideal values, open output valve.
        """
        is_ideal = self._is_ideal(SensorNames.TREATED_TANK_TEMP.value) and \
            self._is_ideal(SensorNames.TREATED_TANK_CONDUCTIVITY.value) and \
            self._is_ideal(SensorNames.TREATED_TANK_DISSOLVED_OX.value) and \
            self._is_ideal(SensorNames.TREATED_TANK_TURBIDITY.value) and \
            self._is_ideal(SensorNames.TREATED_TANK_PH.value)
        log_with_attributes(
            f"_on_treated_tank_quality_check - {SensorNames.TREATED_TANK_TEMP.value}, {SensorNames.TREATED_TANK_CONDUCTIVITY.value},{SensorNames.TREATED_TANK_DISSOLVED_OX.value},{SensorNames.TREATED_TANK_TURBIDITY.value},{SensorNames.TREATED_TANK_PH} is ideal: {is_ideal}")
        if is_ideal:
            treated_output_pump_debit = self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value]/self.simulation_time_loop_in_seconds
            log_with_attributes(f"_on_treated_tank_quality_check - treated_output_pump_debit [{self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value]} / {self.simulation_time_loop_in_seconds}] = {treated_output_pump_debit}")
            self._manage_pipe(PipeType.TREATED_OUTPUT, treated_output_pump_debit, 1)
        else:
            retreatment_pump_debit = (self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value] - self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value])/self.simulation_time_loop_in_seconds
            log_with_attributes(f"_on_treated_tank_quality_check - retreatment_pump_debit [({self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value]} - {self.curr_state[SensorNames.UNTREATED_TANK_LEVEL.value]}) / {self.simulation_time_loop_in_seconds}] = {retreatment_pump_debit}")
            self._manage_pipe(PipeType.RETREATEMENT, retreatment_pump_debit, 1)

    def _on_empty_treated_tank(self):
        log_with_attributes(f"_on_empty_treated_tank - current_treated_tank_level: {self.curr_state[SensorNames.TREATED_TANK_LEVEL.value]}")
        if self.curr_state[SensorNames.TREATED_TANK_LEVEL.value] <= 0:
            self._manage_pipe(PipeType.RETREATEMENT, 0, 0)
            self._manage_pipe(PipeType.TREATED_OUTPUT, 0, 0)

    def on_message(self, client, userdata, message):
        log_with_attributes(f"Received message: {message.payload.decode()} on topic {message.topic}")
        
        # The PLC will receive all the data from the sensors
        if message.topic in self.curr_state:
            value = float(message.payload.decode())
            self.curr_state[message.topic] = value

            enum_type, enum_member = self._get_enum_type(message.topic)

            otel_lbl = "sensor" if enum_type.__name__ == "SensorNames" else "actuator"
            gauge = self.sensor_gauge if enum_type.__name__ == "SensorNames" else self.actuator_gauge
            histogram = self.sensor_histogram if enum_type.__name__ == "SensorNames" else self.actuator_histogram

            # Update metrics (Gauges)
            gauge.set(value, {f"{otel_lbl}": message.topic})
            # Update histograms for distributions of values
            histogram.record(value, {f"{otel_lbl}": message.topic})

            self._on_empty_untreated_tank()
            self._on_filled_untreated_tank()
            self._on_treated_water()
            self._on_filled_treated_tank()
            self._on_treated_tank_quality_check()
            self._on_empty_treated_tank()

        else:
            self.logger.error(f"Error! {message.topic} doesn't exist")

    def _get_enum_type(self, input_string):
        """
        Determines which enum (if any) contains the given string.

        Args:
            input_string: The string to check.

        Returns:
            A tuple: (enum_type, enum_member) where enum_type is the Enum class
            and enum_member is the Enum member, or (None, None) if the string
            is not found in either enum.
        """
        for enum_class in [SensorNames, ActuatorNames]: # Add more enums here as needed
            try:
                enum_member = enum_class(input_string)
                return enum_class, enum_member
            except ValueError:
                pass  # String not found in this enum; try the next one

        return None, None  # String not found in either enum

    def _is_ideal(self, sensor: str):
        ideal_sensor = sensor.replace("TRTM", "TRT")
        log_with_attributes(f"Checking if {sensor} is ideal between: {self.curr_state[sensor]} and {self.ideal_state[ideal_sensor]}")
        return self._almost_equal(self.curr_state[sensor], self.ideal_state[ideal_sensor])

    def _almost_equal(self, first, second):
        is_almost_equal = abs(first - second) < 1
        log_with_attributes(f"Almost Equals for {first}, {second}: {is_almost_equal}")
        return is_almost_equal

    def _manage_pipe(self, pipe_type: str, pump_debit: float, valve_position: float):
        if pipe_type == PipeType.UNTREATED_INPUT and self.curr_state[ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value] is not valve_position:
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value, pump_debit)
            log_with_attributes(f"_manage_pipe - Received manage pipe request for {pipe_type}, pump_debit: {pump_debit}, valve_position: {valve_position}")
        elif pipe_type == PipeType.UNTREATED_OUTPUT and self.curr_state[ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value] is not valve_position:
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_PUMP.value, pump_debit)
            log_with_attributes(f"_manage_pipe - Received manage pipe request for {pipe_type}, pump_debit: {pump_debit}, valve_position: {valve_position}")
        elif pipe_type == PipeType.RETREATEMENT and self.curr_state[ActuatorNames.RETREATEMENT_PIPE_VALVE.value] is not valve_position:
            self.mqtt_publish(ActuatorNames.RETREATEMENT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.RETREATEMENT_PIPE_PUMP.value, pump_debit)
            log_with_attributes(f"_manage_pipe - Received manage pipe request for {pipe_type}, pump_debit: {pump_debit}, valve_position: {valve_position}")
        elif pipe_type == PipeType.TREATED_OUTPUT and self.curr_state[ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value] is not valve_position:
            self.mqtt_publish(ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value, valve_position)
            self.mqtt_publish(ActuatorNames.TREATED_TANK_OUTPUT_PIPE_PUMP.value, pump_debit)
            log_with_attributes(f"_manage_pipe - Received manage pipe request for {pipe_type}, pump_debit: {pump_debit}, valve_position: {valve_position}")
            # self.mqtt_publish(SensorNames.TREATED_TANK_OUTPUT_PIPE_DEBIT.value, pump_debit)

    def mqtt_publish(self, topic, message):
        if self.client.is_connected():
            result = self.client.publish(topic, message)
            status = result.rc
            if status == 0:
                log_with_attributes(f"mqtt_publish - Message `{message}` sent to topic `{topic}`")
            else:
                self.logger.error(f"mqtt_publish - Failed to send message to topic `{topic} with message {message}`")

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()  # Start the network loop
        # Keep the script running
        try:
            while True:
                if not self.is_connected:
                    log_with_attributes("Waiting for connection...", level="debug", is_connected=self.is_connected)
                    time.sleep(1)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()