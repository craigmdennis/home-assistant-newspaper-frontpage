"""The Guardian Frontpage Camera."""
from __future__ import annotations

import logging
from datetime import timedelta

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

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Guardian Frontpage camera."""
    coordinator = GuardianFrontpageCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([GuardianFrontpageCamera(coordinator)])

class GuardianFrontpageCoordinator(DataUpdateCoordinator):
    """Coordinator for Guardian Frontpage data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Guardian Frontpage",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> str:
        """Fetch the latest image URL."""
        return await self.hass.async_add_executor_job(self._get_image_url)

    def _get_image_url(self) -> str:
        """Get the latest image URL."""
        try:
            base_url = "https://www.frontpages.com/the-guardian/"
            res = requests.get(base_url, timeout=10)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.content, "html.parser")
            
            for img in soup.find_all("img"):
                src = img.get("src", "")
                if "the-guardian" in src:
                    return urljoin("https://www.frontpages.com", src)
                    
            _LOGGER.error("No Guardian image found on the page")
            return None
        except Exception as e:
            _LOGGER.error(f"Error fetching Guardian image: {e}")
            return None

class GuardianFrontpageCamera(Camera):
    """Representation of a Guardian Frontpage camera."""

    def __init__(self, coordinator: GuardianFrontpageCoordinator) -> None:
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_name = "The Guardian Frontpage"
        self._attr_unique_id = "guardian_frontpage"

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
            _LOGGER.error(f"Error downloading Guardian image: {e}")
            return None 