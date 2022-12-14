import paho.mqtt.client as mqtt
from uuid import uuid4
import certifi

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hat-draw-1")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


clientId = "hat-" + str(uuid4())

client = mqtt.Client(clientId, clean_session=True, transport="websockets")
client.ws_set_options(path="/ws")
client.tls_set(certifi.where())
client.on_connect = on_connect
client.on_message = on_message

client.connect("mq02.cy2.me", 443, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
