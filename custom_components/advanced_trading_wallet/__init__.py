from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import Platform
from .const import (
    DOMAIN,
    LOGGER,
    PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_API_PROVIDER,
)
from .coordinator import ATWCoordinator
from .services import async_setup_services, async_unload_services


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Advanced Trading Wallet from a config entry."""
    LOGGER.debug(f"Setting up entry for {config_entry.entry_id}")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        LOGGER.debug("Initialized domain data")

    # If global coordinator doesn't exist, create it
    if "coordinator" not in hass.data[DOMAIN]:
        coordinator = ATWCoordinator(
            hass,
            preferred_currency=config_entry.data.get("preferred_currency", "usd"),
            update_interval=config_entry.data.get(
                "update_interval", DEFAULT_SCAN_INTERVAL
            ),
        )
        hass.data[DOMAIN]["coordinator"] = coordinator
        LOGGER.debug("Created global coordinator")
        await coordinator.async_config_entry_first_refresh()
    else:
        coordinator = hass.data[DOMAIN]["coordinator"]

    # Store per-entry data
    hass.data[DOMAIN][config_entry.entry_id] = {
        "api_provider": config_entry.data.get("api_provider", DEFAULT_API_PROVIDER),
        "stocks_to_track": config_entry.data.get("stocks_to_track", ""),
        "crypto_to_track": config_entry.data.get("crypto_to_track", ""),
        "stock_amount_owned": config_entry.data.get("stock_amount_owned", 0),
        "stock_purchase_price": config_entry.data.get("stock_purchase_price", 0),
        "crypto_amount_owned": config_entry.data.get("crypto_amount_owned", 0),
        "crypto_purchase_price": config_entry.data.get("crypto_purchase_price", 0),
    }

    # Update coordinator's list of symbols and API providers
    coordinator.update_symbols(hass.data[DOMAIN])

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Pass the coordinator when setting up services
    await async_setup_services(hass, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
        # Update coordinator's list of symbols
        coordinator = hass.data[DOMAIN]["coordinator"]
        coordinator.update_symbols(hass.data[DOMAIN])

        # If no other entries remain, remove the coordinator and services
        if len(hass.data[DOMAIN]) == 1:  # Only 'coordinator' remains
            hass.data[DOMAIN].pop("coordinator")
            await async_unload_services(hass)

    return unload_ok


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Advanced Trading Wallet integration."""
    LOGGER.debug("Setting up Advanced Trading Wallet")
    return True


async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    LOGGER.debug(f"Removing config entry {config_entry.entry_id}")
    if config_entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    # Ensure global coordinator removal if no entries are left
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
