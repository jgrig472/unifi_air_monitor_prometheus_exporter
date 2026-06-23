# unifi-air-exporter

A Prometheus exporter for the [UniFi Vape Detection & Air Quality Sensor](https://store.ui.com/us/en/products/up-airquality), managed by UniFi Protect.

Exposes air quality index, vape index, CO2, PM1.0/2.5/4.0/10, VOC, TVOC, NOx, temperature, and humidity as Prometheus metrics. Multiple sensors adopted into the same Protect controller are discovered and labeled automatically.

Source, full documentation, and a ready-to-import Grafana dashboard: https://github.com/jgrig472/unifi_air_monitor_prometheus_exporter

## Why username/password instead of an API key

UniFi Protect's public, API-key-based Integration API does not expose Air Quality / Vape sensor readings (as of Protect 7.1.x) — only the private session API that the Protect app itself uses has this data. So this image authenticates with a UniFi local account's username and password, not an API key. See the GitHub README for how to set up a scoped, Viewer-only account for this.

## Quick start

```bash
docker run -d \
  --name unifi-air-exporter \
  -p 9840:9840 \
  -e PROTECT_HOST=your-console-host \
  -e PROTECT_USER=prom_exporter \
  -e PROTECT_PASS=your-password \
  -e PROTECT_VERIFY_TLS=false \
  jasona1246/unifi-air-exporter
```

Metrics are then served at `http://localhost:9840/metrics`.

## docker-compose

```yaml
services:
  unifi-air-exporter:
    image: jasona1246/unifi-air-exporter:latest
    restart: unless-stopped
    ports:
      - "9840:9840"
    environment:
      PROTECT_HOST: your-console-host
      PROTECT_USER: prom_exporter
      PROTECT_PASS: your-password
      PROTECT_VERIFY_TLS: "false"
```

## Configuration

| Variable              | Required | Default | Description                                                                 |
|------------------------|----------|---------|-------------------------------------------------------------------------------|
| `PROTECT_HOST`         | yes      | —       | Hostname or IP of your UniFi OS console, no scheme and no path.             |
| `PROTECT_USER`         | yes      | —       | Local UniFi account username (Protect Viewer role recommended).             |
| `PROTECT_PASS`         | yes      | —       | Password for that account.                                                    |
| `PROTECT_VERIFY_TLS`   | no       | `false` | Set to `true` if your console has a valid (non-self-signed) TLS certificate. |
| `EXPORTER_PORT`        | no       | `9840`  | Port the exporter's `/metrics` endpoint listens on (also update `-p`/`ports` to match). |

## Tags

- `latest` — most recent build from the `main` branch.
- `<major>.<minor>.<patch>` / `<major>.<minor>` (e.g. `1.0.0`, `1.0`) — versioned releases, built from git tags.

Images are multi-arch (`linux/amd64`, `linux/arm64`).

## Metrics exposed

| Metric                               | Unit    |
|----------------------------------------|---------|
| `unifi_air_quality_index`            | index (0-500) |
| `unifi_air_vape_index`               | index (0-100) |
| `unifi_air_co2_ppm`                  | ppm     |
| `unifi_air_voc_index`                | index   |
| `unifi_air_tvoc_index`               | index   |
| `unifi_air_nox_index`                | index (not on all firmware) |
| `unifi_air_pm1_0_ugm3` / `pm2_5` / `pm4_0` / `pm10_0` | µg/m³ |
| `unifi_air_temperature_celsius`      | °C      |
| `unifi_air_humidity_percent`         | %       |
| `unifi_air_exporter_scrape_success`  | 1/0     |
