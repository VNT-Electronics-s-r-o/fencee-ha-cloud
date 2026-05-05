DEVICE_TYPES = {
    "mc20": {
        "name": "MC20",
        "sensors": {
            "voltageFence",
            "voltageBattery",
            "voltageFenceLowTreshold",
            "signal",
            "createdAt",
        },
        "faults": True,
    },
    "edc": {
        "name": "EDC",
        "sensors": {
            "createdAt",
            "voltageFence",
            "voltageBattery",
            "energyFence",
            "impedance",
            "voltageFenceLowTreshold",
            "signal",
            "powerOutput",
        },
        "faults": True,
    },
}


def get_device_type_options():
    return {key: info["name"] for key, info in DEVICE_TYPES.items()}


def get_allowed_sensors(device_type: str):
    """Return set of sensor keys allowed for device type."""
    if device_type not in DEVICE_TYPES:
        return set(DEVICE_TYPES.values())[0]["sensors"]
    return DEVICE_TYPES[device_type]["sensors"]


def has_faults(device_type: str):
    """Return whether device type has fault sensors."""
    if device_type not in DEVICE_TYPES:
        return True
    return DEVICE_TYPES[device_type]["faults"]
