metrics_settings = {
    "sn": { "name": "terneo_serial_number", "description": "Serial number"},
    # "hw": ["terneo_hardware_type", "Hardware type", 0],
    # "cloud": [ "terneo_coud_connection", "Cloud connection", 0],
    # "connection": [ "terneo_connection_status", "status of the connection to the cloud", 0],
    # "wifi": [ "terneo_wifi_signal_strength", "Wi-Fi signal strength in dBm", 0],
    # "display": ["terneo_current_display", "device display reading", ],
    # Themperatures
    "t.0": {"type": "gauge", "name": "terneo_internal_themperature", "description": "Internal thermal sensor", "correction": 1/16},
    "t.1": {"type": "gauge", "name": "terneo_floor_themperature", "description": "Floor thermal sensor", "correction": 1/16},
    "t.2": {"type": "gauge", "name": "terneo_air_temperature", "description": "Air thermal sensor", "correction": 1/16},
    "t.3": {"type": "gauge", "name": "terneo_precipitation_sensor", "description": "precipitation sensor", "correction": 1/16},
    "t.4": {"type": "gauge", "name": "terneo_external_themperature", "description": "External thermal sensor", "correction": 1/16},
    "t.5": {"type": "gauge", "name": "terneo_current_themperature_setting", "description": "Current themperature setpoint", "correction": 1/16},
    "t.6": {"type": "gauge", "name": "terneo_themperature_correction", "description": "Themperature correction value", "correction": 1/16},
    # Voltages
    # "u.0": "Maximal voltage",
    # "u.1": "Minimal voltage",
    # "u.2": "3.3V line voltage",
    # "u.3": "Battery voltage",
    # "u.4": "High level",
    # "u.5": "Low level",
    # "u.6": "Average voltage",
    # # Current
    # "i.0": "maximum current during telemetry period",
    # "i.1": "average current during telemetry period",
    # "i.2": "minimum current during telemetry period",
    # "i.3": "upper current limit",
    # "i.4": "average current limit",
    # "i.5": "lower current limit",
    # # Power
    # "w.0": "upper power limit, watt",
    # "w.1": "maximum total load power during telemetry period, VA",
    # "w.2": "average total load power during telemetry period, VA",
    # "w.3": "minimum total load power during telemetry period, VA",
    # "w.4": "maximum cosine fi during telemetry period, 1/100 degree",
    # "w.5": "average cosine fi during telemetry period, 1/100 degree",
    # "w.6": "the minimum cosine fi during telemetry period, 1/100 degree",
    # # Resistance
    # "r.0": "ground moisture sensor, 100 Ohm",
    # # active and reactive parameters
    # "p.0": "the maximum active load power during telemetry period, watts",
    # "p.1": "average active load power during telemetry period, watts",
    # "p.2": "the minimum active load power during telemetry period, watts",
    # "p.3": "maximum reactive load power during period of telemetry, VAR",
    # "p.4": "average reactive load power during telemetry period, VAR",
    # "p.5": "minimum reactive load power during telemetry period, VAR",
    # Modes
    "m.0": {"type": "gauge", "name": "terneo_control_type_sensor", "description": "control type: floor = 0, air = 1, extended = 2"},
    "m.1": {"type": "gauge", "name": "terneo_control_type_mode", "description": "control type: schedule = 0, manual = 3, away = 4, temporary = 5"},
    "m.2": {"type": "gauge", "name": "terneo_number_of_schedule_period", "description": "the number of the current period of the schedule (the first period of Monday = 0, Tuesday = maxSchedulePeriod …)["},
    "m.3": {"type": "gauge", "name": "terneo_blocking_type", "description": "blocking type: no blocking = 0, blocking changes from the cloud = 1, blocking changes from the local network = 2, both = 3"},
    "m.4": {"type": "gauge", "name": "terneo_controlled_power_type", "description": "controlled power type: active power = 0, reactive power = 1, apparent power = 2"},
    # Other
    "o.0": {"type": "gauge", "name": "terneo_wifi_signal_strength", "description":  "Wi-Fi signal strength in dBm"},
    "o.1": {"type": "gauge", "name": "terneo_reboot_cause", "description": "the cause of the last reboot, mask: power off = 0x04, soft reset = 0x08, watchdog timer = 0x10, low voltage = 0x40"},
    # duplication of some device parameters
    # "par.0": "",
    # "te": "extra temperatures",
    #  bit parameters
    "f.0": {"type": "gauge", "name": "terneo_load_status", "description": "load status"},
    "f.1": {"type": "gauge", "name": "terneo_waiting_for_load", "description": "waiting for load is being changed"},
    "f.2": {"type": "gauge", "name": "terneo_floor_restriction_action", "description": "floor restriction action"},
    "f.3": {"type": "gauge", "name": "terneo_no_floor_sensor", "description": "no floor sensor"},
    "f.4": {"type": "gauge", "name": "terneo_short_circ_floor_sensor", "description": "short circuit floor sensor"},
    "f.5": {"type": "gauge", "name": "terneo_no_air_sensor", "description": "no air sensor"},
    "f.6": {"type": "gauge", "name": "terneo_short_circ_air_sensor", "description": "short circuit air sensor"},
    "f.7": {"type": "gauge", "name": "terneo_func_preheat_is_active", "description": "preheat algorithm is active"},
    "f.8": {"type": "gauge", "name": "terneo_func_open_windows_is_active", "description": "an open window function is active"},
    "f.9": {"type": "gauge", "name": "terneo_internal_overheating", "description": "internal overheating"},
    "f.10": {"type": "gauge", "name": "terneo_battery_is_low", "description": "the battery is low"},
    "f.11": {"type": "gauge", "name": "terneo_clock_issue", "description": "problems with the clock"},
    "f.12": {"type": "gauge", "name": "terneo_no_overheat_control", "description": "no overheat control"},
    "f.13": {"type": "gauge", "name": "terneo_func_proportional_is_active", "description": "proportional mode is active"},
    "f.14": {"type": "gauge", "name": "terneo_digital_foor_sensor", "description": "digital floor sensor is used"},
    "f.15": {"type": "gauge", "name": "terneo_restart_by_watchdog", "description": "restart by watchdog timer"},
    "f.16": {"type": "gauge", "name": "terneo_poweredoff", "description": "power off state"},
    "f.17": {"type": "gauge", "name": "terneo_long_time_load_error", "description": "long time load on error"}
}
