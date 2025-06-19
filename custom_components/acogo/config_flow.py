"""Config flow for acoGO integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import AcoGoAPI, AcoGoAPIError
from .const import CONF_DEVICE_ID, CONF_DEVICE_PASSWORD, CONF_PASSWORD, CONF_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = AcoGoAPI(hass)
    
    try:
        auth_result = await api.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD])
        device_id = api.device_id
        device_password = api.device_password
        
        if not device_id or not device_password:
            raise InvalidAuth("Failed to get device credentials")
        
        # Test getting devices to verify everything works
        devices = await api.get_devices()
        
        return {
            "title": f"acoGO ({data[CONF_USERNAME]})",
            CONF_USERNAME: data[CONF_USERNAME],
            CONF_PASSWORD: data[CONF_PASSWORD],
            CONF_DEVICE_ID: device_id,
            CONF_DEVICE_PASSWORD: device_password,
            "devices_count": len(devices),
        }
    
    except AcoGoAPIError as err:
        _LOGGER.error("Authentication failed: %s", err)
        raise InvalidAuth from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for acoGO."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_USERNAME: info[CONF_USERNAME],
                        CONF_PASSWORD: info[CONF_PASSWORD],
                        CONF_DEVICE_ID: info[CONF_DEVICE_ID],
                        CONF_DEVICE_PASSWORD: info[CONF_DEVICE_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth.""" 