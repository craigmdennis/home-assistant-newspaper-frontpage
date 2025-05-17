"""Config flow for Newspaper Frontpage integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from . import NEWSPAPERS

_LOGGER = logging.getLogger(__name__)

class NewspaperFrontpageConfigFlow(config_entries.ConfigFlow, domain="newspaper_frontpage"):
    """Handle a config flow for Newspaper Frontpage."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            newspaper_id = user_input["newspaper_id"]
            
            # Check if this newspaper is already configured
            await self.async_set_unique_id(newspaper_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Newspaper Frontpages",  # Generic title for the device
                data={"newspaper_id": newspaper_id},
            )

        # Create a list of newspaper options
        newspaper_options = {
            newspaper_id: data["name"]
            for newspaper_id, data in NEWSPAPERS.items()
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("newspaper_id"): vol.In(newspaper_options)
            }),
        ) 