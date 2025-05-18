"""The Newspaper Frontpage Image."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo

from . import NEWSPAPERS, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)
FRONTPAGES_URL = "https://www.frontpages.com/"

# Map newspaper IDs to their correct URL paths
NEWSPAPER_URLS = {
    "guardian": "the-guardian",
    "times": "the-times",
    "telegraph": "the-daily-telegraph",
    "independent": "the-independent",
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Newspaper Frontpage images."""
    newspaper_id = config_entry.data["newspaper_id"]
    newspaper = NEWSPAPERS[newspaper_id]
    
    # Create coordinator for this newspaper
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"newspaper_frontpage_{newspaper_id}",
        update_interval=SCAN_INTERVAL,
    )
    
    # Create image entity
    image = NewspaperFrontpageImage(
        hass,
        coordinator,
        newspaper_id,
        newspaper,
        config_entry.entry_id
    )
    
    # Add the image entity
    async_add_entities([image])

class NewspaperFrontpageImage(ImageEntity):
    """Representation of a Newspaper Frontpage image."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        newspaper_id: str,
        newspaper: Dict[str, Any],
        entry_id: str
    ) -> None:
        """Initialize a Newspaper Frontpage image."""
        super().__init__(hass)
        self.coordinator = coordinator
        self._newspaper_id = newspaper_id
        self._newspaper = newspaper
        self._entry_id = entry_id
        self._attr_name = "Frontpage"
        self._attr_unique_id = f"{newspaper_id}_frontpage"
        self._image_url = None
        self._attr_entity_picture = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._newspaper_id)},
            name=self._newspaper["name"],
            manufacturer="Newspaper Frontpage",
            model="Digital Edition",
            entry_type="service",
        )

    async def async_update(self) -> None:
        """Update the image."""
        await self.coordinator.async_request_refresh()
        if self.coordinator.data:
            self._image_url = self.coordinator.data
            self._attr_entity_picture = self._image_url
            _LOGGER.debug("Updated image URL: %s", self._image_url)

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""
        try:
            # Get the correct URL path for this newspaper
            url_path = NEWSPAPER_URLS.get(self._newspaper_id)
            if not url_path:
                _LOGGER.error("No URL mapping found for newspaper: %s", self._newspaper_id)
                return None

            # Construct the newspaper's URL
            newspaper_url = urljoin(FRONTPAGES_URL, f"{url_path}/")
            _LOGGER.debug("Fetching newspaper page: %s", newspaper_url)
            
            async with aiohttp.ClientSession() as session:
                # Get the newspaper page
                async with session.get(newspaper_url, timeout=10) as response:
                    response.raise_for_status()
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find the front page image - it's typically the first large image on the page
            # Look for images with specific classes or attributes that indicate it's the front page
            img = soup.find('img', {'class': 'giornale-img'})
            
            if not img:
                # Fallback: look for any image that contains the newspaper name in its src
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if url_path in src.lower():
                        break
                else:
                    _LOGGER.error("Could not find front page image for %s", self._newspaper["name"])
                    return None
            
            if not img.get('src'):
                _LOGGER.error("Image found but no src attribute for %s", self._newspaper["name"])
                return None
            
            # Get the image
            image_url = urljoin(newspaper_url, img['src'])
            _LOGGER.debug("Found image URL: %s", image_url)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=10) as response:
                    response.raise_for_status()
                    image_data = await response.read()
            
            self._image_url = image_url
            self._attr_entity_picture = image_url
            _LOGGER.debug("Image downloaded successfully, size: %d bytes", len(image_data))
            return image_data
            
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error getting newspaper frontpage: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Error getting newspaper frontpage: %s", err)
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the image state attributes."""
        return {
            "newspaper_id": self._newspaper_id,
            "newspaper_name": self._newspaper["name"],
            "image_url": self._image_url,
        } 