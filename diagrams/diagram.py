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

    simulation_state_db = Postgresql("Simulation Data")

    with Cluster("EC2 Environnement Physique"):
        # Sensor Dockers
        with Cluster("Capteur de mouvement d'eau"):
            flow_sensor = Docker("Capteur de Flux de l'eau") # (m^3/s)
            level_sensor = Docker("Capteur du niveau d'eau") # (m)

        with Cluster("Capteurs de qualité d'eau"):
            ph_sensor = Docker("Capteur de pH de l'eau") # (pH)
            turbidity_sensor = Docker("Capteur de turbidité de l'eau") # (nephelometric turbidity units (NTU))
            dissolved_oxygen_sensor = Docker("Capteur d'oxygène dissout") # (mg/L)
            conductivity_sensor = Docker("Capteur de conductivité de l'eau") # siemens per meter (S/m)

        with Cluster("Capteur de température"):
            temperature_sensor = Docker("Capteur de température d'eau") # (C)

        with Cluster("Capteur de pression"):
            pressure_sensor = Docker("Capteur de pression de l'eau") # psi

        # Actuator Dockers
        with Cluster("Actuators"):
            pump_actuator = Docker("Pump Actuator\n(P101)")
            valve_actuator = Docker("Valve Actuator\n(MV101)")

        # PLC EC2 instance with MQTT broker
        with Cluster("PLC Instance"):
            mqtt_broker = IotMqtt("Eclipse Mosquitto MQTT Broker")
            python_app = Python("Python PLC")

    # Connections
    sensors = [flow_sensor, level_sensor, ph_sensor, turbidity_sensor, dissolved_oxygen_sensor, conductivity_sensor, pressure_sensor, temperature_sensor]
    actuators = [pump_actuator, valve_actuator]

    # Sensor to MQTT Broker (EC2)
    for sensor in sensors:
        sensor >> Edge(label="MQTT Data") >> mqtt_broker
        simulation_state_db << Edge(label="reads") << sensor

    # MQTT Broker to Actuators via Python Application
    for actuator in actuators:
        python_app >> Edge(label="MQTT Commands") >> actuator
        actuator >> Edge(label="modifies") >> simulation_state_db

    mqtt_broker >> Edge(label="MQTT Data") >> python_app
    mqtt_broker << Edge(label="collect") << metrics
    python_app << Edge(label="collect") << metrics
