from datetime import timedelta

import logging
from aiohttp import ClientError

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

MAIN = "fencee"
DOMAIN = "fencee"
DATA_COORDINATOR = "coordinator"
DEFAULT_UPDATE_INTERVAL = 3600
MIN_UPDATE_INTERVAL = 60
MAX_UPDATE_INTERVAL = 86400

HOSTS = {
    "fencee": "ha-dev.fenceelink.com",
    "voss": "ha-dev.fenceelink.com",
}

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup_entry(hass, entry):
    session = async_get_clientsession(hass)

    mac = entry.data["mac"].lower()
    token = entry.data["token"]
    brand = entry.data["brand"]
    update_interval = min(
        max(
            int(entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)),
            MIN_UPDATE_INTERVAL,
        ),
        MAX_UPDATE_INTERVAL,
    )

    host = HOSTS.get(brand)
    url = f"https://{host}/api/v1/device/last-value?token={token}&mac={mac}"

    async def async_update_data():
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()
        except (ClientError, ValueError) as err:
            raise UpdateFailed(f"Error fetching data for {mac}: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"fencee_{mac}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=update_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok