# unifi-air-exporter

A Prometheus exporter for the [UniFi Vape Detection & Air Quality Sensor](https://store.ui.com/us/en/products/up-airquality), managed by UniFi Protect.

It exposes CO2, PM1.0/2.5/4.0/10, VOC, TVOC, NOx, AQI, vape index, temperature, and humidity as Prometheus metrics, and ships with a ready-to-import Grafana dashboard.

## Why this doesn't use an API key

UniFi Protect's public, API-key-based Integration API does **not** expose Air Quality / Vape sensor readings (as of Protect 7.1.x) — it only models the device with the generic Smart Sensor schema (light/humidity/temperature/motion), with no CO2/PM/VOC/AQI/vape fields at all.

That data only exists in Protect's private session API — the same one the Protect web/mobile app uses internally. So this exporter logs in with a **username and password**, not an API key.

### Setting up a UniFi account for this exporter

1. In UniFi OS, create a dedicated local account (e.g. `prom_exporter`) rather than reusing your own admin login.
2. Give it the **Protect** app permission at the **Viewer** (read-only) role. Note: UniFi has no way to scope an account down to a single device or sensor type — Viewer-on-Protect is the most restrictive option available, and it can see all Protect devices' data, not just the air quality sensor.
3. You do not need Network app access for this exporter. If the account also has Network permissions for other reasons, that's harmless but unnecessary here.

## Running locally (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then fill in your values
set -a && source .env && set +a

python -m unifi_air_exporter.main
```

Metrics are then available at `http://localhost:9840/metrics`.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable              | Required | Default | Description                                                                 |
|------------------------|----------|---------|-------------------------------------------------------------------------------|
| `PROTECT_HOST`         | yes      | —       | Hostname or IP of your UniFi OS console, no scheme and no path (e.g. `dragon.home.co`). |
| `PROTECT_USER`         | yes      | —       | Local UniFi account username (see above).                                    |
| `PROTECT_PASS`         | yes      | —       | Password for that account.                                                    |
| `PROTECT_VERIFY_TLS`   | no       | `false` | Set to `true` if your console has a valid (non-self-signed) TLS certificate. |
| `EXPORTER_PORT`        | no       | `9840`  | Port the exporter's `/metrics` endpoint listens on.                          |

## Running with Docker

### Docker Compose (recommended)

```bash
cp .env.example .env   # then fill in your values
docker compose up -d
```

This builds the image from the local `Dockerfile` and starts the exporter on port `9840`, reading config from `.env` via `env_file`.

### Docker CLI

```bash
docker build -t unifi-air-exporter .

docker run -d \
  --name unifi-air-exporter \
  -p 9840:9840 \
  -e PROTECT_HOST=dragon.home.co \
  -e PROTECT_USER=prom_exporter \
  -e PROTECT_PASS=your-password \
  -e PROTECT_VERIFY_TLS=false \
  unifi-air-exporter
```

## Pointing Prometheus at it

```yaml
scrape_configs:
  - job_name: unifi-air-exporter
    static_configs:
      - targets: ["<exporter-host>:9840"]
```

## Metrics exposed

| Metric                               | Unit    | Notes                                  |
|----------------------------------------|---------|-----------------------------------------|
| `unifi_air_quality_index`            | index   | 0-500 AQI                               |
| `unifi_air_vape_index`               | index   | 0-100                                    |
| `unifi_air_co2_ppm`                  | ppm     |                                           |
| `unifi_air_voc_index`                | index   | 1-500                                    |
| `unifi_air_tvoc_index`               | index   |                                           |
| `unifi_air_nox_index`                | index   | 1-500; not reported on all firmware versions |
| `unifi_air_pm1_0_ugm3`               | µg/m³   |                                           |
| `unifi_air_pm2_5_ugm3`               | µg/m³   |                                           |
| `unifi_air_pm4_0_ugm3`               | µg/m³   |                                           |
| `unifi_air_pm10_0_ugm3`              | µg/m³   |                                           |
| `unifi_air_temperature_celsius`      | °C      |                                           |
| `unifi_air_humidity_percent`         | %       |                                           |
| `unifi_air_exporter_scrape_success`  | 1/0     | 1 if the last scrape of Protect succeeded |

All sensor metrics carry `sensor_name`, `sensor_mac`, and `sensor_id` labels, so multiple Air Quality sensors adopted into the same Protect controller are all exported automatically.

## Grafana dashboard

Import [`dashboard/unifi-air-quality.json`](dashboard/unifi-air-quality.json) into Grafana (Dashboards → New → Import). You'll be prompted to pick the Prometheus datasource to bind to the `${DS_PROMETHEUS}` variable. Built and tested against Grafana 13.

## Troubleshooting

- **Login fails with `AUTHENTICATION_FAILED_ACCOUNT_LOCKED`**: the account is locked, or hasn't completed first-time setup in the UniFi OS web UI yet. Log in once via the browser, then retry.
- **Bootstrap request returns 403 after a successful login**: the account doesn't have Protect app permission — grant it Viewer access on Protect (see setup steps above).
- **A metric is missing for your sensor**: not every firmware version reports every field (e.g. `nox` is absent on some). The exporter only emits metrics for fields the device actually returns.
