"""The Newspaper Frontpage integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "newspaper_frontpage"

# Configuration for different newspapers
NEWSPAPERS = {
    "guardian": {
        "name": "The Guardian",
        "section": "UK Newspapers",
    },
    "times": {
        "name": "The Times",
        "section": "UK Newspapers",
    },
    "telegraph": {
        "name": "The Daily Telegraph",
        "section": "UK Newspapers",
    },
    "independent": {
        "name": "The Independent",
        "section": "UK Newspapers",
    },
}

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Newspaper Frontpage component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Newspaper Frontpage from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Forward the setup to the camera platform using the new method
    await hass.config_entries.async_forward_entry_setups(entry, ["camera"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Forward the unload to the camera platform
    return await hass.config_entries.async_forward_entry_unload(entry, "camera") 