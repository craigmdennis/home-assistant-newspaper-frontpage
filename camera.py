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

from . import NEWSPAPERS

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Newspaper Frontpage cameras."""
    # Create a coordinator for each newspaper
    coordinators = {}
    cameras = []
    
    for newspaper_id, newspaper in NEWSPAPERS.items():
        # Create coordinator for this newspaper
        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"newspaper_frontpage_{newspaper_id}",
            update_interval=SCAN_INTERVAL,
        )
        coordinators[newspaper_id] = coordinator
        
        # Create camera entity
        camera = NewspaperFrontpageCamera(coordinator, newspaper_id, newspaper)
        cameras.append(camera)
    
    # Add all cameras
    async_add_entities(cameras)

class NewspaperFrontpageCamera(Camera):
    """Representation of a Newspaper Frontpage camera."""

    def __init__(self, coordinator: DataUpdateCoordinator, newspaper_id: str, newspaper: Dict[str, Any]) -> None:
        """Initialize a Newspaper Frontpage camera."""
        super().__init__()
        self.coordinator = coordinator
        self._newspaper_id = newspaper_id
        self._newspaper = newspaper
        self._attr_name = f"{newspaper['name']} Frontpage"
        self._attr_unique_id = f"newspaper_frontpage_{newspaper_id}"
        self._image = None

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        try:
            # Get the front page image
            response = requests.get(self._newspaper["base_url"])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Add your image extraction logic here based on the newspaper's HTML structure
            # This is a placeholder - you'll need to implement the actual image extraction
            image_url = "https://example.com/frontpage.jpg"  # Replace with actual image URL
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            self._image = image_response.content
            return self._image
            
        except Exception as err:
            _LOGGER.error("Error getting newspaper frontpage: %s", err)
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the camera state attributes."""
        return {
            "newspaper_id": self._newspaper_id,
            "newspaper_name": self._newspaper["name"],
        }

def get_image_url():
    try:
        # First get the main page
        base_url = "https://www.frontpages.com/the-guardian/"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(res.content, "html.parser")
        
        # Look for any image that contains 'the-guardian' in its src
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "the-guardian" in src:
                # Convert relative URL to absolute URL
                return urljoin("https://www.frontpages.com", src)
                
        print("No Guardian image found on the page")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def download_image(url, filename="guardian_frontpage.jpg"):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"Image saved as {filename}")
    except Exception as e:
        print(f"Failed to download image: {e}")

if __name__ == "__main__":
    img_url = get_image_url()
    if img_url:
        print(f"Found image URL: {img_url}")
        download_image(img_url)
    else:
        print("No image URL found.")