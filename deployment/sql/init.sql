--SET search_path = INF6103; -- Was causing problems in online db playground so idk...

DROP SCHEMA IF EXISTS INF6103 CASCADE;
CREATE SCHEMA INF6103;

------------------- Sensors -------------------
CREATE TABLE IF NOT EXISTS INF6103.Sensor (
    id SERIAL,
    sensor_name TEXT,
    current_reading FLOAT NOT NULL,
    ideal_value FLOAT NOT NULL,
    unit TEXT NOT NULL, -- will be retrieved from IdealValue table,
    psswd TEXT NOT NULL,
    PRIMARY KEY (id, sensor_name)
);

------------------- Actuators -------------------
CREATE TABLE IF NOT EXISTS INF6103.Actuator (
    id SERIAL,
    actuator_name TEXT,
    current_value FLOAT NOT NULL, -- is essentially the position for valves (ex: 10% open) and 'débit'' for pumps (ex: 5 cubic meters per second).
    unit TEXT NOT NULL, -- either % or volume/second,
    psswd TEXT NOT NULL,
    PRIMARY KEY (id, actuator_name)
);

------------------- Populating Sensor Table -------------------
-- T_ = Tank
-- P_ = Pipe
-- TRTM = Zone de traitement
-- TRT = Zone traitée
-- RTRTM = Boucle de retraitement
-------------------------------------------------------------------
INSERT INTO INF6103.Sensor(sensor_name, current_reading, ideal_value, unit, psswd) 
VALUES  ('T_Temperature_TRTM', 0, 15, '°C', 'yl206864'),
        ('T_Level_TRTM', 0, 450, 'L', 'yl206864'), -- can be measured with volume or height units; going for volume, same as for treated water
        ('T_Conductivity_TRTM', 0, 5000, 'S/m', 'yl206864'), -- siemens per meter; value from https://atlas-scientific.com/blog/water-quality-parameters/
        ('T_Dissolved_Oxygen_TRTM', 0, 4, 'mg/L', 'yl206864'),
        ('T_Turbidity_TRTM', 0, 9, 'NTU', 'yl206864'), -- nephelometric turbidity units; value from https://atlas-scientific.com/blog/water-quality-parameters/
        ('T_PH_TRTM', 0, 5, 'pH', 'yl206864'); -- we're assuming this waste water is acidic

INSERT INTO INF6103.Sensor(sensor_name, current_reading, ideal_value, unit, psswd) 
VALUES  ('T_Temperature_TRT', 0, 25, '°C', 'ykb965531398'), -- should be between 20 and 40 degrees, so 25 should be fine
        ('T_Level_TRT', 0, 450, 'L', 'ykb965531398'),
        ('T_Conductivity_TRT', 0, 200, 'S/m', 'ykb965531398'),
        ('T_Dissolved_Oxygen_TRT', 7, 7, 'mg/', 'ykb965531398'),
        ('T_Turbidity_TRT', 0, 0.5, 'NTU', 'ykb965531398'),
        ('T_PH_TRT', 0, 7.6, 'pH', 'ykb965531398');

-- All set to 0 because we're initializing both tanks to be nearly full, so all valves are closed, all pumps are off, and debit is null
INSERT INTO INF6103.Sensor(sensor_name, current_reading, ideal_value, unit, psswd) 
VALUES  ('P_Debit_TRT_Out', 0, 0, 'L/s', 'panenbap790319'),
        ('P_Debit_TRTM_Out', 0, 0, 'L/s', 'panenbap790319'), -- Is also input of treated tank
        ('P_Debit_RTRTM', 0, 0, 'L/s', 'panenbap790319'),
        ('P_Debit_TRTM_In', 0, 0, 'L/s', 'panenbap790319');

------------------- Populating Actuators Table -------------------
-- Valves
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit, psswd) 
VALUES  ('P_Valve_TRT_Out', 0, '%', '199019'), -- Opened at X%
        ('P_Valve_TRTM_Out', 0, '%', '199019'),
        ('P_Valve_RTRTM', 0, '%', '199019'),
        ('P_Valve_TRTM_In', 0, '%', '199019');

-- Pumps
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit, psswd) 
VALUES  ('P_Pump_TRT_Out', 0, 'L/s', '181293'), -- Also debit
        ('P_Pump_TRTM_Out', 0, 'L/s', '181293'),
        ('P_Pump_RTRTM', 0, 'L/s', '181293'),
        ('P_Pump_TRTM_In', 0, 'L/s', '181293');
