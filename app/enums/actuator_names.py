"""
------------------- Populating Actuators Table -------------------
-- Valves
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit, psswd) 
VALUES  ('P_Valve_TRT_Out', 0, '%', 'P_Valve_TRT_Out_psswd'), -- Opened at X%
        ('P_Valve_TRTM_Out', 0, '%', 'P_Valve_TRTM_Out_psswd'),
        ('P_Valve_RTRTM', 0, '%', 'P_Valve_RTRTM_psswd'),
        ('P_Valve_TRTM_In', 100, '%', 'P_Valve_TRT_In_psswd');

-- Pumps
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit, psswd) 
VALUES  ('P_Pump_TRT_Out', 0, 'L/s', 'P_Pump_TRT_Out_psswd'), -- Also debit
        ('P_Pump_TRTM_Out', 0, 'L/s', 'P_Pump_TRTM_Out_psswd'),
        ('P_Pump_RTRTM', 0, 'L/s', 'P_Pump_RTRTM_psswd'),
        ('P_Pump_TRTM_In', 45, 'L/s', 'P_Pump_TRT_In_psswd');

UNTREATED_TANK_INPUT_PIPE_DEBIT = 'P_Pump_TRTM_In'
UNTREATED_TANK_OUTPUT_PIPE_DEBIT = 'P_Pump_TRTM_Out'
TREATED_TANK_OUTPUT_PIPE_DEBIT = 'P_Pump_TRT_Out'
RETREATEMENT_PIPE_DEBIT = 'P_Pump_RTRTM'
"""
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