from enum import Enum

class ActuatorNames(Enum):
    # Valves
    UNTREATED_TANK_INPUT_PIPE_VALVE = 'P_Valve_TRTM_In'
    UNTREATED_TANK_OUTPUT_PIPE_VALVE = 'P_Valve_TRTM_Out'
    TREATED_TANK_OUTPUT_PIPE_VALVE = 'P_Valve_TRT_Out'
    RETREATEMENT_PIPE_VALVE = 'P_Valve_RTRTM'

    # Pumps
    UNTREATED_TANK_INPUT_PIPE_PUMP = 'P_Pump_TRTM_In'
    UNTREATED_TANK_OUTPUT_PIPE_PUMP = 'P_Pump_TRTM_Out'
    TREATED_TANK_OUTPUT_PIPE_PUMP = 'P_Pump_TRT_Out'
    RETREATEMENT_PIPE_PUMP = 'P_Pump_RTRTM'