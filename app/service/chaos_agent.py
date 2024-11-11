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
from app.service.db_service import DbService
from app.enums.sensor_names import SensorNames
from app.enums.actuator_names import ActuatorNames
from app.enums.pipe_type import PipeType
from app.enums.tank_type import TankType
import time

class Chaos_Agent:
    """
    Class that simulated activity in the tanks but randomly varying the values read by the sensors.
    Modifies the database, from which sensors read values.
    """
    def __init__(self):
        self.db_service = DbService()
        self.db_service.reset_all_current_values() # Reset simulation
        self.simulation_time_loop_in_seconds = 5
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

    def fill_untreated_tank_when_input_valve_active(self):
        """
        Consider current tank level, target tank level and simulation time loop
        Calculate increase rate
        Open valve
        Set input pump to that rate and fill up tank
        Close pump
        """
        # to move to plc #
        init_current_tank_lvl, init_target_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading, ideal_value", SensorNames.UNTREATED_TANK_LEVEL.value)
        print("INIT CURRENT INTREATED TANK LEVEL: ", init_current_tank_lvl, "INIT_TARGET INTREATED TANK LEVEL: ", init_target_tank_lvl)
        untreated_input_pump_debit = (init_target_tank_lvl - init_current_tank_lvl)/self.simulation_time_loop_in_seconds
        self.manage_pipe(PipeType.UNTREATED_INPUT, untreated_input_pump_debit, 1) # set to 1 for valve position to activate
        ##################


        untreated_input_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value)[0]       
        while untreated_input_valve_status: # once plc done, replace this with while actuator of input pipe valve open
            # Get current level and increase rate
            increase_rate = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value)[0]
            self.db_service.update_single_actuator_current_value(increase_rate, ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value) # Update sensor according to actuator value
            current_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading, ideal_value", SensorNames.UNTREATED_TANK_LEVEL.value)[0]

            current_tank_lvl = round(current_tank_lvl + increase_rate, 2)
            self.db_service.update_single_sensor_current_reading(current_tank_lvl, SensorNames.UNTREATED_TANK_LEVEL.value)
            print("Current untreated tank lvl (filling up phase): ", current_tank_lvl, "ideal value", init_target_tank_lvl)
            time.sleep(1)

            # to remove once integration done
            if current_tank_lvl >= init_target_tank_lvl:
                self.manage_pipe(PipeType.UNTREATED_INPUT, 0, 0) # set to 0 for valve position to close    
            
            # retrieve valve status again
            untreated_input_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value)[0]
            
        print("Untreated tank filled to target level. Beginning treatment.") # move these statements to plc during integration
    
    def _init_tank_sensors_to_their_ideal_values(self, tank_type: str):
        """
        Init tank sensors (except level) to their ideal values
        """
        str_tank_sensor_names = ""
        if tank_type == TankType.UNTREATED:
            str_tank_sensor_names = ', '.join(f"'{sensor}'" for sensor in self.untreated_tank_sensor_names)
        elif tank_type == TankType.TREATED:
            str_tank_sensor_names = ', '.join(f"'{sensor}'" for sensor in self.treated_tank_sensor_names)
        self.db_service.command(f"UPDATE INF6103.Sensor SET current_reading = ideal_value WHERE sensor_name IN ({str_tank_sensor_names});", modify=True)

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

    def treat_water(self): # trigger when input AND output valves are closed
        """
        Initialize all UNTREATED sensors to their ideal value
        Get ideal values of TREATED sensor counterparts
        Make all sensors of untreated tank (except lvl) vary towards their ideal TREATED value
        """
        self._init_tank_sensors_to_their_ideal_values(TankType.UNTREATED)
        sensor_target_vals = self._set_untreated_tank_sensor_data()

        all_sensors_at_treated_ideal_val = True
        untreated_output_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value)[0]
        untreated_intput_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value)[0]

        while all_sensors_at_treated_ideal_val and not (untreated_output_valve_status or untreated_intput_valve_status): #
            # increment
            self._increment_untreated_tank_sensor_values(sensor_target_vals)

            # check if all have reached id val
            # all(flag == 0 for (_, _, flag) in items) -- thank you stackoverflow i owe you my life
            all_sensors_at_treated_ideal_val = not all(curr_val >= id_val for curr_val, id_val, _ in sensor_target_vals.values())
            time.sleep(1)

            # Retrieve valve status again to stop as soon as either of them opens (treatment interrupted if so)
            untreated_output_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value)[0]

        print("Water treated. Transfering to quality check tank.")

    def fill_treated_tank_when_untreated_output_valve_open(self): #trigger when untreated output valve open
        """
        Open untreated tank output pipe
        Fill treated tank
        Simultaneously empty untreated tank
        once on empty and the other full, close pipe
        """
        # to move to plc #
        init_current_treated_tank_lvl, init_target_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading, ideal_value", SensorNames.TREATED_TANK_LEVEL.value)
        untreated_output_pump_debit = (init_target_tank_lvl - init_current_treated_tank_lvl)/self.simulation_time_loop_in_seconds
        self.manage_pipe(PipeType.UNTREATED_OUTPUT, untreated_output_pump_debit, 1) # set to 1 for valve position to activate
        ##################

        # Get values of untreated sensors for first iteration of loop
        untreated_output_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value)[0]
        current_untreated_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.UNTREATED_TANK_LEVEL.value)[0]

        while untreated_output_valve_status and current_untreated_tank_lvl > 0:
            # Get current tank levels and increase rate
            treated_tank_increase_rate = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_PUMP.value)[0]
            self.db_service.update_single_sensor_current_reading(treated_tank_increase_rate, SensorNames.UNTREATED_TANK_OUTPUT_PIPE_DEBIT)
            current_treated_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.TREATED_TANK_LEVEL.value)[0]
            current_untreated_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.UNTREATED_TANK_LEVEL.value)[0]
            
            # Update current tank levels
            current_treated_tank_lvl = round(current_treated_tank_lvl + treated_tank_increase_rate, 2)
            current_untreated_tank_lvl = round(current_untreated_tank_lvl - treated_tank_increase_rate, 2) # empty untreated tank at same rate as treated is filling up
            print("Current treated tank lvl (post treatment phase): ", current_treated_tank_lvl, "Current untreated tank lvl (post treatment phase): ", current_untreated_tank_lvl)

            self.db_service.update_single_sensor_current_reading(current_treated_tank_lvl, SensorNames.TREATED_TANK_LEVEL.value)
            self.db_service.update_single_sensor_current_reading(current_untreated_tank_lvl, SensorNames.UNTREATED_TANK_LEVEL.value)

            time.sleep(1)

        print("Treated tank filled to target level. Beginning quality check.")
        self._init_tank_sensors_to_their_ideal_values(TankType.TREATED)

    ########################################### TO REMOVE ONCE INTEGRATION WITH PLC DONE ###########################################
    def manage_pipe(self, pipe_type: str, pump_debit: float, valve_position: float):
        if pipe_type == PipeType.UNTREATED_INPUT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.UNTREATED_TANK_INPUT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.UNTREATED_TANK_INPUT_PIPE_PUMP.value)
            # self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.UNTREATED_TANK_INPUT_PIPE_DEBIT.value)
        elif pipe_type == PipeType.UNTREATED_OUTPUT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.UNTREATED_TANK_OUTPUT_PIPE_PUMP.value)
            # self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.UNTREATED_TANK_OUTPUT_PIPE_DEBIT.value)
        elif pipe_type == PipeType.RETREATEMENT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.RETREATEMENT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.RETREATEMENT_PIPE_PUMP.value)
            # self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.RETREATEMENT_PIPE_DEBIT.value)
        elif pipe_type == PipeType.TREATED_OUTPUT:
            self.db_service.update_single_actuator_current_value(valve_position, ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value)
            self.db_service.update_single_actuator_current_value(pump_debit, ActuatorNames.TREATED_TANK_OUTPUT_PIPE_PUMP.value)
            # self.db_service.update_single_sensor_current_reading(pump_debit, SensorNames.TREATED_TANK_OUTPUT_PIPE_DEBIT.value)
            
    def _get_tank_level_variation_rates(self, treated_output_valve_status: bool, retreatment_valve_status: bool):
        """
        Gets the decrease rate of treated tank level depending on both retreatment and output debit
        Gets the increase rate of untreated tank based on retreatment
        """
        # Get decrease rates
        decrease_rate_from_output_pipe = 0
        decrease_rate_from_retreatment_pipe = 0

        if treated_output_valve_status:
            decrease_rate_from_output_pipe = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.TREATED_TANK_OUTPUT_PIPE_PUMP.value)[0]
            # Update the sensor manually as well in case it wasnt properly done in other steps
            self.db_service.update_single_sensor_current_reading(decrease_rate_from_output_pipe, SensorNames.TREATED_TANK_OUTPUT_PIPE_DEBIT.value)
        if retreatment_valve_status:
            decrease_rate_from_retreatment_pipe = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.RETREATEMENT_PIPE_PUMP.value)[0]
            self.db_service.update_single_sensor_current_reading(decrease_rate_from_retreatment_pipe, SensorNames.RETREATEMENT_PIPE_DEBIT.value)
        
        # Set tank decrease rate to sum of both decrease rates
        treated_tank_decrease_rate = decrease_rate_from_output_pipe + decrease_rate_from_retreatment_pipe
        return (treated_tank_decrease_rate, decrease_rate_from_retreatment_pipe)

    def empty_treated_tank(self):
        """
        check values of the output valve actuator; if on, empty tank
        """    
        # to move to plc #
        current_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.TREATED_TANK_LEVEL.value)[0]
        treated_tank_output_pump_debit = current_tank_lvl/self.simulation_time_loop_in_seconds
        self.manage_pipe(PipeType.RETREATEMENT, treated_tank_output_pump_debit, 1) # set to 1 for valve position to activate
        ##################

        # Wait a bit to show status in graph
        time.sleep(5)

        # Check which of the output valves is opened
        treated_output_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value)[0]
        retreatment_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.RETREATEMENT_PIPE_VALVE.value)[0]
    
        current_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.TREATED_TANK_LEVEL.value)[0]
        while (treated_output_valve_status or retreatment_valve_status) and current_tank_lvl > 0: # Since we're emptying it, it makes no sense to keep decreasing after it hits 0
            # Get current tank level and decrease
            current_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.TREATED_TANK_LEVEL.value)[0]

            # Calculate treated tank increase level (done wach loop in case one of the pipes was closed mid loop)
            treated_tank_decrease_rate, untreated_tank_increase_level = self._get_tank_level_variation_rates(treated_output_valve_status, retreatment_valve_status)
            current_tank_lvl = round(current_tank_lvl - treated_tank_decrease_rate, 2)
            self.db_service.update_single_sensor_current_reading(current_tank_lvl, SensorNames.TREATED_TANK_LEVEL.value)


            current_untreated_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.UNTREATED_TANK_LEVEL.value)[0]
            current_untreated_tank_lvl = round(current_untreated_tank_lvl + untreated_tank_increase_level, 2)
            self.db_service.update_single_sensor_current_reading(current_untreated_tank_lvl, SensorNames.UNTREATED_TANK_LEVEL.value)

            # Log tank levels
            print("Current treated tank lvl: ", current_tank_lvl)
            if retreatment_valve_status: print("Current untreated tank lvl (retreatment phase): ", current_untreated_tank_lvl)
            time.sleep(1)

            # retrieve status of valves again
            treated_output_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.TREATED_TANK_OUTPUT_PIPE_VALVE.value)[0]
            retreatment_valve_status = self.db_service.get_single_actuator_attributes("current_value", ActuatorNames.RETREATEMENT_PIPE_VALVE.value)[0]

        current_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.TREATED_TANK_LEVEL.value)[0]
        current_untreated_tank_lvl = self.db_service.get_single_sensor_attributes("current_reading", SensorNames.UNTREATED_TANK_LEVEL.value)[0]


        print("Treated tank emptied into reservoir.")


        
def main():
    chaos_agent = Chaos_Agent()
    chaos_agent.fill_untreated_tank_when_input_valve_active()
    chaos_agent.treat_water()
    chaos_agent.fill_treated_tank_when_untreated_output_valve_open()
    chaos_agent.empty_treated_tank()

if __name__ == "__main__":
    main()

    