import aiohttp
from homeassistant.core import HomeAssistant, ServiceCall
from .const import (
    DOMAIN,
    LOGGER,
    DEFAULT_HISTORICAL_INTERVAL,
)
from .coordinator import ATWCoordinator


async def async_setup_services(
    hass: HomeAssistant, coordinator: ATWCoordinator
) -> None:
    """Set up Advanced Trading Wallet services."""

    async def handle_refresh_data(service_call: ServiceCall) -> None:
        """Handle the refresh data service."""
        await coordinator.async_request_refresh()

    async def handle_get_historical_data(service_call: ServiceCall) -> None:
        """Handle the get historical data service."""
        try:
            asset_symbol = service_call.data["asset_symbol"]
            asset_type = service_call.data["asset_type"]
            interval = service_call.data.get("interval", DEFAULT_HISTORICAL_INTERVAL)

            await coordinator.fetch_historical_data(asset_symbol, asset_type, interval)
            LOGGER.info(
                f"Historical data for {asset_symbol} over {interval} fetched successfully."
            )

        except KeyError as key_err:
            LOGGER.error(f"Missing required service data: {key_err}")
        except aiohttp.ClientError as client_err:
            LOGGER.error(
                f"Network error fetching data for {asset_symbol}: {client_err}"
            )
        except Exception as e:
            LOGGER.error(f"Unexpected error occurred: {e}")

    async def handle_buy_stock(service_call: ServiceCall) -> None:
        """Handle the buy_stock service."""
        stock_symbol = service_call.data.get("stock_symbol")
        amount = float(service_call.data.get("amount"))
        purchase_price = float(service_call.data.get("purchase_price"))

        LOGGER.debug(
            f"Service call to buy stock: {stock_symbol}, amount: {amount}, purchase price: {purchase_price}"
        )

        try:
            await coordinator.buy_stock(stock_symbol, amount, purchase_price)
            await coordinator.async_request_refresh()
        except Exception as e:
            LOGGER.error(f"Error in buy_stock service: {e}")

    async def handle_sell_stock(service_call: ServiceCall):
        """Handle a stock sale."""
        stock_symbol = service_call.data.get("stock_symbol")
        amount = float(service_call.data.get("amount"))

        LOGGER.debug(f"Service call to sell stock: {stock_symbol}, amount: {amount}")

        try:
            await coordinator.sell_stock(stock_symbol, amount)
            await coordinator.async_request_refresh()
        except ValueError as e:
            LOGGER.error(f"Error in sell_stock service: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected error in sell_stock service: {e}")

    async def handle_buy_crypto(service_call: ServiceCall):
        """Handle a cryptocurrency purchase."""
        crypto_symbol = service_call.data.get("crypto_symbol")
        amount = float(service_call.data.get("amount"))
        purchase_price = float(service_call.data.get("purchase_price"))

        LOGGER.debug(
            f"Service call to buy crypto: {crypto_symbol}, amount: {amount}, purchase price: {purchase_price}"
        )

        try:
            await coordinator.buy_crypto(crypto_symbol, amount, purchase_price)
            await coordinator.async_request_refresh()
        except Exception as e:
            LOGGER.error(f"Error in buy_crypto service: {e}")

    async def handle_sell_crypto(service_call: ServiceCall):
        """Handle a cryptocurrency sale."""
        crypto_symbol = service_call.data.get("crypto_symbol")
        amount = float(service_call.data.get("amount"))

        LOGGER.debug(f"Service call to sell crypto: {crypto_symbol}, amount: {amount}")

        try:
            await coordinator.sell_crypto(crypto_symbol, amount)
            await coordinator.async_request_refresh()
        except ValueError as e:
            LOGGER.error(f"Error in sell_crypto service: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected error in sell_crypto service: {e}")

    # Register services
    hass.services.async_register(DOMAIN, "refresh_data", handle_refresh_data)
    hass.services.async_register(
        DOMAIN, "get_historical_data", handle_get_historical_data
    )
    # Register the services for stocks
    hass.services.async_register(DOMAIN, "buy_stock", handle_buy_stock)
    hass.services.async_register(DOMAIN, "sell_stock", handle_sell_stock)

    # Register the services for cryptocurrencies
    hass.services.async_register(DOMAIN, "buy_crypto", handle_buy_crypto)
    hass.services.async_register(DOMAIN, "sell_crypto", handle_sell_crypto)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload the Advanced Trading Wallet services."""
    hass.services.async_remove(DOMAIN, "refresh_data")
    hass.services.async_remove(DOMAIN, "get_historical_data")
    hass.services.async_remove(DOMAIN, "buy_stock")
    hass.services.async_remove(DOMAIN, "sell_stock")
    hass.services.async_remove(DOMAIN, "buy_crypto")
    hass.services.async_remove(DOMAIN, "sell_crypto")
