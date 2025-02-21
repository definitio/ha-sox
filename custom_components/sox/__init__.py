"""The SoX component."""

import asyncio
import logging
from typing import Final
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "sox"

DEFAULT_PORT = 7777

PLATFORMS: Final = ["media_player"]

CONFIG_SCHEMA: Final = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_send_media(
    host: str,
    media_id: str | None = None,
    volume_level: float | None = None,
    port: int = DEFAULT_PORT,
):
    """Send media_id to SoX."""
    reader, writer = (None, None)
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=5
        )
        if media_id is None:
            media_id = ""
        if volume_level is None:
            volume_level = 1.0
        # Set a timeout for operations
        payload = f"{media_id};{volume_level};".encode()
        _LOGGER.debug("Sending payload to host [%s:%s]: %s", host, port, payload)
        writer.write(payload)
        await writer.drain()
        # Try to receive data with a timeout
        data = await asyncio.wait_for(reader.read(256), timeout=5)
        output = data.decode("utf-8").rstrip()
        _LOGGER.debug("Received data from host [%s:%s]: %s", host, port, output)

        volume_level = None
        is_playing = None
        if "=" in output and ";" in output:
            output_parsed = dict(x.split("=") for x in output.split(";"))
            if "volume" in output_parsed.keys():
                volume_level = float(output_parsed["volume"])
            is_playing = output_parsed.get("playing") == "True" or False
        return is_playing, volume_level
    except Exception as exc:
        _LOGGER.error("Error communicating with host [%s:%s]: %s", host, port, exc)
        raise
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the SoX component."""
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the SoX entry."""

    # Forward entry setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Create options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Finished config entry setup")

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload configuration entry"""
    _LOGGER.info("Reloading configuration entry")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload configuration entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
