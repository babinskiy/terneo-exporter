import socket
import sys
import threading
import requests
import json
import os
from time import time as curr_time
from logging import error, warning, info, debug, basicConfig as log_config
from signal import signal, SIGTERM, SIGINT
from prometheus_client import start_http_server, Counter, Gauge, Info

from metrics import metrics_settings

READ_DEVICE_INTERVAL = float(os.getenv('DEVICES_POLL_INTERVAL', '30'))
GC_DEVICE_INTERVAL = float(os.getenv('DEVICES_GC_INTERVAL', '300'))
GC_MAX_AGE = float(os.getenv('DEVICES_GC_AGE', 300))

read_devices_thread = None
gc_devices_thread = None
thread_exit_event = None

devices = {}
metrics = {}


def set_metric_gauge(metric, data, labels=None):
    global devices, metrics
    if metric not in metrics:
        metrics[metric] = Gauge(metrics_settings[metric]['name'],
                                metrics_settings[metric]['description'],
                                labels.keys())
    metrics[metric].labels(**labels).set(int(data) * metrics_settings[metric].get('correction', 1))


def update_metrics(device, data):
    global devices, metrics
    labels = {'sn':      device,
              'address': devices[device]['address'],
              'hw':      devices[device]['hw']}
    for metric in data:
        metric_settings = metrics_settings.get(metric, {})
        if len(metric_settings) == 0:
            warning('Unknown metric name: %s from %s', metric, device)
            continue
        metric_type = metric_settings.get('type', 'none')
        labels['metric_key'] = metric

        if metric_type == 'gauge':
            set_metric_gauge(metric, data[metric], labels)
        # TODO: Add other types of metric


def gc_devices():
    global devices
    global GC_MAX_AGE
    info('Devices GC process is started')
    for device in devices.keys():
        if curr_time() - devices[device]['lastSeen'] > GC_MAX_AGE:
            warning('Devise %s is outdated. Removing' % device)
            del devices[device]


def gc_devices_threaded(interval=60):
    global devices
    global thread_exit_event
    cycle_start_time = curr_time()
    while not thread_exit_event.wait(0.1):
        if curr_time() - cycle_start_time < interval:
            continue
        else:
            cycle_start_time = curr_time()
        gc_devices()


def read_device(device):
    global devices
    device_address = devices[device]['address']
    debug("Start reading data from: %s" % device)
    debug('Sending query to %s', device_address)
    try:
        req = requests.post("http://%s/api.cgi" % device_address, data='{"cmd": 4}', timeout=5)
    except requests.RequestException as err:
        error('Device request failed: %s', str(err))
        return {'sn': device}
    debug('Request result code: %s, data: %s', req.status_code, req.text)
    # debug('Returned data: %s', req.text)
    if req.status_code == 200:
        try:
            return req.json()
        except requests.exceptions.JSONDecodeError:
            error('Device reply decode failed. Device: %s, address: %s, reply: %s', device, device_address, req.text)
    else:
        error('Device reqesut failed. Device: %s, Address: %s, code %s, message "%s"', device, device_address, req.status_code, req.text)
    return {'sn': device}


def read_devices():
    global devices, metrics
    for device in devices.keys():
        metric_data = None
        with metrics['dev_poll_time'].labels(sn=device).time():
            metric_data = read_device(device)
        update_metrics(device, metric_data)


def read_devices_threaded(interval=15):
    global thread_exit_event
    cycle_start_time = curr_time()
    while not thread_exit_event.wait(0.1):
        if curr_time() - cycle_start_time < interval:
            continue
        else:
            cycle_start_time = curr_time()
        info('Start device polling cycle')
        read_devices()


def signal_handler(signal, frame):
    warning('Application was interrupted by signal. Exiting...')
    thread_exit_event.set()
    sys.exit()


def thread_exception_hook(args):
    global read_devices_thread, READ_DEVICE_INTERVAL
    global gc_devices_thread, GC_DEVICE_INTERVAL
    error('Thread "%s" has failed. Recreating...', args.thread.name)
    if args.thread.name == 'DevPollThread':
        run_devpoll_thread()
    elif args.thread.name == "DevicesGCThread":
        run_devgc_thread()
    else:
        error('Thread "%s" is uncnown! Panic!')
        sys.exit(1)


def run_devpoll_thread():
    global read_devices_thread, READ_DEVICE_INTERVAL
    debug('Starting device polling thread')
    read_devices_thread = threading.Thread(target=read_devices_threaded, name="DevPollThread", kwargs={"interval": READ_DEVICE_INTERVAL})
    read_devices_thread.start()


def run_devgc_thread():
    global gc_devices_thread, GC_DEVICE_INTERVAL
    debug('Starting GC thread')
    gc_devices_thread = threading.Thread(target=gc_devices_threaded, name="DevicesGCThread", kwargs={"interval": GC_DEVICE_INTERVAL})
    gc_devices_thread.start()


def kill_app():
    pid = os.getpid()
    os.kill(pid, SIGTERM)


def __configure_logger():
    log_config(
        level=os.getenv('LOG_LEVEL', 'INFO'),
        format='[%(asctime)s] [%(levelname)s]: (%(threadName)s) %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def __main():
    global devices, metrics
    global read_devices_thread, READ_DEVICE_INTERVAL
    global gc_devices_thread, GC_DEVICE_INTERVAL
    global thread_exit_event
    global dev_poll_time

    __configure_logger()
    info('Staring Up...')

    debug('Starting background threads')
    thread_exit_event = threading.Event()
    threading.excepthook = thread_exception_hook
    run_devpoll_thread()
    run_devgc_thread()

    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    debug('Starting UDP Broadcasts listeing')
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind((os.getenv('ANNOUNCE_LISTEN_ADDR', '0.0.0.0'), int(os.getenv('ANNOUNCE_LISTEN_PORT', 23500))))

    debug('Start listeting for metric collectors connections')
    start_http_server(
        addr=os.getenv('LISTEN_ADDR', '0.0.0.0'),
        port=int(os.getenv('LISTEN_PORT', 8000)))

    metrics['dev_num'] = Gauge("terneo_number_of_devices", "Number of detected devices")
    metrics['dev_num'].set_function(lambda: len(devices.keys()))
    metrics['dev_poll_time'] = Gauge('terneo_device_polling_time', 'Device polling time', ['sn'])


    while True:
        new_device = True
        data, addr = client.recvfrom(1024)
        device_data = json.loads(data)
        device_sn = device_data['sn']
        debug("Received announcement from %s: %s", addr[0], device_data)

        if device_sn in devices.keys():
            new_device = False

        devices[device_sn] = device_data | {'address': addr[0], 'lastSeen': curr_time()}

        if new_device:
            metric_data = read_device(device_sn)
            update_metrics(device_sn, metric_data)
            info('New device is found: sn=%s address=%s', device_sn, addr[0])


if __name__ == "__main__":
    __main()
