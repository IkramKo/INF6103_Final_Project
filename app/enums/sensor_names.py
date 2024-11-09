from enum import Enum

class SensorNames(Enum):
    # Untreated Tank
    UNTREATED_TANK_TEMP = 'T_Temperature_TRTM'
    UNTREATED_TANK_LEVEL = 'T_Level_TRTM'
    UNTREATED_TANK_CONDUCTIVITY = 'T_Conductivity_TRTM'
    UNTREATED_TANK_DISSOLVED_OX = 'T_Dissolved_Oxygen_TRTM'
    UNTREATED_TANK_TURBIDITY = 'T_Turbidity_TRTM'
    UNTREATED_TANK_PH = 'T_PH_TRTM'

    # Treated Tank
    TREATED_TANK_TEMP = 'T_Temperature_TRT'
    TREATED_TANK_LEVEL = 'T_Level_TRT'
    TREATED_TANK_CONDUCTIVITY = 'T_Conductivity_TRT'
    TREATED_TANK_DISSOLVED_OX = 'T_Dissolved_Oxygen_TRT'
    TREATED_TANK_TURBIDITY = 'T_Turbidity_TRT'
    TREATED_TANK_PH = 'T_PH_TRT'

    # Pipes
    UNTREATED_TANK_INPUT_PIPE_DEBIT = 'P_Pump_TRTM_In'
    UNTREATED_TANK_OUTPUT_PIPE_DEBIT = 'P_Pump_TRTM_Out'
    TREATED_TANK_OUTPUT_PIPE_DEBIT = 'P_Pump_TRT_Out'
    RETREATEMENT_PIPE_DEBIT = 'P_Pump_RTRTM'


