"""DataUpdateCoordinator for acoGO integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AcoGoAPI, AcoGoAPIError
from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_PASSWORD,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class AcoGoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.api = AcoGoAPI(hass)
        self.entry = entry
        
        # Set up API credentials
        self.api.set_credentials(
            entry.data[CONF_DEVICE_ID],
            entry.data[CONF_DEVICE_PASSWORD]
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # No automatic updates
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Load initial data - called only once during setup."""
        try:
            devices = await self.api.get_devices()
            _LOGGER.info("Loaded %d devices from acoGO API", len(devices))
            return {"devices": devices}
        except AcoGoAPIError as err:
            # Try to re-authenticate if credentials are invalid
            if "authentication" in str(err).lower() or "401" in str(err):
                try:
                    _LOGGER.info("Re-authenticating with acoGO API")
                    await self.api.authenticate(
                        self.entry.data[CONF_USERNAME],
                        self.entry.data[CONF_PASSWORD],
                        self.entry.data[CONF_DEVICE_ID]
                    )
                    devices = await self.api.get_devices()
                    _LOGGER.info("Loaded %d devices after re-authentication", len(devices))
                    return {"devices": devices}
                except AcoGoAPIError as reauth_err:
                    raise UpdateFailed(f"Error re-authenticating: {reauth_err}") from reauth_err
            else:
                raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_open_gate(self, target_id: str) -> bool:
        """Open gate for specified device."""
        try:
            return await self.api.open_gate(target_id)
        except AcoGoAPIError as err:
            _LOGGER.error("Error opening gate: %s", err)
            return False 