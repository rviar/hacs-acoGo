"""Constants for the acoGO integration."""

DOMAIN = "acogo"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_PASSWORD = "device_password"

# API endpoints
API_BASE_URL = "https://api.aco.com.pl/listener/v1"
API_DEVICE_ENDPOINT = f"{API_BASE_URL}/device"
API_PREVIEW_ENDPOINT = f"{API_BASE_URL}/preview"
API_ORDER_ENDPOINT = f"{API_BASE_URL}/order"

# Default values
DEFAULT_TIMEOUT = 10

# Device info
DEVICE_MODEL = 63
DEVICE_NAME = "acoGO! MobileApp"
DEVICE_FIRMWARE = "18.4.1"
DEVICE_SOFTWARE = "1.8.2"
DEVICE_HARDWARE = "ha" 