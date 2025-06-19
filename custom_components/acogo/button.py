"""Button platform for acoGO integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AcoGoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up acoGO button platform."""
    coordinator: AcoGoDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    if coordinator.data and "devices" in coordinator.data:
        entities = []
        for device in coordinator.data["devices"]:
            entities.append(AcoGoGateButton(coordinator, device))
        async_add_entities(entities)


class AcoGoGateButton(CoordinatorEntity, ButtonEntity):
    """Representation of acoGO gate button."""

    def __init__(
        self,
        coordinator: AcoGoDataUpdateCoordinator,
        device: dict[str, Any],
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device['devId']}_open_gate"
        self._attr_name = f"Open Gate {device['devId']}"
        self._attr_icon = "mdi:gate"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device["devId"])},
            "name": f"acoGO Gate {self._device['devId']}",
            "manufacturer": "ACO",
            "model": "Gate Controller",
            "via_device": (DOMAIN, self.coordinator.entry.entry_id),
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Opening gate for device %s", self._device["devId"])
        success = await self.coordinator.async_open_gate(self._device["devId"])
        
        if success:
            _LOGGER.info("Gate opened successfully for device %s", self._device["devId"])
        else:
            _LOGGER.error("Failed to open gate for device %s", self._device["devId"]) 