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
        self.db_service.reset_all_current_values() # Reset simulation
        self.db_service = DbService()
        self.simulation_time_loop_in_seconds = 10

    def manage_pipe(self, pipe_type:str, pump_debit: float, valve_position: float):
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
            time.sleep(1)

        # close untreated input pipe
        self.manage_pipe(PipeType.UNTREATED_INPUT, 0, 0)
        print("Tank filled to target level.")

    def treat_water(self):
        """
        Make all sensors of untreated tank (except lvl) vary towards their ideal value
        """
        




chaos_agent = Chaos_Agent()
chaos_agent.fill_untreated_tank()

    