import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AIR_QUALITY_TYPE = "UP-AirQuality"


class ProtectAuthError(RuntimeError):
    pass


class ProtectClient:
    """Reads UniFi Protect's private session-API (the one the Protect app
    itself uses), since the public API-key Integration API does not expose
    Air Quality / Vape sensor readings (CO2, PM*, VOC, NOx, AQI, vape index)
    as of Protect 7.1.x.
    """

    def __init__(self, host, username, password, verify_tls=True, timeout=10):
        host = host.strip().rstrip("/")
        if "://" in host:
            host = host.split("://", 1)[1]
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = verify_tls

    def _url(self, path):
        return f"https://{self.host}{path}"

    def login(self):
        resp = self.session.post(
            self._url("/api/auth/login"),
            json={"username": self.username, "password": self.password},
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise ProtectAuthError(f"login failed: HTTP {resp.status_code}")

    def bootstrap(self):
        if "TOKEN" not in self.session.cookies:
            self.login()
        resp = self.session.get(self._url("/proxy/protect/api/bootstrap"), timeout=self.timeout)
        if resp.status_code in (401, 403):
            self.login()
            resp = self.session.get(self._url("/proxy/protect/api/bootstrap"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def air_quality_sensors(self):
        data = self.bootstrap()
        return [s for s in data.get("sensors", []) if s.get("type") == AIR_QUALITY_TYPE]
