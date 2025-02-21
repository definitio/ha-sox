"""Support for interacting with the SoX music player."""

import logging
import asyncio
from typing import Final

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components import media_source
from homeassistant.components.media_player import (
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.components.media_player.browse_media import (
    async_process_play_media_url,
    BrowseMedia,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant

from custom_components.sox import DOMAIN, DEFAULT_PORT, async_send_media

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME: Final = "SoX"

SUPPORTED_FEATURES_DEFAULT = (
    MediaPlayerEntityFeature.BROWSE_MEDIA
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PLAY_MEDIA
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Inclusive(CONF_HOST, "remote"): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the SoX platform."""

    host = config_entry.data[CONF_HOST]
    port = config_entry.data[CONF_PORT]

    await async_setup_platform(
        hass,
        {
            CONF_HOST: host,
            CONF_PORT: port,
            CONF_NAME: config_entry.title,
        },
        async_add_entities,
        unique_id=f"{host}:{port}",
    )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discover_info: DiscoveryInfoType | None = None,
    unique_id: str | None = None,
):
    """Set up the SoX platform."""
    # del discover_info
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    name = config[CONF_NAME]

    device = SoXDevice(host, port, name, unique_id)
    add_entities([device], True)


class SoXDevice(MediaPlayerEntity):
    """Representation of a running SoX."""

    def __init__(self, host, port, name, unique_id: str | None = None):
        """Initialize the SoX device."""
        self._host = host
        self._port = port

        self._attr_name = name
        self._attr_unique_id = unique_id or name or "{}:{}".format(host, port)
        self._attr_is_volume_muted = False

        self._is_connected = None
        self._is_playing = False
        self._muted_volume = None

    @property
    def available(self):
        """Return true if MPD is available and connected."""
        return self._is_connected

    @property
    def state(self):
        """Return the media state."""
        if self._is_playing:
            return MediaPlayerState.PLAYING
        return MediaPlayerState.IDLE

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        supported = SUPPORTED_FEATURES_DEFAULT

        if self._attr_volume_level is not None:
            supported |= (
                MediaPlayerEntityFeature.STOP
                | MediaPlayerEntityFeature.VOLUME_SET
                | MediaPlayerEntityFeature.VOLUME_STEP
                | MediaPlayerEntityFeature.VOLUME_MUTE
            )

        return supported

    async def async_mute_volume(self, mute):
        """Mute. Emulated with set_volume_level."""
        if self.volume_level is not None and mute != self._attr_is_volume_muted:
            if mute:
                self._muted_volume = self.volume_level
                await self.async_set_volume_level(0)
            elif self._muted_volume is not None:
                await self.async_set_volume_level(self._muted_volume)
            self._attr_is_volume_muted = mute

    async def async_set_volume_level(self, volume):
        """Set volume of media player."""
        self._attr_volume_level = round(volume, 2)
        if self._is_playing:
            await self.async_media_stop()
            await self.async_media_play()

    async def async_media_play(self):
        """Send play command."""
        media_id = self.hass.data[DOMAIN].get(self.unique_id)
        if media_id is not None:
            _LOGGER.debug(
                "SoX play: %s",
            )
            await self._async_send(media_id)

    async def async_media_stop(self):
        """Send stop command."""
        await self._async_send("stop")

    async def async_browse_media(
        self,
        media_content_type: MediaType | str | None = None,
        media_content_id: str | None = None,
    ) -> BrowseMedia:
        """Implement the websocket media browsing helper."""
        return await media_source.async_browse_media(
            self.hass,
            media_content_id,
            content_filter=lambda item: item.media_content_type.startswith("audio/"),
        )

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Send the play command."""
        del kwargs

        if media_source.is_media_source_id(media_id):
            media_type = MediaType.MUSIC
            play_item = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = async_process_play_media_url(self.hass, play_item.url)

        if media_type in [MediaType.MUSIC, MediaType.PLAYLIST]:
            await self._async_send(media_id)
            self.hass.data[DOMAIN][self.unique_id] = media_id
        else:
            _LOGGER.error(
                "Invalid media type %s. Only %s and %s are supported",
                media_type,
                MediaType.MUSIC,
                MediaType.PLAYLIST,
            )

    async def _async_send(self, media_id):
        try:
            is_playing, volume_level = await async_send_media(
                self._host, media_id, self.volume_level, self._port
            )

        except (asyncio.TimeoutError, OSError) as err:
            _LOGGER.debug("Async SoX connection error: %s", err)
            self._is_connected = False
            raise err
        else:
            self._is_connected = True
            if is_playing is not None:
                self._is_playing = is_playing
            if volume_level is not None:
                self._attr_volume_level = volume_level

    async def async_volume_up(self):
        """Service to send the MPD the command for volume up."""
        if self.volume_level is not None:
            current_volume = self.volume_level

            if current_volume < 1:
                await self.async_set_volume_level(min(current_volume + 0.05, 1))

    async def async_volume_down(self):
        """Service to send the MPD the command for volume down."""
        if self.volume_level is not None:
            current_volume = self.volume_level

            if current_volume > 0:
                await self.async_set_volume_level(max(current_volume - 0.05, 0))

    async def async_update(self):
        """Get the latest data and update the state."""
        if not self._is_connected or self._attr_volume_level is not None:
            try:
                await self._async_send("")  # For compatibility with old sound server
            except:
                pass
