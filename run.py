import socket
import threading
import requests
import json
import time
import os
from prometheus_client import start_http_server, Summary, Counter, Gauge, Info

from metrics import metrics_settings

def set_metric_gauge(metric, data, labels=None):
    if metric not in metrics:
        metrics[metric] = Gauge(metrics_settings[metric]['name'],
                                metrics_settings[metric]['description'],
                                labels.keys())
    metrics[metric].labels(**labels).set(int(data) * metrics_settings[metric].get('correction', 1))


def update_metrics(device, data):
    labels = { 'sn':      device,
               'address': devices[device]['address'],
               'hw':      devices[device]['hw']}
    for metric in data:
        metric_settings = metrics_settings.get(metric, {})
        if len(metric_settings) == 0:
            print('Just got unknown metric name: %s' % metric)
            continue
        metric_type = metric_settings.get('type', 'none')

        if metric_type == 'gauge':
            set_metric_gauge(metric, data[metric], labels)

def gc_devices():
    for device in devices.keys():
        if time.time() - devices[device]['lastSeen'] > 300:
            print('Devise %s is outdated. Removing' % device)
            del devices[device]

def read_device(device):
    print("reading data from: %s" % device)
    req = requests.post("http://%s/api.cgi" % devices[device]['address'], data='{"cmd": 4}', timeout=5)
    if req.status_code == 200:
        return req.json()
    else:
        return None

def read_devices():
    for device in devices.keys():
        metric_data = read_device(device)
        update_metrics(device, metric_data)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.bind(("", 23500))

start_http_server(
    addr = os.getenv('LISTEN_ADDR', '0.0.0.0'),
    port = os.getenv('LISTEN_PORT', 8000)
    )

devices = {}
metrics = {}
metrics['dev_num'] = Gauge("number_of_devices", "Number of detected devices")
metrics['dev_num'].set_function(lambda: len(devices.keys()))

threading.Timer(15.0, read_devices).start()
threading.Timer(7.0, gc_devices).start()

while True:
    new_device = True
    data, addr = client.recvfrom(1024)
    print("received message: %s from %s" % (data, addr[0]))
    device_data = json.loads(data)
    device_sn = device_data['sn']

    if device_sn in devices.keys():
        new_device = False

    devices[device_sn] = device_data | {'address': addr[0], 'lastSeen': time.time()}

    if new_device:
        metric_data = read_device(device_sn)
        update_metrics(device_sn, metric_data)
