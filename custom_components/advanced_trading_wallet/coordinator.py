from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import ATWAPIClient
from homeassistant.core import HomeAssistant
from .const import DOMAIN, LOGGER, DEFAULT_SCAN_INTERVAL, DEFAULT_API_PROVIDER


class ATWCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching stock and crypto data."""

    def __init__(
        self,
        hass: HomeAssistant,
        preferred_currency="usd",
        update_interval=DEFAULT_SCAN_INTERVAL,
    ):
        """Initialize the coordinator."""
        self.hass = hass
        self.preferred_currency = preferred_currency
        self.stocks = {}
        self.crypto = {}
        self.transactions = {"stocks": {}, "crypto": {}}
        self.historical_data = {}
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )

    def update_symbols(self, data):
        """Update the list of symbols and their API providers based on current entries."""
        stocks = {}
        crypto = {}
        for entry_id, entry_data in data.items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            api_provider = entry_data.get("api_provider", DEFAULT_API_PROVIDER)
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if stock_symbol:
                    stocks[stock_symbol] = api_provider
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if crypto_symbol:
                    crypto[crypto_symbol] = api_provider
        self.stocks = stocks
        self.crypto = crypto
        LOGGER.debug(
            f"Updated symbols to track: Stocks={self.stocks}, Crypto={self.crypto}"
        )

    def add_entry_coordinator(self, entry_coordinator):
        """Add an entry-specific coordinator to be tracked globally."""
        self.entry_coordinators.append(entry_coordinator)

    async def _async_update_data(self):
        """Fetch data for all symbols."""
        data = {}
        # Fetch data for stocks grouped by API provider
        stocks_by_provider = {}
        for symbol, api_provider in self.stocks.items():
            stocks_by_provider.setdefault(api_provider, []).append(symbol)

        for api_provider, symbols in stocks_by_provider.items():
            api_client = ATWAPIClient(self.hass, api_provider)
            for symbol in symbols:
                try:
                    stock_data = await api_client.get_stock_data(symbol)
                    if stock_data:
                        data[symbol] = stock_data
                    else:
                        LOGGER.warning(f"No data received for stock: {symbol}")
                except Exception as e:
                    LOGGER.error(f"Error fetching data for stock {symbol}: {e}")

        # Similar for cryptocurrencies
        crypto_by_provider = {}
        for symbol, api_provider in self.crypto.items():
            crypto_by_provider.setdefault(api_provider, []).append(symbol)

        for api_provider, symbols in crypto_by_provider.items():
            api_client = ATWAPIClient(self.hass, api_provider)
            for symbol in symbols:
                try:
                    crypto_data = await api_client.get_crypto_data(symbol)
                    if crypto_data:
                        data[symbol] = crypto_data
                    else:
                        LOGGER.warning(f"No data received for crypto: {symbol}")
                except Exception as e:
                    LOGGER.error(f"Error fetching data for crypto {symbol}: {e}")

        return data

    async def fetch_historical_data(
        self, asset_symbol: str, asset_type: str, interval: str
    ):
        """Fetch historical data for stocks or crypto."""
        LOGGER.info(
            f"Fetching {asset_type} historical data for {asset_symbol} over {interval}"
        )

        # Determine the API provider for the asset
        if asset_type == "stock":
            api_provider = self.stocks.get(asset_symbol, DEFAULT_API_PROVIDER)
        elif asset_type == "crypto":
            api_provider = self.crypto.get(asset_symbol, DEFAULT_API_PROVIDER)
        else:
            LOGGER.error(f"Invalid asset type: {asset_type}")
            return

        api_client = ATWAPIClient(self.hass, api_provider)

        try:
            if asset_type == "stock":
                data = await api_client.get_stock_historical_data(
                    asset_symbol, interval
                )
            elif asset_type == "crypto":
                data = await api_client.get_crypto_historical_data(
                    asset_symbol, interval
                )

            if data:
                # Store the fetched data
                self.historical_data[asset_symbol] = data
                LOGGER.info(f"Historical data retrieved for {asset_symbol}: {data}")
            else:
                LOGGER.warning(
                    f"No data returned for {asset_symbol} at interval {interval}"
                )

        except Exception as e:
            LOGGER.error(f"Error fetching historical data for {asset_symbol}: {e}")

    def buy_stock(self, stock_symbol: str, amount: float, purchase_price: float):
        """Log a stock purchase and update per-entry data."""
        # Loop through entries to find the one that contains the stock
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            stocks_to_track = [
                s.strip() for s in entry_data.get("stocks_to_track", "").split(",")
            ]
            if stock_symbol in stocks_to_track:
                # Update the entry data
                old_amount = entry_data.get("stock_amount_owned", 0)
                old_purchase_price = entry_data.get("stock_purchase_price", 0)

                # Calculate new amount and purchase price
                total_amount = old_amount + amount
                total_value = (old_amount * old_purchase_price) + (
                    amount * purchase_price
                )
                new_purchase_price = total_value / total_amount if total_amount else 0

                entry_data["stock_amount_owned"] = total_amount
                entry_data["stock_purchase_price"] = new_purchase_price

                LOGGER.debug(
                    f"Updated entry {entry_id} for stock {stock_symbol}: amount={total_amount}, purchase_price={new_purchase_price}"
                )
                break
        else:
            LOGGER.warning(f"Stock symbol {stock_symbol} not found in any entry.")

    def sell_stock(self, stock_symbol: str, amount: float):
        """Log a stock sale and update per-entry data."""
        # Loop through entries to find the one that contains the stock
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            stocks_to_track = [
                s.strip() for s in entry_data.get("stocks_to_track", "").split(",")
            ]
            if stock_symbol in stocks_to_track:
                # Get current amount owned
                current_amount = entry_data.get("stock_amount_owned", 0)
                if amount > current_amount:
                    raise ValueError(
                        f"Cannot sell {amount} shares; only {current_amount} available."
                    )
                # Update the entry data
                new_amount = current_amount - amount
                entry_data["stock_amount_owned"] = new_amount
                LOGGER.debug(
                    f"Updated entry {entry_id} for stock {stock_symbol}: amount={new_amount}"
                )
                break
        else:
            LOGGER.warning(f"Stock symbol {stock_symbol} not found in any entry.")

    def buy_crypto(self, crypto_symbol: str, amount: float, purchase_price: float):
        """Log a cryptocurrency purchase and update per-entry data."""
        # Loop through entries to find the one that contains the crypto
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            crypto_to_track = [
                s.strip() for s in entry_data.get("crypto_to_track", "").split(",")
            ]
            if crypto_symbol in crypto_to_track:
                # Update the entry data
                old_amount = entry_data.get("crypto_amount_owned", 0)
                old_purchase_price = entry_data.get("crypto_purchase_price", 0)

                # Calculate new amount and purchase price
                total_amount = old_amount + amount
                total_value = (old_amount * old_purchase_price) + (
                    amount * purchase_price
                )
                new_purchase_price = total_value / total_amount if total_amount else 0

                entry_data["crypto_amount_owned"] = total_amount
                entry_data["crypto_purchase_price"] = new_purchase_price

                LOGGER.debug(
                    f"Updated entry {entry_id} for crypto {crypto_symbol}: amount={total_amount}, purchase_price={new_purchase_price}"
                )
                break
        else:
            LOGGER.warning(
                f"Cryptocurrency symbol {crypto_symbol} not found in any entry."
            )

    def sell_crypto(self, crypto_symbol: str, amount: float):
        """Log a cryptocurrency sale and update per-entry data."""
        # Loop through entries to find the one that contains the crypto
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            crypto_to_track = [
                s.strip() for s in entry_data.get("crypto_to_track", "").split(",")
            ]
            if crypto_symbol in crypto_to_track:
                # Get current amount owned
                current_amount = entry_data.get("crypto_amount_owned", 0)
                if amount > current_amount:
                    raise ValueError(
                        f"Cannot sell {amount} units; only {current_amount} available."
                    )
                # Update the entry data
                new_amount = current_amount - amount
                entry_data["crypto_amount_owned"] = new_amount
                LOGGER.debug(
                    f"Updated entry {entry_id} for crypto {crypto_symbol}: amount={new_amount}"
                )
                break
        else:
            LOGGER.warning(
                f"Cryptocurrency symbol {crypto_symbol} not found in any entry."
            )
