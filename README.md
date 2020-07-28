# HomeAssistant - SoX component

This is a custom component to allow play sounds over network via SoX. Can be used for Xiaomi vacuums - [build firmware](https://github.com/zvldz/vacuum) with `--enable-sound-server` option.

## Example configuration.yaml
```yaml
media_player:
  - platform: sox
    name: Vacuum
    host: vacuum.lan
    port: 7777
```
