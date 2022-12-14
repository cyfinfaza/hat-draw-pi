import paho.mqtt.client as mqtt
from uuid import uuid4
import certifi
from sense_hat import SenseHat
from PIL import ImageColor
import json
import time

hat = SenseHat()
hat.clear()

TOPIC = "hat-draw-1"

connected = False
hadFirstConnection = False


def convertHexArrayToRGB(hexArray):
    rgbArray = []
    for hex in hexArray:
        try:
            if not len(hex) == 7:
                raise Exception("Hex string is not 7 characters long")
            rgbArray.append(ImageColor.getrgb(hex))
        except Exception as e:
            print(f'FAILED TO SET COLOR "{hex}" at position {len(rgbArray)}: {e}')
            rgbArray.append((0, 0, 0))
    return rgbArray


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global connected
    global hadFirstConnection
    connected = True
    hadFirstConnection = True
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC)
    print("Subscribed to topic: " + TOPIC)


def on_disconnect(client, userdata, rc):
    global connected
    connected = False
    print("Disconnected with result code " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(
        f"INCOMING {msg.topic} ({len(msg.payload)} characters), attempting display update"
    )
    try:
        data = json.loads(msg.payload)
        hat.set_pixels(convertHexArrayToRGB(data["grid"]))
        print("DISPLAY UPDATE SUCCESS")
    except Exception as e:
        print("FAILED: ", e)
        return


clientId = "hat-" + str(uuid4())
print("clientId: " + clientId)
client = mqtt.Client(clientId, clean_session=True, transport="websockets")
client.ws_set_options(path="/mqtt")
client.tls_set(certifi.where())
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.loop_start()
while True:
    if not connected:
        hat.set_pixel(7, 7, 255, 0, 0)
        if not hadFirstConnection:
            try:
                client.connect("mqtt.4hcomputers.club", 443, 60)
            except:
                print("Failed to connect, trying again in 1 second")
                time.sleep(1)
        time.sleep(0.1)
        hat.set_pixel(7, 7, 0, 0, 0)
        time.sleep(0.1)
    else:
        time.sleep(1)
