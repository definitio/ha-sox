# SoX component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant integration to turn your vacuum into an audio player.

## Installation

1. Install firmware for your Xiaomi (Roborock) vacuum - use [pre-build firmware](https://github.com/zvldz/vacuum#already-build-firmware) or [build it yourself](https://github.com/zvldz/vacuum) with `--enable-sound-server` option.
2. Install the integration to Home Assistant: use [HACS](https://hacs.xyz/) or copy the contents of `custom_components/sox/` to `<your config dir>/custom_components/sox/`.
3. Configure in the Home Assistant `configuration.yaml` (See the [Configuration](#configuration) and [Configuration Options](#configuration-options) sections below)
4. Restart Home Assistant.

## <a name="configuration"></a> Configuration

To enable the SoX integration, add the following lines to your Home Assistant's `configuration.yaml` file:

```yaml
media_player:
  - platform: sox
    name: sox
    host: <server hostname or IP address>
    port: 7777
```

## <a name="configuration-options"></a> Configuration Options

- **name:** *(string) (Optional)*

  This is the name you would like to give to SoX media player.
  
    *Default value: `sox`*

- **host:** *(string) (Required)*

  This is the hostname, domain name or IP address of your vacuum.

- **port:** *(string) (Optional)*

  This is the port that the SoX player on your vacuum can be reached at.

    *Default value: `7777`*
