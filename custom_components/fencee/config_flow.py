import voluptuous as vol

from homeassistant import config_entries
from .types import get_device_type_options

DOMAIN = "fencee"
DEFAULT_UPDATE_INTERVAL = 3600
MIN_UPDATE_INTERVAL = 60
MAX_UPDATE_INTERVAL = 86400


class FenceeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input["mac"].lower())
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("device_type", default="edc"): vol.In(list(get_device_type_options().keys())),
                vol.Required("brand", default="fencee"): vol.In(["fencee", "voss"]),
                vol.Required("token"): str,
                vol.Required("mac"): str,
                vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )