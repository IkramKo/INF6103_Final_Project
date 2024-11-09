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

class Chaos_Agent:
    """
    Class that simulated activity in the tanks but randomly varying the values read by the sensors.
    Modifies the database, from which sensors read values.
    """

    def __init__(self):
        self.db_service = DbService()
    
    def read_sensor_current_value(self, sensor_name: str):
        return self.db_service.command(f"SELECT current_reading FROM INF6103.Sensor WHERE sensor_name=%s", params=(sensor_name,))[0][0]

    def read_actuator_current_value(self, sensor_name: str):
        return self.db_service.command(f"SELECT current_reading FROM INF6103.Actuator WHERE sensor_name=%s", params=(sensor_name,))[0][0]

    def fill_trtm_tank(self):
        """
            - increase trtm level sensor by 45 L/s
            - trtm input pump already set to 45 L/s in init sql
            - trtm input valve already open 100% in init sql
        """
        print(self.read_sensor_current_value("T_Level_TRTM"))

chaos_agent = Chaos_Agent()
chaos_agent.fill_trtm_tank()

    