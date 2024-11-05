from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.iot import IotMqtt
from diagrams.aws.network import VPC
from diagrams.programming.language import Python

with Diagram("IoT-Driven Water Treatment Plant with PLC", show=False, direction="LR"):

    # PLC EC2 instance with MQTT broker
    with Cluster("PLC EC2 Instance"):
        mqtt_broker = IotMqtt("Eclipse Mosquitto MQTT Broker")
        python_app = Python("Python PLC")

    # Sensor Lambdas
    with Cluster("Capteur de mouvement d'eau"):
        flow_sensor = Lambda("Capteur de Flux de l'eau") # (m^3/s)
        level_sensor = Lambda("Capteur du niveau d'eau") # (m)

    with Cluster("Capteur de qualité d'eau"):
        ph_sensor = Lambda("Capteur de pH de l'eau") # (pH)
        turbidity_sensor = Lambda("Capteur de turbidité de l'eau") # (nephelometric turbidity units (NTU))
        dissolved_oxygen_sensor = Lambda("Capteur d'oxygène dissout") # (mg/L)
        conductivity_sensor = Lambda("Capteur de conductivité de l'eau") # siemens per meter (S/m)

    with Cluster("Capteur de température"):
        temperature_sensor = Lambda("Capteur de température d'eau") # (C)

    with Cluster("Capteur de pression"):
        pressure_sensor = Lambda("Capteur de pression de l'eau") # psi

    # Actuator Lambdas
    with Cluster("Actuators"):
        pump_actuator = Lambda("Pump Actuator\n(P101)")
        valve_actuator = Lambda("Valve Actuator\n(MV101)")

    # Connections
    sensors = [flow_sensor, level_sensor, ph_sensor, turbidity_sensor, dissolved_oxygen_sensor, conductivity_sensor, pressure_sensor, temperature_sensor]
    actuators = [pump_actuator, valve_actuator]

    # Sensor to MQTT Broker (EC2)
    for sensor in sensors:
        sensor >> Edge(label="MQTT Data") >> mqtt_broker

    # MQTT Broker to Actuators via Python Application
    for actuator in actuators:
        python_app >> Edge(label="MQTT Commands") >> actuator

    mqtt_broker >> Edge(label="MQTT Data") >> python_app
