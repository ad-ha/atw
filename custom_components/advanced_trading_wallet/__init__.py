from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
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

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Advanced Trading Wallet from a config entry."""
    LOGGER.debug(f"Setting up entry for {config_entry.entry_id}")

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        LOGGER.debug("Initialized domain data")

    # If global coordinator doesn't exist, create it
    if "coordinator" not in hass.data[DOMAIN]:
        update_interval = config_entry.options.get(
            "update_interval", DEFAULT_SCAN_INTERVAL
        )
        coordinator = ATWCoordinator(
            hass,
            preferred_currency=config_entry.data.get("preferred_currency", "USD"),
            update_interval=update_interval,
        )
        hass.data[DOMAIN]["coordinator"] = coordinator
        LOGGER.debug("Created global coordinator")
        await coordinator.data_store.async_load()
        await coordinator.async_config_entry_first_refresh()
    else:
        coordinator = hass.data[DOMAIN]["coordinator"]
        # Update coordinator's update interval if changed
        update_interval = config_entry.options.get(
            "update_interval", DEFAULT_SCAN_INTERVAL
        )
        await coordinator.async_set_update_interval(timedelta(minutes=update_interval))

    # Store per-entry data
    entry_id = config_entry.entry_id
    entry_data = {
        "api_provider": config_entry.data.get("api_provider", DEFAULT_API_PROVIDER),
        "preferred_currency": config_entry.data.get(
            "preferred_currency", "USD"
        ).upper(),
        "stocks_to_track": config_entry.data.get("stocks_to_track", ""),
        "crypto_to_track": config_entry.data.get("crypto_to_track", ""),
        "stock_amount_owned": config_entry.data.get("stock_amount_owned", 0),
        "stock_purchase_price": config_entry.data.get("stock_purchase_price", 0),
        "crypto_amount_owned": config_entry.data.get("crypto_amount_owned", 0),
        "crypto_purchase_price": config_entry.data.get("crypto_purchase_price", 0),
    }

    # Update entry_data with stored data if available
    stored_entry_data = coordinator.data_store.get_entry_data(entry_id)
    if stored_entry_data:
        entry_data.update(stored_entry_data)

    hass.data[DOMAIN][entry_id] = entry_data

    # Update coordinator's list of symbols and API providers
    coordinator.update_symbols(hass.data[DOMAIN])

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Pass the coordinator when setting up services
    await async_setup_services(hass, coordinator)

    # Add update listener for options
    config_entry.async_on_unload(
        config_entry.add_update_listener(async_options_updated)
    )

    return True


async def async_options_updated(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    # Retrieve the coordinator
    coordinator = hass.data[DOMAIN]["coordinator"]

    # Get the new update_interval from options
    update_interval = config_entry.options.get("update_interval", DEFAULT_SCAN_INTERVAL)
    new_interval = timedelta(minutes=update_interval)
    LOGGER.debug(f"Options updated: new update_interval={new_interval}")

    # Update the coordinator's update_interval
    await coordinator.async_set_update_interval(new_interval)


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
            await coordinator.async_close()
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
