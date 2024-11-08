import paho.mqtt.client as mqtt

# MQTT broker settings
broker_address = "172.17.0.1"
port = 1883
topic = "test/topic"
# Credentials
username = "user1"
password = "pwd1"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(username, password)
client.connect(broker_address, port)

# Publish a message
message = "Hello, MQTT!"
result = client.publish(topic, message)
status = result.rc

if status == 0:
    print(f"Message `{message}` sent to topic `{topic}`")
else:
    print(f"Failed to send message to topic `{topic}`")

client.disconnect()