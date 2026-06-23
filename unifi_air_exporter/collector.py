from prometheus_client.core import GaugeMetricFamily

# airQuality key -> (metric name, help text)
METRICS = {
    "aqi": ("unifi_air_quality_index", "Overall air quality index (0-500)"),
    "vape": ("unifi_air_vape_index", "Vape detection index (0-100)"),
    "co2": ("unifi_air_co2_ppm", "CO2 concentration in ppm"),
    "tvoc": ("unifi_air_tvoc_index", "Total VOC index"),
    "voc": ("unifi_air_voc_index", "VOC index (1-500)"),
    "nox": ("unifi_air_nox_index", "NOx index (1-500)"),
    "pm1p0": ("unifi_air_pm1_0_ugm3", "PM1.0 concentration in ug/m3"),
    "pm2p5": ("unifi_air_pm2_5_ugm3", "PM2.5 concentration in ug/m3"),
    "pm4p0": ("unifi_air_pm4_0_ugm3", "PM4.0 concentration in ug/m3"),
    "pm10p0": ("unifi_air_pm10_0_ugm3", "PM10 concentration in ug/m3"),
    "temperature": ("unifi_air_temperature_celsius", "Temperature in degrees Celsius"),
    "humidity": ("unifi_air_humidity_percent", "Relative humidity percentage"),
}

LABELS = ["sensor_name", "sensor_mac", "sensor_id"]


class AirQualityCollector:
    def __init__(self, client):
        self.client = client

    def collect(self):
        up = GaugeMetricFamily(
            "unifi_air_exporter_scrape_success",
            "1 if the last scrape of the Protect controller succeeded, else 0",
        )
        families = {
            key: GaugeMetricFamily(name, help_text, labels=LABELS)
            for key, (name, help_text) in METRICS.items()
        }

        try:
            sensors = self.client.air_quality_sensors()
        except Exception as e:
            print(f"scrape failed: {e}", flush=True)
            up.add_metric([], 0)
            yield up
            return

        for sensor in sensors:
            labels = [
                sensor.get("name") or "",
                sensor.get("mac") or "",
                sensor.get("id") or "",
            ]
            for key, reading in (sensor.get("airQuality") or {}).items():
                family = families.get(key)
                if family is None or not isinstance(reading, dict):
                    continue
                value = reading.get("value")
                if value is not None:
                    family.add_metric(labels, value)

        up.add_metric([], 1)
        yield up
        for family in families.values():
            yield family
