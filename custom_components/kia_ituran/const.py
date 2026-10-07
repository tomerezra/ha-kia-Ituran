"""Constants for Kia EV (Ituran)."""
from datetime import timedelta

DOMAIN = "kia_ituran"
CONF_PLATFORM_ID = "platform_id"

API_URL = (
    "https://app.ituran.com/ituranmobileservice/mobileservice.asmx/GetElectricData"
)
USER_AGENT = "MY KIA/1.2.15 (IOS)"
SCAN_INTERVAL = timedelta(minutes=5)
