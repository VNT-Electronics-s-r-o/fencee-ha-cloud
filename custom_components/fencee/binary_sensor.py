from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import DATA_COORDINATOR, DOMAIN
from .types import has_faults


def _fault_name(key: str) -> str:
    label = key.replace("alarm_", "").replace("_", " ")
    return "Porucha: " + label.capitalize()


async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data["name"]
    mac = config_entry.data["mac"].lower()
    device_type = config_entry.data.get("device_type", "edc")
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []

    if not has_faults(device_type):
        async_add_entities(entities)
        return

    entities.append(
        FenceeBinarySensor(coordinator, name, mac, "hasFaults", "Ma poruchu"),
    )

    faults = coordinator.data.get("data", {}).get("faults", {})
    if isinstance(faults, dict):
        for fault_key, fault_value in faults.items():
            if fault_value:
                entities.append(
                    FenceeBinarySensor(
                        coordinator,
                        name,
                        mac,
                        fault_key,
                        _fault_name(fault_key),
                        parent_key="faults",
                    )
                )

    async_add_entities(entities)


class FenceeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator,
        device_name,
        mac,
        key,
        sensor_name,
        parent_key=None,
    ):
        super().__init__(coordinator)
        self._device_name = device_name
        self._mac = mac
        self._key = key
        self._parent_key = parent_key
        self._sensor_name = sensor_name

    @property
    def name(self):
        return f"{self._device_name} {self._sensor_name}"

    @property
    def unique_id(self):
        if self._parent_key:
            return f"fencee_{self._mac}_{self._parent_key}_{self._key}"
        return f"fencee_{self._mac}_{self._key}"

    @property
    def is_on(self):
        data = self.coordinator.data.get("data", {})
        if self._parent_key:
            nested = data.get(self._parent_key, {})
            if isinstance(nested, dict):
                return bool(nested.get(self._key))
            return False
        return bool(data.get(self._key))

    @property
    def device_class(self):
        return BinarySensorDeviceClass.PROBLEM

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": self._device_name,
            "manufacturer": "VNT electronics s.r.o.",
            "model": "Fencee monitor",
        }
