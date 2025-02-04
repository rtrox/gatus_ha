"""Config flow for Gatus Uptime Monitors integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_NAME,
    CONF_URL,
    CONF_VERIFY_SSL,
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.util import slugify

from .api import (
    GatusApiClient,
    GatusApiClientConnectionError,
    GatusApiClientDNSError,
    GatusApiClientError,
    GatusApiClientSSLError,
    GatusApiClientTimeoutError,
)
from .const import DOMAIN, LOGGER


class GatusFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gatus Uptime Monitors integration."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    url=user_input[CONF_URL],
                    verifyssl=user_input[CONF_VERIFY_SSL],
                )
            except GatusApiClientTimeoutError as e:
                LOGGER.warning("Timeout error: %s", e)
                _errors["base"] = "timeout"
            except GatusApiClientError as e:
                LOGGER.error("Error: %s", e)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=(user_input or {}).get(CONF_NAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Required(
                        CONF_URL,
                        default=(user_input or {}).get(CONF_URL, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        )
                    ),
                    vol.Required(
                        CONF_VERIFY_SSL,
                        default=(user_input or {}).get(CONF_NAME, True),
                    ): selector.BooleanSelector(
                        selector.BooleanSelectorConfig(),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_connection(self, url: str, verifyssl: bool) -> dict[str, str]:  # noqa: FBT001
        errors: dict[str, str] = {}
        client = GatusApiClient(url, async_create_clientsession(self.hass), verifyssl)
        try:
            await client.async_get_config()
        except GatusApiClientTimeoutError as e:
            LOGGER.warning("Timeout error: %s", e)
            errors["base"] = "timeout"
        except GatusApiClientSSLError as e:
            LOGGER.error("SSL error: %s", e)
            errors["base"] = "ssl"
        except GatusApiClientDNSError as e:
            LOGGER.error("DNS error: %s", e)
            errors["base"] = "dns"
        except GatusApiClientConnectionError as e:
            LOGGER.error("Connection error: %s", e)
            errors["base"] = "connection"
        except GatusApiClientError as e:
            LOGGER.error("Error: %s", e)
            errors["base"] = "unknown"
        return errors
