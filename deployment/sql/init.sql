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
-- C_ = Capteur
-- TRTM = Zone de traitement
INSERT INTO INF6103.IdealValue(sensor_name, ideal_value, unit) 
VALUES  ('C_Temperature_TRTM', 15, '°C'),
        ('C_Level_TRTM', 450, 'L') -- can be measured with volume or height units; going for volume, same as for treated water
        ('C_Conductivity_TRTM', 5000, 'S/m'), -- siemens per meter; value from https://atlas-scientific.com/blog/water-quality-parameters/
        ('C_Dissolved_Oxygen_TRTM', 4, 'mg/L'),
        ('C_Turbidity_TRTM', 9, 'NTU'), -- nephelometric turbidity units; value from https://atlas-scientific.com/blog/water-quality-parameters/
        ('C_PH_TRTM', 5, 'pH'); -- we're assuming this waste water is acidic

-- TRT = Zone traitée
INSERT INTO INF6103.IdealValue(sensor_name, ideal_value, unit) 
VALUES  ('C_Temperature_TRT', 25, '°C'), -- should be between 20 and 40 degrees, so 25 should be fine
        ('C_Level_TRT', 450, 'L')
        ('C_Conductivity_TRT', 200, 'S/m'),
        ('C_Dissolved_Oxygen_TRT', 7, 'mg/'),
        ('C_Turbidity_TRT', 0.5, 'NTU'),
        ('C_PH_TRT', 7.6, 'pH');

------------------- Populating Sensor Table -------------------
-- Initially, this will essentially copy the IdealValue table entirely, but the current reading will eventually be modified during the simulation.
-- This is done so that we will always have access to IdealValue in a separate table so the PLC can compare the current reading to the IdealValue and make commands accordingly.
INSERT INTO INF6103.Sensor (sensor_name, current_reading, unit)
SELECT 
    id_val.sensor_name,
    id_val.id AS current_reading,
    id_val.unit
FROM 
    INF6103.IdealValue id_val;  

------------------- Populating Actuators Table -------------------
INSERT INTO INF6103.Actuator(actuator_name, current_value, unit) 
VALUES  ('Pompe_Entrée_Traitement', 18, 'L/s'),
        ('Valve_Sortie_Traitée', 5, '%'); 


