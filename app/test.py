# import paho.mqtt.client as mqtt

# # MQTT broker settings
# broker_address = "localhost"
# port = 1883
# topic = "test/topic"
# # Credentials
# username = "T_PH_TRTM"
# password = "T_PH_TRTM_psswd"
# # username= "user1"
# # password = "pwd1"

# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# client.username_pw_set(username, password)
# client.connect(broker_address, port)

# # Publish a message
# message = "Hello, MQTT!"
# result = client.publish(topic, message)
# status = result.rc

# if status == 0:
#     print(f"Message `{message}` sent to topic `{topic}`")
# else:
#     print(f"Failed to send message to topic `{topic}`")

# client.disconnect()

from model.sensor import Sensor

sensor = Sensor("T_Temperature_TRT")
sensor.mqtt_publish()