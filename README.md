# SoX component for Home Assistant

A Home Assistant integration to turn your vacuum into an audio player.

1. Build and install firmware for your Xiaomi (Roborock) vacuum - [build firmware](https://github.com/zvldz/vacuum) with `--enable-sound-server` option.
2. Install the integration to Home Assistant: use [HACS](https://hacs.xyz/) or copy the contents of `custom_components/sox/` to `<your config dir>/custom_components/sox/`.
3. Add to configuration.yaml:

```yaml
media_player:
  - platform: sox
    name: Vacuum
    host: <server hostname or IP address>
    port: 7777 # Optional
```

4. Restart Home Assistant.
