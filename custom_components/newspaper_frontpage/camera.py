"""The Newspaper Frontpage Camera."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)

# Configuration for different newspapers
NEWSPAPERS = {
    "guardian": {
        "name": "The Guardian",
        "base_url": "https://www.frontpages.com/the-guardian/",
        "image_pattern": "the-guardian",
    },
    # Add more newspapers here as needed
    # "times": {
    #     "name": "The Times",
    #     "base_url": "https://www.frontpages.com/the-times/",
    #     "image_pattern": "the-times",
    # },
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Newspaper Frontpage cameras."""
    newspaper_id = config_entry.data.get("newspaper_id", "guardian")
    if newspaper_id not in NEWSPAPERS:
        _LOGGER.error(f"Unknown newspaper ID: {newspaper_id}")
        return

    coordinator = NewspaperFrontpageCoordinator(hass, newspaper_id)
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([NewspaperFrontpageCamera(coordinator, newspaper_id)])

class NewspaperFrontpageCoordinator(DataUpdateCoordinator):
    """Coordinator for Newspaper Frontpage data."""

    def __init__(self, hass: HomeAssistant, newspaper_id: str) -> None:
        """Initialize the coordinator."""
        self.newspaper_id = newspaper_id
        self.newspaper_config = NEWSPAPERS[newspaper_id]
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{self.newspaper_config['name']} Frontpage",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> str:
        """Fetch the latest image URL."""
        return await self.hass.async_add_executor_job(self._get_image_url)

    def _get_image_url(self) -> str:
        """Get the latest image URL."""
        try:
            base_url = self.newspaper_config["base_url"]
            res = requests.get(base_url, timeout=10)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.content, "html.parser")
            
            for img in soup.find_all("img"):
                src = img.get("src", "")
                if self.newspaper_config["image_pattern"] in src:
                    return urljoin("https://www.frontpages.com", src)
                    
            _LOGGER.error(f"No {self.newspaper_config['name']} image found on the page")
            return None
        except Exception as e:
            _LOGGER.error(f"Error fetching {self.newspaper_config['name']} image: {e}")
            return None

class NewspaperFrontpageCamera(Camera):
    """Representation of a Newspaper Frontpage camera."""

    def __init__(self, coordinator: NewspaperFrontpageCoordinator, newspaper_id: str) -> None:
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self.newspaper_id = newspaper_id
        self.newspaper_config = NEWSPAPERS[newspaper_id]
        
        self._attr_name = f"{self.newspaper_config['name']} Frontpage"
        self._attr_unique_id = f"newspaper_frontpage_{self.newspaper_id}"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        image_url = self.coordinator.data
        if not image_url:
            return None

        try:
            response = await self.hass.async_add_executor_job(
                requests.get, image_url, {"timeout": 10}
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            _LOGGER.error(f"Error downloading {self.newspaper_config['name']} image: {e}")
            return None 