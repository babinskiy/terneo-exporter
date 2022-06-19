# terneo-exporter
Simple tool for exporting operational status of [Terneo climate control devices](https://www.terneo.ua/) in way suitable for collectin by [Prometheus](https://prometheus.io)

License: [GPL3.0](LICENSE)

## Running
In current version it creates list of polled devices only by catched broadcast anounces, so it must be run in the same network segment where Terneo devices are connected.

```
docker run --name terneo-exporter \
--daemon \
--network=host \
-e DEVICES_POLL_INTERVAL=30 \
-e DEVICES_GC_INTERVAL=120 \
nbabinskiy/terneo-exporter:latest
```

## Configuration
There are available set of environment variables:
```text
DEVICES_GC_INTERVAL=300  # Number of seconds between running devices garbage collections (process of removing of devices which arent seen for long time (300 seconds for now))
DEVICES_GC_AGE=300  # Number of seconds passed from last announce needed for removing device from polling list
DEVICES_POLL_INTERVAL=30  # Number of seconds between sending data collection requests to devices 
LOG_LEVEL=INFO # Log level, could be one of DEBUG, INFO, WARNING, ERROR 
LISTEN_ADDR=0.0.0.0  # Adress which will be listened for metric collection tool connections
LISTEN_PORT=8000  # Port which will be listened for metric collection tool connections
ANNOUNCE_LISTEN_ADDR=0.0.0.0 # Adress which will be listened for device's annonce packages
ANNOUNCE_LISTEN_PORT=23500 # Port which will be listened for device's annonce packages (All of them uses port 23500 as I know, so there is no reasun to use this variable)
```