DEVICE_TYPES = {
    "mc20": {
        "name": "MC20",
        "sensors": {
            "createdAt",
            "packetId",
            "voltageFence",
            "voltageBattery",
            "voltageFenceLowTreshold",
            "signal",
        },
        "faults": True,
        "units": {
            "voltageBattery": "%",
        },
    },
    "edc": {
        "name": "EDC",
        "sensors": {
            "createdAt",
            "packetId",
            "voltageFence",
            "voltageBattery",
            "energyFence",
            "impedance",
            "voltageFenceLowTreshold",
            "signal",
            "powerOutput",
            "state",
        },
        "faults": True,
        "units": {
            "voltageBattery": "V",
        },
    },
    "pdc50": {
        "name": "PDC50",
        "sensors": {
            "createdAt",
            "packetId",
            "voltageFence",
            "voltageBattery",
            "voltageFenceLowTreshold",
            "signal",
            "powerOutput",
            "state",
        },
        "faults": True,
        "units": {
            "voltageBattery": "V",
        },
    },
}


def get_device_type_options():
    """Return dict of device type keys and names for display."""
    return {key: info["name"] for key, info in DEVICE_TYPES.items()}


def get_allowed_sensors(device_type: str):
    """Return set of sensor keys allowed for device type."""
    if device_type not in DEVICE_TYPES:
        return DEVICE_TYPES["edc"]["sensors"]
    return DEVICE_TYPES[device_type]["sensors"]


def get_unit_overrides(device_type: str):
    """Return dict of unit overrides for device type."""
    if device_type not in DEVICE_TYPES:
        return {}
    return DEVICE_TYPES[device_type].get("units", {})


def has_faults(device_type: str):
    """Return whether device type has fault sensors."""
    if device_type not in DEVICE_TYPES:
        return True
    return DEVICE_TYPES[device_type]["faults"]
