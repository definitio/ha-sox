"""Support for interacting with the SoX music player."""
import logging
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

import voluptuous as vol

from homeassistant.components.media_player import MediaPlayerEntity, PLATFORM_SCHEMA
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_PLAYLIST,
    SUPPORT_PLAY_MEDIA,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    STATE_OFF,
    STATE_PLAYING,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "sox"
DEFAULT_PORT = 7777

SUPPORT_SOX = SUPPORT_PLAY_MEDIA

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Inclusive(CONF_HOST, "remote"): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discover_info):
    """Set up the SoX platform."""
    del hass, discover_info
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    name = config.get(CONF_NAME)

    device = SoXDevice(host, port, name)
    add_entities([device], True)


class SoXDevice(MediaPlayerEntity):
    """Representation of a running SoX."""

    def __init__(self, host, port, name):
        """Initialize the SoX device."""
        self._host = host
        self._port = port
        self._name = name
        self._play = False

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the media state."""
        if self._play:
            return STATE_PLAYING
        return STATE_OFF

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_SOX

    def play_media(self, media_type, media_id, **kwargs):
        """Send the play command."""
        del kwargs
        if media_type in [MEDIA_TYPE_MUSIC, MEDIA_TYPE_PLAYLIST]:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((self._host, self._port))
            self._play = True
            sock.sendall("{};".format(media_id).encode())
            sock.close()
            sleep(10)
            self._play = False
        else:
            _LOGGER.error(
                "Invalid media type %s. Only %s and %s are supported",
                media_type,
                MEDIA_TYPE_MUSIC,
                MEDIA_TYPE_PLAYLIST,
            )
