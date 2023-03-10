# python3.6
#### Tasmota MQTT extractor
appver = "1.3.3"
appname = "Tasmota MQTT extractor"
appshortname = "TMQTTEx"

import random
import json
from paho.mqtt import client as mqtt_client
from prometheus_client import start_http_server, Gauge
from time import sleep as sleep
from datetime import datetime
from os import environ as environ


print(appname + " ver. "+appver)
# print('test_env_var:'+ str(test_env_var))
tab='  |'

env ='dev' #prod

if env == 'prod':
    server_port =int(environ.get('SERVER_PORT'))
    get_delay = int(environ.get('GET_DELAY'))
    broker = environ.get('BROKER_IP')
    port = int(environ.get('BROKER_PORT'))
    topic = environ.get('TOPIC')
    username = environ.get('USERNAME')
    password = environ.get('PASSWORD')
else:
    server_port=int('80')
    get_delay = 10
    broker = '192.168.2.4'
    port = 1883
    topic = "tele/7C9EBDFA21A0/SENSOR"
    username = 'mqtt'
    password = 'mqtt001'


# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

# metric_name=topic.replace('/','_')
MQTT_VALUE = Gauge(topic.replace('/','_'), 'topic', ['topic','key','value','type'])
APP_INFO = Gauge('app_info', 'Return app info',['appname','appshortname','version'])
APP_INFO.labels(appname,appshortname,appver).set(1)

def pars_json(text):
    print('------------------------')
    d = json.loads(text)
    for key, values in d.items():
        print(key,values)
        if type(values) != dict:
            if key == 'Time':

                datetime_object = datetime.strptime(values, '%Y-%m-%dT%H:%M:%S')
                set_metrica(key, int(datetime_object.strftime('%y%m%d%H%M%S')))
            else: set_metrica(key,values)
        if type(values) == dict:
            for key2, values2 in values.items():
                set_metrica(key+'_'+key2,values2)

def set_metrica(k,v):
    vt = type(v)
    if vt in (int,float):
        l3=1
        mv= v
    else:
        l3 =v
        mv = 1
    MQTT_VALUE.labels(topic, k, l3, vt).set(mv)
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        pars_json(msg.payload.decode())
        pars_json(msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    try:
        start_http_server(server_port)
    except Exception as e: print(e)
    while True:
        run()
        sleep(get_delay)
