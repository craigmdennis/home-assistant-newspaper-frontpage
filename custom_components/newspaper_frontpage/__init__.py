"""The Newspaper Frontpage integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "newspaper_frontpage"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Newspaper Frontpage component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigType) -> bool:
    """Set up Newspaper Frontpage from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigType) -> bool:
    """Unload a config entry."""
    return True 