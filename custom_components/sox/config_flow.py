"""Configuration flow for SoX component."""

from typing import Final
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from custom_components.sox import DOMAIN, DEFAULT_PORT, async_send_media
from custom_components.sox.media_player import DEFAULT_NAME

STEP_USER_SCHEMA: Final = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_NAME): str,
    }
)


class SoXConfigFlow(ConfigFlow, domain=DOMAIN):
    """SoX configuration flow."""

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = None
        schema = STEP_USER_SCHEMA
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )

            try:
                await async_send_media(
                    user_input[CONF_HOST], port=user_input[CONF_PORT]
                )
            except (OSError, TimeoutError):
                error = "cannot_connect"
            except Exception as error:
                error = "unknown_error"
            else:
                title = user_input.get(CONF_NAME)
                if not title:
                    title = f"{DEFAULT_NAME} @ {user_input[CONF_HOST]}"
                    if user_input[CONF_PORT] != DEFAULT_PORT:
                        title += f":{user_input[CONF_PORT]}"
                return self.async_create_entry(title=title, data=user_input)

            errors = {"base": error}
            schema = self.add_suggested_values_to_schema(
                schema,
                user_input,
            )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
