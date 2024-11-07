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
        simulation_state_db = Postgresql("État de Simulation")

        # Sensors and Actuators Untreated Water -> Treatment Tank
        with Cluster("Entrée dans la zone de traitement"):
            flow_sensor_1 = Docker("Capteur de débit d'eau")
            pump_actuator_1 = Docker("Pompe (Actionneur)")
            valve_actuator_1 = Docker("Valve (Actionneur)")

        # Sensors and Actuators Treated Tank -> Treatment Tank
        with Cluster("Boucle de re-traitement"):
            flow_sensor_2 = Docker("Capteur de débit d'eau")
            pump_actuator_2 = Docker("Pompe (Actionneur)")
            valve_actuator_2 = Docker("Valve (Actionneur)")

        # Sensors for Treatment Tank
        with Cluster("Zone de traitement"):
            ph_sensor_1 = Docker("Capteur de pH de l'eau") # (pH)
            turbidity_sensor_1 = Docker("Capteur de turbidité de l'eau") # (nephelometric turbidity units (NTU))
            dissolved_oxygen_sensor_1 = Docker("Capteur d'oxygène dissout") # (mg/L)
            conductivity_sensor_1 = Docker("Capteur de conductivité de l'eau") # siemens per meter (S/m)
            level_sensor_1 = Docker("Capteur du niveau d'eau") # (m)
            temperature_sensor_1 = Docker("Capteur de température d'eau") # (C)

        # Sensors for Treatment Tank -> Treated Tank
        with Cluster("Sortie de la zone de traitement"):
            flow_sensor_3 = Docker("Capteur de débit d'eau")
            pump_actuator_3 = Docker("Pompe (Actionneur)")
            valve_actuator_3 = Docker("Valve (Actionneur)")

        # Sensors for Treated Tank
        with Cluster("Zone traitée"):
            ph_sensor_2 = Docker("Capteur de pH de l'eau") # (pH)
            turbidity_sensor_2 = Docker("Capteur de turbidité de l'eau") # (nephelometric turbidity units (NTU))
            dissolved_oxygen_sensor_2 = Docker("Capteur d'oxygène dissout") # (mg/L)
            conductivity_sensor_2 = Docker("Capteur de conductivité de l'eau") # siemens per meter (S/m)
            level_sensor_2 = Docker("Capteur du niveau d'eau") # (m)
            temperature_sensor_2 = Docker("Capteur de température d'eau") # (C)

        # Sensors for Leaving Treated Tank
        with Cluster("Sortie de la zone traitée"):
            flow_sensor_4 = Docker("Capteur de débit d'eau")
            pump_actuator_4 = Docker("Pompe (Actionneur)")
            valve_actuator_4 = Docker("Valve (Actionneur)")

        # PLC EC2 instance with MQTT broker
        with Cluster("PLC Instance"):
            mqtt_broker = IotMqtt("Eclipse Mosquitto MQTT Broker")
            python_app = Python("Python PLC")

    sensors = [
        flow_sensor_1,
        flow_sensor_2,
        ph_sensor_1,
        turbidity_sensor_1,
        dissolved_oxygen_sensor_1,
        conductivity_sensor_1,
        level_sensor_1,
        temperature_sensor_1,
        flow_sensor_3,
        ph_sensor_2,
        turbidity_sensor_2,
        dissolved_oxygen_sensor_2,
        conductivity_sensor_2,
        level_sensor_2,
        temperature_sensor_2,
        flow_sensor_4
    ]

    actuators = [
        pump_actuator_1,
        valve_actuator_1,
        pump_actuator_2,
        valve_actuator_2,
        pump_actuator_3,
        valve_actuator_3,
        pump_actuator_4,
        valve_actuator_4
    ]

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