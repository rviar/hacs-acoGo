"""API client for acoGO integration."""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_DEVICE_ENDPOINT,
    API_ORDER_ENDPOINT,
    API_PREVIEW_ENDPOINT,
    DEFAULT_TIMEOUT,
    DEVICE_FIRMWARE,
    DEVICE_HARDWARE,
    DEVICE_MODEL,
    DEVICE_NAME,
    DEVICE_SOFTWARE,
)

_LOGGER = logging.getLogger(__name__)


class AcoGoAPIError(Exception):
    """Exception to indicate an API error."""


class AcoGoAPI:
    """API client for acoGO."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.session = async_get_clientsession(hass)
        self._device_id: str | None = None
        self._device_password: str | None = None

    def generate_device_id(self) -> str:
        """Generate a unique device ID."""
        return str(uuid.uuid4()).upper()

    async def authenticate(self, username: str, password: str, device_id: str | None = None) -> dict[str, Any]:
        """Authenticate with the acoGO API."""
        if device_id is None:
            device_id = self.generate_device_id()
        
        headers = {
            "Host": "api.aco.com.pl",
            "content-type": "application/json",
            "accept": "text/plain, */*",
            "sec-fetch-site": "cross-site",
            "accept-language": "en-GB,en;q=0.9",
            "sec-fetch-mode": "cors",
            "devid": device_id,
            "origin": "ionic://localhost",
            "username": username,
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "userpassword": password,
            "sec-fetch-dest": "empty",
        }

        data = {
            "language": "en",
            "name": DEVICE_NAME,
            "localization": "",
            "firmware": DEVICE_FIRMWARE,
            "software": DEVICE_SOFTWARE,
            "hardware": DEVICE_HARDWARE,
            "model": DEVICE_MODEL,
        }

        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with self.session.post(
                    API_DEVICE_ENDPOINT,
                    headers=headers,
                    json=data
                ) as resp:
                    if resp.status not in (200, 201):
                        raise AcoGoAPIError(f"Authentication failed: {resp.status}")
                    
                    result = await resp.json()
                    
                    if "additionalInfo" not in result or "devicePassword" not in result["additionalInfo"]:
                        raise AcoGoAPIError("Invalid response: missing devicePassword")
                    
                    self._device_id = device_id
                    self._device_password = result["additionalInfo"]["devicePassword"]
                    
                    return result
        
        except asyncio.TimeoutError as err:
            raise AcoGoAPIError("Authentication timeout") from err
        except aiohttp.ClientError as err:
            raise AcoGoAPIError(f"Authentication error: {err}") from err

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get available devices."""
        if not self._device_id or not self._device_password:
            raise AcoGoAPIError("Not authenticated")

        headers = {
            "Host": "api.aco.com.pl",
            "content-type": "application/json",
            "accept": "text/plain, */*",
            "sec-fetch-site": "cross-site",
            "accept-language": "en-GB,en;q=0.9",
            "sec-fetch-mode": "cors",
            "devid": self._device_id,
            "origin": "ionic://localhost",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "devicepassword": self._device_password,
            "sec-fetch-dest": "empty",
        }

        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with self.session.get(
                    API_PREVIEW_ENDPOINT,
                    headers=headers
                ) as resp:
                    if resp.status not in (200, 201):
                        raise AcoGoAPIError(f"Failed to get devices: {resp.status}")
                    
                    return await resp.json()
        
        except asyncio.TimeoutError as err:
            raise AcoGoAPIError("Get devices timeout") from err
        except aiohttp.ClientError as err:
            raise AcoGoAPIError(f"Get devices error: {err}") from err

    async def open_gate(self, target_id: str) -> bool:
        """Open gate for specified device."""
        if not self._device_id or not self._device_password:
            raise AcoGoAPIError("Not authenticated")

        headers = {
            "Host": "api.aco.com.pl",
            "content-type": "application/json",
            "accept": "text/plain, */*",
            "sec-fetch-site": "cross-site",
            "accept-language": "en-GB,en;q=0.9",
            "sec-fetch-mode": "cors",
            "devid": self._device_id,
            "origin": "ionic://localhost",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "devicepassword": self._device_password,
            "sec-fetch-dest": "empty",
        }

        data = {
            "address": None,
            "targetId": target_id,
        }

        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with self.session.post(
                    f"{API_ORDER_ENDPOINT}?orderId=ezOpen",
                    headers=headers,
                    json=data
                ) as resp:
                    return resp.status in (200, 201, 202)
        
        except asyncio.TimeoutError as err:
            raise AcoGoAPIError("Open gate timeout") from err
        except aiohttp.ClientError as err:
            raise AcoGoAPIError(f"Open gate error: {err}") from err

    def set_credentials(self, device_id: str, device_password: str) -> None:
        """Set device credentials."""
        self._device_id = device_id
        self._device_password = device_password

    @property
    def device_id(self) -> str | None:
        """Get device ID."""
        return self._device_id

    @property
    def device_password(self) -> str | None:
        """Get device password."""
        return self._device_password 