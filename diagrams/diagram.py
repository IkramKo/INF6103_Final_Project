from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.onprem.container import Docker
from diagrams.aws.iot import IotMqtt
from diagrams.aws.network import VPC
from diagrams.programming.language import Python
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.database import Postgresql

with Diagram("IoT-Driven Water Treatment Plant with PLC", show=False, direction="LR"):

    metrics = Prometheus("metric")
    metrics << Edge(color="firebrick", style="dashed") << Grafana("monitoring")

    with Cluster("EC2 Simulation"):
        simulation_state_db = Postgresql("Simulation Data")
        with Cluster("Capteur IOTs pour l'eau à traiter"):
            # Sensor Dockers
            with Cluster("Capteur de mouvement d'eau"):
                flow_sensor_s = Docker("Capteur de Flux de l'eau") # (m^3/s)
                level_sensor_s = Docker("Capteur du niveau d'eau") # (m)

            with Cluster("Capteurs de qualité d'eau"):
                ph_sensor_s = Docker("Capteur de pH de l'eau") # (pH)
                turbidity_sensor_s = Docker("Capteur de turbidité de l'eau") # (nephelometric turbidity units (NTU))
                dissolved_oxygen_sensor_s = Docker("Capteur d'oxygène dissout") # (mg/L)
                conductivity_sensor_s = Docker("Capteur de conductivité de l'eau") # siemens per meter (S/m)

            with Cluster("Capteur de température"):
                temperature_sensor_s = Docker("Capteur de température d'eau") # (C)

            with Cluster("Capteur de pression"):
                pressure_sensor_s = Docker("Capteur de pression de l'eau") # psi

            # Actuator Dockers
            with Cluster("Actuators"):
                pump_actuator_s = Docker("Pump Actuator")
                valve_actuator_s = Docker("Valve Actuator")

        with Cluster("Capteur IOTs pour l'eau traitée"):
            # Sensor Dockers
            with Cluster("Capteur de mouvement d'eau"):
                flow_sensor_f = Docker("Capteur de Flux de l'eau") # (m^3/s)
                level_sensor_f = Docker("Capteur du niveau d'eau") # (m)

            with Cluster("Capteurs de qualité d'eau"):
                ph_sensor_f = Docker("Capteur de pH de l'eau") # (pH)
                turbidity_sensor_f = Docker("Capteur de turbidité de l'eau") # (nephelometric turbidity units (NTU))
                dissolved_oxygen_sensor_f = Docker("Capteur d'oxygène dissout") # (mg/L)
                conductivity_sensor_f = Docker("Capteur de conductivité de l'eau") # siemens per meter (S/m)

            with Cluster("Capteur de température"):
                temperature_sensor_f = Docker("Capteur de température d'eau") # (C)

            with Cluster("Capteur de pression"):
                pressure_sensor_f = Docker("Capteur de pression de l'eau") # psi

            # Actuator Dockers
            with Cluster("Actuators"):
                pump_actuator_f = Docker("Pump Actuator")
                valve_actuator_f = Docker("Valve Actuator")

        # PLC EC2 instance with MQTT broker
        with Cluster("PLC Instance"):
            mqtt_broker = IotMqtt("Eclipse Mosquitto MQTT Broker")
            python_app = Python("Python PLC")

    # Connections
    sensors = [
        # Sensors for water to be treated
        flow_sensor_s, 
        level_sensor_s, 
        ph_sensor_s, 
        turbidity_sensor_s, 
        dissolved_oxygen_sensor_s, 
        conductivity_sensor_s, 
        pressure_sensor_s, 
        temperature_sensor_s,
        # Sensors for water after treatment
        flow_sensor_f,
        level_sensor_f,
        ph_sensor_f,
        turbidity_sensor_f,
        dissolved_oxygen_sensor_f,
        conductivity_sensor_f,
        temperature_sensor_f,
        pressure_sensor_f
    ]
    actuators = [pump_actuator_s, valve_actuator_s, pump_actuator_f, valve_actuator_f]

    # Sensor to MQTT Broker (EC2)
    for sensor in sensors:
        sensor >> Edge(label="MQTT Data") >> mqtt_broker
        simulation_state_db << Edge(label="reads") << sensor

    # MQTT Broker to Actuators via Python Application
    for actuator in actuators:
        python_app >> Edge(label="MQTT Commands") >> actuator
        simulation_state_db << Edge(label="modifies") << actuator

    mqtt_broker >> Edge(label="MQTT Data") >> python_app
    mqtt_broker << Edge(label="collect") << metrics
    python_app << Edge(label="collect") << metrics
