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
        "base_url": "https://www.theguardian.com/",
        "image_pattern": "the-guardian",
    },
    "times": {
        "name": "The Times",
        "base_url": "https://www.thetimes.co.uk/",
        "image_pattern": "the-times",
    },
    "telegraph": {
        "name": "The Telegraph",
        "base_url": "https://www.telegraph.co.uk/",
        "image_pattern": "the-telegraph",
    },
    "independent": {
        "name": "The Independent",
        "base_url": "https://www.independent.co.uk/",
        "image_pattern": "the-independent",
    },
}

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Newspaper Frontpage component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Newspaper Frontpage from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Forward the setup to the camera platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "camera")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Forward the unload to the camera platform
    return await hass.config_entries.async_forward_entry_unload(entry, "camera") 