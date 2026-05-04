
from datetime import timedelta

import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "fencee"

SENSORS = {
    "voltageFence": ("Napeti na ohrade", "V"),
    "voltageBattery": ("Baterie", "%"),
    "energyFence": ("Energie", "%"),
    "impedance": ("Impedance", "Ohm"),
    "voltageFenceLowTreshold":("Threshold", "V"),
    "signal": ("Signal", "%"),
    "powerOutput": ("Nastaveny maximalni vykon", "%"),
}

HOSTS = {
    "fencee": "16.60.164.227",
    "voss": "16.60.164.227",
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    session = async_get_clientsession(hass)

    name = config_entry.data["name"]
    mac = config_entry.data["mac"].lower()
    token = config_entry.data["token"]
    brand = config_entry.data["brand"]

    host = HOSTS.get(brand)

    url = f"http://{host}:5000/api/v1/device/last-value?token={token}&mac={mac}"

    async def async_update_data():
        async with session.get(url) as resp:
            return await resp.json()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"fencee_{mac}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=60),
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []
    data = coordinator.data.get("data", {})

    for key in data.keys():
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
        return self.coordinator.data.get("data", {}).get(self._key)

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def device_class(self):
        if self._key == "voltageFence":
            return SensorDeviceClass.VOLTAGE

        if self._key == "voltageBattery":
            return SensorDeviceClass.BATTERY

        if self._key == "voltageFenceLowTreshold":
            return SensorDeviceClass.VOLTAGE

        if self._key == "energyFence":           
            return SensorDeviceClass.PERCENTAGE

        return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": self._device_name,
            "manufacturer": "VNT electronics s.r.o.",
            "model": "Fencee monitor",
        }