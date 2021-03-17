# SoX component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

A Home Assistant integration to turn your vacuum into an audio player.

## Installation

- Install firmware for your Xiaomi (Roborock) vacuum - use [pre-build firmware](https://github.com/zvldz/vacuum#already-build-firmware) or [build it yourself](https://github.com/zvldz/vacuum) with `--enable-sound-server` option.
- Install the integration to Home Assistant: use [HACS](https://hacs.xyz/) or copy the contents of `custom_components/sox/` to `<your config dir>/custom_components/sox/`.

## Configuration

- Add the following lines to your Home Assistant's `configuration.yaml` file:

```yaml
media_player:
  - platform: sox
    name: sox
    host: <server hostname or IP address>
    port: 7777
```

- Restart Home Assistant

### Configuration Options

- **name:** _(string) (Optional)_

  This is the name you would like to give to SoX media player.

  _Default value: `sox`_

- **host:** _(string) (Required)_

  This is the hostname, domain name or IP address of your vacuum.

- **port:** _(string) (Optional)_

  This is the port that the SoX player on your vacuum can be reached at.

  _Default value: `7777`_

## Useful links

- [Media Player documentation](https://www.home-assistant.io/integrations/media_player)
- [Home Assistant forum](https://community.home-assistant.io)
