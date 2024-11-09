from db_service import DbService
######################################################## SIMULATION ########################################################
"""
    1. To be treated tank fills up
        - all sensors to 0
    2. Level sensor starts to increase until 450 liters
        - level sensor remains at 450 the whole time
        - all other tank sensors init to their ideal value
    3. _TRTM Sensors start varying towards the ideal value of the _TRT version of the sensor over 1-2 minutes
        - once ideal value hit, stop variation
    4. Once all ideal values hit, wait a lil
        - enable valves and pumps and sensor of _TRTM_Out
        - drain ONLY the lvl sensor of _TRTM tank until it hits 0
        - at the same time, lvl sensor of _TRT tank increases at same rate as _TRTM tank empties
        - once empty _TRTM and _TRT full, reset all current readings of _TRTM to 0
    5. Init all sensors of _TRT to ideal value
        - wait a lil
    6. Empty _TRT tank
        - enable valves and pumps and sensor of _TRT_Out
        - once drained, reset sensors to 0
    7. Restart loop
"""
############################################################################################################################
from enums.sensor_names import SensorNames
from enums.actuator_names import ActuatorNames
from enum import Enum
import time

class TankType(Enum):
    TREATED = 'treated'
    UNTREATED = 'untreated'

class PipeType(Enum):
    TREATED_OUTPUT = 'treated_output'
    UNTREATED_INPUT = 'untreated_input'
    UNTREATED_OUTPUT = 'untreated_output'
    RETREATEMENT = 'retreatment'

