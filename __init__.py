"""The Newspaper Frontpage integration."""
from __future__ import annotations

import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "newspaper_frontpage"

# Configuration for different newspapers
NEWSPAPERS = {
    "guardian": {
        "name": "The Guardian",
        "url": "https://www.frontpages.com/the-guardian/",
    },
    "times": {
        "name": "The Times",
        "url": "https://www.frontpages.com/the-times/",
    },
    "telegraph": {
        "name": "The Daily Telegraph",
        "url": "https://www.frontpages.com/the-daily-telegraph/",
    },
    "independent": {
        "name": "The Independent",
        "url": "https://www.frontpages.com/the-independent/",
    },
}

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Newspaper Frontpage component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Newspaper Frontpage from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Forward the setup to the image platform
    await hass.config_entries.async_forward_entry_setups(entry, ["image"])
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Forward the unload to the image platform
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "image")
    
    # Clean up the data
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    
    return unload_ok 