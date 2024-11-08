from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import Postgresql
from diagrams.programming.flowchart import Database

with Diagram("Water Treatment Plant Database", show=False, direction="TB"):
    with Cluster("INF6103 Database Schema"):
        ideal_value_table = Database("IdealValue")
        sensor_table = Database("Sensor")
        actuator_table = Database("Actuator")

    ideal_value_table >> Edge(label="1:1 (id, sensor_name)", color="blue") >> sensor_table
    sensor_table << Edge(label="foreign key", color="black") << ideal_value_table
    actuator_table