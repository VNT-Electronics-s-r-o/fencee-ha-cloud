

from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import DATA_COORDINATOR, DOMAIN
from .types import get_allowed_sensors, get_unit_overrides

SENSORS = {
    "createdAt": ("Poslední aktualizace", None),
    "packetId": ("Packet ID", None),
    "voltageFence": ("Napeti na ohrade", "V"),
    "voltageBattery": ("Baterie", "%"),
    "energyFence": ("Energie", "%"),
    "impedance": ("Impedance", "Ohm"),
    "voltageFenceLowTreshold":("Threshold", "V"),
    "signal": ("Signal", "%"),
    "powerOutput": ("Nastaveny maximalni vykon", "%"),
    "state": ("Stav", None),
}

STATE_MAP = {
    0: "OFF",
    1: "Standby",
    2: "ON",
}

DEVICE_CLASSES = {
    "createdAt": SensorDeviceClass.TIMESTAMP,
    "voltageFence": SensorDeviceClass.VOLTAGE,
    "voltageFenceLowTreshold": SensorDeviceClass.VOLTAGE,
}

MEASUREMENT_KEYS = {
    "voltageFence",
    "voltageBattery",
    "energyFence",
    "impedance",
    "voltageFenceLowTreshold",
    "signal",
    "powerOutput",
    "packetId",
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data["name"]
    mac = config_entry.data["mac"].lower()
    device_type = config_entry.data.get("device_type", "edc")
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    allowed_sensors = get_allowed_sensors(device_type)
    unit_overrides = get_unit_overrides(device_type)
    entities = []

    for key in SENSORS:
        if key not in allowed_sensors:
            continue
        sensor_name, unit = SENSORS.get(key, (key, None))
        unit = unit_overrides.get(key, unit)
        entities.append(FenceeSensor(coordinator, name, mac, key, sensor_name, unit))

    async_add_entities(entities)


class FenceeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_name, mac, key, sensor_name, unit):
        super().__init__(coordinator)
        self._device_name = device_name
        self._mac = mac
        self._key = key
        self._sensor_name = sensor_name
        self._unit = unit

    @property
    def name(self):
        return f"{self._device_name} {self._sensor_name}"

    @property
    def unique_id(self):
        return f"fencee_{self._mac}_{self._key}"

    @property
    def native_value(self):
        value = self.coordinator.data.get("data", {}).get(self._key)
        if self._key == "createdAt":
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value, tz=timezone.utc)
            return None
        if self._key == "state":
            return STATE_MAP.get(value, value)
        if value is None and self._unit is not None:
            return 0
        return value

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def state_class(self):
        if self._key in MEASUREMENT_KEYS:
            return SensorStateClass.MEASUREMENT
        return None

    @property
    def device_class(self):
        dc = DEVICE_CLASSES.get(self._key)
        if dc:
            return dc
        if self._key == "voltageBattery":
            if self._unit == "V":
                return SensorDeviceClass.VOLTAGE
            return SensorDeviceClass.BATTERY
        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": self._device_name,
            "manufacturer": "VNT electronics s.r.o.",
            "model": "Fencee monitor",
        }