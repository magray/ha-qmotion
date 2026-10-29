"""Config flow for QMotion."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_PORT, DOMAIN
from .protocol import QMotionClient


class QMotionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a QSync hub by IP address."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input["port"]
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            try:
                await QMotionClient(host, port).async_get_blinds()
            except (HomeAssistantError, OSError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=f"QMotion ({host})", data={CONF_HOST: host, "port": port})

        schema = vol.Schema({vol.Required(CONF_HOST): str, vol.Optional("port", default=DEFAULT_PORT): vol.Coerce(int)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
