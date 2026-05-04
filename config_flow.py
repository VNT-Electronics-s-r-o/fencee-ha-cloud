import voluptuous as vol

from homeassistant import config_entries

DOMAIN = "fencee"


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
              vol.Required("brand", default="fencee"): vol.In(["fencee", "voss"]),
              vol.Required("token"): str,
              vol.Required("mac"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )