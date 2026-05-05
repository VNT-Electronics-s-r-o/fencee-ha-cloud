

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import DATA_COORDINATOR, DOMAIN
from .types import get_allowed_sensors

SENSORS = {
    "createdAt": ("Poslední aktualizace", None),
    "voltageFence": ("Napeti na ohrade", "V"),
    "voltageBattery": ("Baterie", "%"),
    "energyFence": ("Energie", "%"),
    "impedance": ("Impedance", "Ohm"),
    "voltageFenceLowTreshold":("Threshold", "V"),
    "signal": ("Signal", "%"),
    "powerOutput": ("Nastaveny maximalni vykon", "%"),
}

DEVICE_CLASSES = {
    "createdAt": SensorDeviceClass.TIMESTAMP,
    "voltageFence": SensorDeviceClass.VOLTAGE,
    "voltageBattery": SensorDeviceClass.BATTERY,
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
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data["name"]
    mac = config_entry.data["mac"].lower()
    device_type = config_entry.data.get("device_type", "edc")
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    allowed_sensors = get_allowed_sensors(device_type)
    entities = []

    for key in SENSORS:
        if key not in allowed_sensors:
            continue
        sensor_name, unit = SENSORS.get(key, (key, None))
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
                return value
            return None
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
        return DEVICE_CLASSES.get(self._key)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": self._device_name,
            "manufacturer": "VNT electronics s.r.o.",
            "model": "Fencee monitor",
        }