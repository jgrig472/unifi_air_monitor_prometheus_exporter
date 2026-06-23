import os
import sys
import time

from prometheus_client import REGISTRY, start_http_server

from unifi_air_exporter.client import ProtectClient
from unifi_air_exporter.collector import AirQualityCollector


def env(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and not val:
        sys.exit(f"Missing required env var: {name}")
    return val


def main():
    host = env("PROTECT_HOST", required=True)
    user = env("PROTECT_USER", required=True)
    password = env("PROTECT_PASS", required=True)
    verify_tls = env("PROTECT_VERIFY_TLS", "false").lower() in ("1", "true", "yes")
    port = int(env("EXPORTER_PORT", "9840"))

    client = ProtectClient(host, user, password, verify_tls=verify_tls)
    REGISTRY.register(AirQualityCollector(client))

    start_http_server(port)
    print(f"unifi-air-exporter listening on :{port}/metrics", flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
