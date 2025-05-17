"""The Newspaper Frontpage Camera."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import aiohttp
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
        self._image_url = None

    async def async_update(self) -> None:
        """Update the camera image."""
        await self.coordinator.async_request_refresh()
        if self.coordinator.data:
            self._image_url = self.coordinator.data
            _LOGGER.debug("Updated image URL: %s", self._image_url)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
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
                    self._image = await response.read()
            
            self._image_url = image_url
            _LOGGER.debug("Image downloaded successfully, size: %d bytes", len(self._image))
            return self._image
            
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error getting newspaper frontpage: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Error getting newspaper frontpage: %s", err)
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the camera state attributes."""
        return {
            "newspaper_id": self._newspaper_id,
            "newspaper_name": self._newspaper["name"],
            "image_url": self._image_url,
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