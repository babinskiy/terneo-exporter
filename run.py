from asyncio.log import logger
import logging
import socket
import sys
import threading
import requests
import json
import time
import os
import argparse
from logging import error, warning, info, debug, basicConfig as log_config
from signal import signal, SIGTERM, SIGINT
from prometheus_client import start_http_server, Summary, Counter, Gauge, Info

from metrics import metrics_settings

devices = {}
metrics = {}

read_devices_thread = None
gc_devices_thread = None


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
            error('Unknown metric name: %s from %s', metric, device)
            continue
        metric_type = metric_settings.get('type', 'none')

        if metric_type == 'gauge':
            set_metric_gauge(metric, data[metric], labels)
        # TODO: Add other types of metric

def gc_devices():
    threading.Timer(7.0, gc_devices).start()
    for device in devices.keys():
        if time.time() - devices[device]['lastSeen'] > 300:
            warning('Devise %s is outdated. Removing' % device)
            del devices[device]

def read_device(device):
    debug("Start reading data from: %s" % device)
    debug('Sending query to %s', devices[device]['address'])
    req = requests.post("http://%s/api.cgi" % devices[device]['address'], data='{"cmd": 4}', timeout=5)
    debug('Request result code: %s', req.status_code)
    # debug('Returned data: %s', req.text)
    if req.status_code == 200:
        return req.json()
    else:
        error('Reqesut for data from %s failed with code %s and message "%s"', devices[device]['address'], req.status_code, req.text)
        return None

def read_devices():
    threading.Timer(15.0, read_devices).start()
    for device in devices.keys():
        metric_data = read_device(device)
        update_metrics(device, metric_data)

def signal_handler(signal, frame):
    read_devices_thread.cancel()
    gc_devices_thread.cancel()
    warning('Application was interrapted by signal. Exiting...')
    sys.exit()

def __parse_args():
    pass

def __configure_logger():
    log_config(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s]: (%(threadName)s) %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def __main():
    global metrics
    global devices
    global read_devices_thread
    global gc_devices_thread
    __configure_logger()
    info('Staring Up...')

    metrics['dev_num'] = Gauge("number_of_devices", "Number of detected devices")
    metrics['dev_num'].set_function(lambda: len(devices.keys()))

    read_devices_thread = threading.Timer(15.0, read_devices)
    read_devices_thread.start()

    gc_devices_thread = threading.Timer(7.0, gc_devices)
    gc_devices_thread.start()

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 23500))
    debug('Startied UDP Broadcasts listeing')

    start_http_server(
        addr = os.getenv('LISTEN_ADDR', '0.0.0.0'),
        port = int(os.getenv('LISTEN_PORT', 8001)))
    debug('Start listeting for metric collectors connections')

    while True:
        new_device = True
        data, addr = client.recvfrom(1024)
        device_data = json.loads(data)
        device_sn = device_data['sn']
        debug("Received announcement from %s: %s", addr[0], device_data)

        if device_sn in devices.keys():
            new_device = False

        devices[device_sn] = device_data | {'address': addr[0], 'lastSeen': time.time()}

        if new_device:
            metric_data = read_device(device_sn)
            update_metrics(device_sn, metric_data)
            info('New device was added to pool: sn=%s address=%s', device_sn, addr[0])

if __name__ == "__main__":
    __main()
