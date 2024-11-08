--SET search_path = INF6103; -- Was causing problems in online db playground so idk...

DROP SCHEMA IF EXISTS INF6103 CASCADE;
CREATE SCHEMA INF6103;

------------------- Sensors -------------------
CREATE TABLE IF NOT EXISTS INF6103.IdealValue (
    id SERIAL,
    sensor_name TEXT NOT NULL,
    ideal_value FLOAT NOT NULL,
    unit TEXT NOT NULL,
    PRIMARY KEY (id, sensor_name)
);

CREATE TABLE IF NOT EXISTS INF6103.Sensor (
    id SERIAL,
    sensor_name TEXT,
    current_reading FLOAT NOT NULL,
    unit TEXT NOT NULL, -- will be retrieved from IdealValue table
    PRIMARY KEY (id, sensor_name), -- composite key, same keys as IdealValue that way we can do 1:1 comparison with that table
    FOREIGN KEY(id, sensor_name) REFERENCES INF6103.IdealValue(id, sensor_name) ON DELETE CASCADE ON UPDATE CASCADE
);

------------------- Actuators -------------------
CREATE TABLE IF NOT EXISTS INF6103.Actuator (
    id SERIAL,
    actuator_name TEXT,
    current_value FLOAT NOT NULL, -- is essentially the position for valves (ex: 10% open) and 'débit'' for pumps (ex: 5 cubic meters per second).
    unit TEXT NOT NULL, -- either % or volume/second
    PRIMARY KEY (id, actuator_name)
);

------------------- Populating IdealValue Table -------------------
-- T_ = Tank
-- P_ = Pipe
-- TRTM = Zone de traitement
-- TRT = Zone traitée
-- RTRTM = Boucle de retraitement
-------------------------------------------------------------------
INSERT INTO INF6103.IdealValue(sensor_name, ideal_value, unit) 
VALUES  ('T_Temperature_TRTM', 15, '°C'),
        ('T_Level_TRTM', 450, 'L'), -- can be measured with volume or height units; going for volume, same as for treated water
        ('T_Conductivity_TRTM', 5000, 'S/m'), -- siemens per meter; value from https://atlas-scientific.com/blog/water-quality-parameters/
        ('T_Dissolved_Oxygen_TRTM', 4, 'mg/L'),
        ('T_Turbidity_TRTM', 9, 'NTU'), -- nephelometric turbidity units; value from https://atlas-scientific.com/blog/water-quality-parameters/
        ('T_PH_TRTM', 5, 'pH'); -- we're assuming this waste water is acidic

INSERT INTO INF6103.IdealValue(sensor_name, ideal_value, unit) 
VALUES  ('T_Temperature_TRT', 25, '°C'), -- should be between 20 and 40 degrees, so 25 should be fine
        ('T_Level_TRT', 450, 'L'),
        ('T_Conductivity_TRT', 200, 'S/m'),
        ('T_Dissolved_Oxygen_TRT', 7, 'mg/'),
        ('T_Turbidity_TRT', 0.5, 'NTU'),
        ('T_PH_TRT', 7.6, 'pH');

-- All set to 0 because we're initializing both tanks to be nearly full, so all valves are closed, all pumps are off, and debit is null
INSERT INTO INF6103.IdealValue(sensor_name, ideal_value, unit) 
VALUES  ('P_Debit_TRT_Out', 0, 'L/s'),
        ('P_Debit_TRTM_Out', 0, 'L/s'), -- Is also input of treated tank
        ('P_Debit_RTRTM', 0, 'L/s'),
        ('P_Debit_TRT_In', 0, 'L/s');

------------------- Populating Sensor Table -------------------
-- Initially, this will essentially copy the IdealValue table entirely, but the current reading will eventually be modified during the simulation.
-- This is done so that we will always have access to IdealValue in a separate table so the PLC can compare the current reading to the IdealValue and make commands accordingly.
---------------------------------------------------------------
INSERT INTO INF6103.Sensor (sensor_name, current_reading, unit)
SELECT 
    id_val.sensor_name,
    id_val.id AS current_reading,
    id_val.unit
FROM 
    INF6103.IdealValue id_val;  

------------------- Populating Actuators Table -------------------
-- Valves
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit) 
VALUES  ('P_Valve_TRT_Out', 0, '%'), -- Opened at X%
        ('P_Valve_TRTM_Out', 0, '%'),
        ('P_Valve_RTRTM', 0, '%'),
        ('P_Valve_TRT_In', 0, '%');

-- Pumps
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit) 
VALUES  ('P_Pump_TRT_Out', 0, 'L/s'), -- Also debit
        ('P_Pump_TRTM_Out', 0, 'L/s'),
        ('P_Pump_RTRTM', 0, 'L/s'),
        ('P_Pump_TRT_In', 0, 'L/s');