class Chaos_Agent:
    """
    Class that simulated activity in the tanks but randomly varying the values read by the sensors.
    Modifies the database, from which sensors read values.
    """
    def __init__(self):
        self.db_service = DbService()
        self.db_service.reset_all_current_values() # Reset simulation
        self.simulation_time_loop_in_seconds = 10
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

    def manage_pipe(self, pipe_type: str, pump_debit: float, valve_position: float):
        if pipe_type == PipeType.UNTREATED_INPUT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value)
            self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.UNTREATED_TANK_INPUT_PIPE_DEBIT.value)
        elif pipe_type == PipeType.UNTREATED_OUTPUT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_PUMP.value)
            self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.UNTREATED_TANK_OUTPUT_PIPE_DEBIT.value)
        elif pipe_type == PipeType.RETREATEMENT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.RETREATEMENT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.RETREATEMENT_PIPE_PUMP.value)
            self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.RETREATEMENT_PIPE_DEBIT.value)
        elif pipe_type == PipeType.TREATED_OUTPUT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.TREATED_TANK_OUTPUT_PIPE_PUMP.value)
            self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.TREATED_TANK_OUTPUT_PIPE_DEBIT.value)

    def fill_untreated_tank(self):
        """
        Consider current tank level, target tank level and simulation time loop
        Calculate increase rate
        Open valve
        Set input pump to that rate and fill up tank
        Close pump
        """
        current_tank_lvl, target_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading, ideal_value", SensorNames.UNTREATED_TANK_LEVEL.value)
        increase_rate = (target_tank_lvl - current_tank_lvl)/self.simulation_time_loop_in_seconds

        # open untreated tank input pipe
        self.manage_pipe(PipeType.UNTREATED_INPUT, increase_rate, 100)
       
        while current_tank_lvl < target_tank_lvl:
            current_tank_lvl = round(current_tank_lvl + increase_rate, 2)
            self.db_service.update_single_sensor_current_reading(current_tank_lvl, SensorNames.UNTREATED_TANK_LEVEL.value)
            print("Current untreated tank lvl (filling up phase): ", current_tank_lvl)
            time.sleep(1)

        # close untreated input pipe
        self.manage_pipe(PipeType.UNTREATED_INPUT, 0, 0)
        print("Untreated tank filled to target level. Beginning treatment.")
    
    def init_tank_sensors_to_their_ideal_values(self, tank_type: str):
        """
        Init tank sensors (except level) to their ideal values
        """
        str_tank_sensor_names = ""
        if tank_type == TankType.UNTREATED:
            str_tank_sensor_names = ', '.join(f"'{sensor}'" for sensor in self.untreated_tank_sensor_names)
        elif tank_type == TankType.TREATED:
            str_tank_sensor_names = ', '.join(f"'{sensor}'" for sensor in self.treated_tank_sensor_names)
        self.db_service.command(f"UPDATE INF6103.Sensor SET current_reading = ideal_value WHERE sensor_name IN ({str_tank_sensor_names})", modify=True)

    def _set_untreated_tank_sensor_data(self):
        """
        Retrieve current and ideal values and store in dict to make following manips easier
        Calculate increase rate of each sensor
        """
        sensor_target_vals = {}

        for untreated_sensor_name in self.untreated_tank_sensor_names:
            # retrieves type (oxygen, turbidity, etc)
            untreated_sensor_type = untreated_sensor_name.split('_')[-2]
            equivalent_treated_sensor = [sensor_type for sensor_type in self.treated_tank_sensor_names if untreated_sensor_type in sensor_type][0]

            # too tired to do a proper try catch so instead, SensorNames(equivalent_treated_sensor) is done to make sure element exists, if not, error raised automatically
            curr_val = self.db_service.get_single_sensor_attributes("current_reading", SensorNames(equivalent_treated_sensor).value)[0]
            id_val = self.db_service.get_single_sensor_attributes("ideal_value", SensorNames(equivalent_treated_sensor).value)[0]
            increase_rate = (id_val - curr_val)/self.simulation_time_loop_in_seconds
            sensor_target_vals[untreated_sensor_name] = (curr_val, id_val, increase_rate)

        return sensor_target_vals
    
    def _increment_untreated_tank_sensor_values(self, sensor_target_vals: dict):
        for sensor_name, vals in sensor_target_vals.items():
            curr_val, id_val, increase_rate = vals
            # dont increment sensors that have already reached their ideal value
            if curr_val < id_val:
                current_reading = round(curr_val + increase_rate, 2)
                sensor_target_vals[sensor_name] = (current_reading, id_val, increase_rate)
                self.db_service.update_single_sensor_current_reading(current_reading, sensor_name)
            print(f"Untreated tank {sensor_name} sensor value (treatment phase): ", self.db_service.get_single_sensor_attributes("current_reading", sensor_name))

    def treat_water(self):
        """
        Initialize all UNTREATED sensors to their ideal value
        Get ideal values of TREATED sensor counterparts
        Make all sensors of untreated tank (except lvl) vary towards their ideal TREATED value
        """
        self.init_tank_sensors_to_their_ideal_values(TankType.UNTREATED)
        sensor_target_vals = self._set_untreated_tank_sensor_data()

        all_sensors_at_treated_ideal_val = True
        while all_sensors_at_treated_ideal_val:
            # increment
            self._increment_untreated_tank_sensor_values(sensor_target_vals)

            # check if all have reached id val
            # all(flag == 0 for (_, _, flag) in items) -- thank you stackoverflow i owe you my life
            all_sensors_at_treated_ideal_val = not all(curr_val >= id_val for curr_val, id_val, _ in sensor_target_vals.values())
            time.sleep(1)

        print("Water treated. Transfering to quality check tank.")

    def fill_treated_tank(self):
        """
        Open untreated tank output pipe
        Fill treated tank
        Simultaneously empty untreated tank
        once on empty and the other full, close pipe
        init treated tank sensors
        wait 5 seconds to simulate quality check
        """
        current_treated_tank_lvl, target_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading, ideal_value", SensorNames.TREATED_TANK_LEVEL.value)
        treated_tank_increase_rate = (target_tank_lvl - current_treated_tank_lvl)/self.simulation_time_loop_in_seconds
        current_untreated_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.UNTREATED_TANK_LEVEL.value)[0]

        # open untreated tank OUTPUT pipe
        self.manage_pipe(PipeType.UNTREATED_OUTPUT, treated_tank_increase_rate, 100)
       
        while current_treated_tank_lvl < target_tank_lvl and current_untreated_tank_lvl > 0:
            current_treated_tank_lvl = round(current_treated_tank_lvl + treated_tank_increase_rate, 2)
            current_untreated_tank_lvl = round(current_untreated_tank_lvl - treated_tank_increase_rate, 2) # empty untreated tank at same rate as treated is filling up
            print("Current treated tank lvl (post treatment phase): ", current_treated_tank_lvl, "Current untreated tank lvl (post treatment phase): ", current_untreated_tank_lvl)

            self.db_service.update_single_sensor_current_reading(current_treated_tank_lvl, SensorNames.TREATED_TANK_LEVEL.value)
            self.db_service.update_single_sensor_current_reading(current_untreated_tank_lvl, SensorNames.UNTREATED_TANK_LEVEL.value)

            time.sleep(1)

        # close untreated output pipe
        self.manage_pipe(PipeType.UNTREATED_OUTPUT, 0, 0)
        print("Treated tank filled to target level. Beginning quality check.")



chaos_agent = Chaos_Agent()
chaos_agent.fill_untreated_tank()
chaos_agent.treat_water()
chaos_agent.fill_treated_tank()

    