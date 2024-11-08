--SET search_path = INF6103; -- Was causing problems in online db playground so idk...

DROP SCHEMA IF EXISTS INF6103 CASCADE;
CREATE SCHEMA INF6103;

------------------- Sensors -------------------
CREATE TABLE IF NOT EXISTS INF6103.IdealValue (
    id SERIAL,
    sensor_name TEXT NOT NULL,
    ideal_value SMALLINT NOT NULL,
    unit TEXT NOT NULL,
    PRIMARY KEY (id, sensor_name)
);

CREATE TABLE IF NOT EXISTS INF6103.Sensor (
    id SERIAL,
    sensor_name TEXT,
    current_reading SMALLINT NOT NULL,
    unit TEXT NOT NULL, -- will be retrieved from IdealValue table
    PRIMARY KEY (id, sensor_name), -- composite key, same keys as IdealValue that way we can do 1:1 comparison with that table
    FOREIGN KEY(id, sensor_name) REFERENCES INF6103.IdealValue(id, sensor_name) ON DELETE CASCADE ON UPDATE CASCADE
);

------------------- Actuators -------------------
CREATE TABLE IF NOT EXISTS INF6103.Actuator (
    id SERIAL,
    actuator_name TEXT,
    current_value SMALLINT NOT NULL, -- is essentially the position for valves (ex: 10% open) and 'débit'' for pumps (ex: 5 cubic meters per second).
    unit TEXT NOT NULL, -- either % or volume/second
    PRIMARY KEY (id, actuator_name)
);

------------------- Populating IdealValue Table -------------------
INSERT INTO INF6103.IdealValue(sensor_name, ideal_value, unit) 
VALUES  ('Température', 2, '°C'),
        ('Débit', 5, 'L/s'); 

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


