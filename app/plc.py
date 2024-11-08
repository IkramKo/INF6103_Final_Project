# import time
# import paho.mqtt.client as mqtt

# # MQTT broker settings
# broker_address = "localhost"  # or "mosquitto" if inside a Docker network
# port = 1883
# topic = "test/topic"
# # Credentials
# username = "T_Temperature_TRTM"
# password = "T_Temperature_TRTM_psswd"

# # Connection status flag
# is_connected = False

# # Callback functions
# def on_connect(client, userdata, flags, rc, properties=None):
#     global is_connected
#     print("Connection result code:", rc)
#     if rc == 0:
#         print("Connected to MQTT Broker!")
#         client.subscribe(topic)
#         is_connected = True
#     else:
#         print(f"Failed to connect, return code {rc}")

# def on_message(client, userdata, message):
#     print(f"Received message: {message.payload.decode()} on topic {message.topic}")

# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# client.username_pw_set(username, password)
# client.on_connect = on_connect
# client.on_message = on_message

# # Connect to broker
# print("Connecting to broker...")
# client.connect(broker_address, port)
# client.loop_start()  # Start the network loop

# # Wait until connected
# while not is_connected:
#     print("Waiting for connection...")
#     time.sleep(1)

# # Keep the script running
# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     client.loop_stop()
#     client.disconnect()

from model.actuator import Actuator

actuator = Actuator("T_Temperature_TRT")
actuator.connect()