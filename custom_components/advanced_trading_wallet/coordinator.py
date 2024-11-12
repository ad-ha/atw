from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.storage import Store
from homeassistant.core import HomeAssistant
from .api import ATWAPIClient
from .const import DOMAIN, LOGGER, DEFAULT_SCAN_INTERVAL, DEFAULT_API_PROVIDER
from homeassistant.helpers.update_coordinator import UpdateFailed


class ATWDataStore:
    """Class to manage the storage of transaction data."""

    def __init__(self, hass: HomeAssistant, version: int = 1):
        self.store = Store(hass, version, f"{DOMAIN}_transaction_data")
        self._data = {}

    async def async_load(self):
        """Load the data from storage."""
        data = await self.store.async_load()
        if data is not None:
            self._data = data
        else:
            self._data = {}

    async def async_save(self):
        """Save the data to storage."""
        await self.store.async_save(self._data)

    def get_entry_data(self, entry_id):
        """Get data for a specific entry."""
        return self._data.get(entry_id, {})

    def set_entry_data(self, entry_id, data):
        """Set data for a specific entry."""
        self._data[entry_id] = data

    def update_entry_data(self, entry_id, key, value):
        """Update a specific key in entry data."""
        if entry_id not in self._data:
            self._data[entry_id] = {}
        self._data[entry_id][key] = value

    def get_all_data(self):
        """Get all stored data."""
        return self._data


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
        self.preferred_currency = preferred_currency.upper()
        self.stocks = {}
        self.crypto = {}
        self.transactions = {"stocks": {}, "crypto": {}}
        self.historical_data = {}
        self.data_store = ATWDataStore(hass)
        self.api_clients = {}
        LOGGER.debug(
            f"Initializing coordinator with update_interval={update_interval} minutes"
        )
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval),
        )

    async def async_set_update_interval(self, new_interval: timedelta):
        """Set a new update interval and reschedule updates."""
        LOGGER.debug(f"Setting new update interval: {new_interval}")
        self.update_interval = new_interval
        # Reschedule the update
        if self._unsub_refresh:
            self._unsub_refresh()
        self._schedule_refresh()

    async def async_close(self):
        """Close any open sessions or resources."""
        for client in self.api_clients.values():
            await client.close()
        self.api_clients.clear()

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

    async def _async_update_data(self):
        """Fetch data for all symbols."""
        data = {}
        try:
            # Fetch data for stocks grouped by API provider
            stocks_by_provider = {}
            for symbol, api_provider in self.stocks.items():
                stocks_by_provider.setdefault(api_provider, []).append(symbol)

            for api_provider, symbols in stocks_by_provider.items():
                if api_provider not in self.api_clients:
                    self.api_clients[api_provider] = ATWAPIClient(
                        self.hass, api_provider
                    )
                api_client = self.api_clients[api_provider]
                for symbol in symbols:
                    try:
                        stock_data = await api_client.get_stock_data(symbol)
                        if stock_data:
                            data[symbol] = stock_data
                        else:
                            LOGGER.warning(f"No data received for stock: {symbol}")
                            # Retain previous data if available
                            if self.data and symbol in self.data:
                                data[symbol] = self.data[symbol]
                    except Exception as e:
                        LOGGER.error(f"Error fetching data for stock {symbol}: {e}")
                        # Retain previous data if available
                        if self.data and symbol in self.data:
                            data[symbol] = self.data[symbol]

            # Fetch data for cryptocurrencies grouped by API provider
            crypto_by_provider = {}
            for symbol, api_provider in self.crypto.items():
                crypto_by_provider.setdefault(api_provider, []).append(symbol)

            for api_provider, symbols in crypto_by_provider.items():
                if api_provider not in self.api_clients:
                    self.api_clients[api_provider] = ATWAPIClient(
                        self.hass, api_provider
                    )
                api_client = self.api_clients[api_provider]
                for symbol in symbols:
                    try:
                        crypto_data = await api_client.get_crypto_data(symbol)
                        if crypto_data:
                            data[symbol] = crypto_data
                        else:
                            LOGGER.warning(f"No data received for crypto: {symbol}")
                            # Retain previous data if available
                            if self.data and symbol in self.data:
                                data[symbol] = self.data[symbol]
                    except Exception as e:
                        LOGGER.error(f"Error fetching data for crypto {symbol}: {e}")
                        # Retain previous data if available
                        if self.data and symbol in self.data:
                            data[symbol] = self.data[symbol]

            if not data:
                # If new data is empty, retain the previous data
                LOGGER.warning("No new data fetched, retaining previous data.")
                return self.data or {}
            else:
                # Update the stored data
                self.data = data
                return data
        except Exception as e:
            LOGGER.error(f"Error in _async_update_data: {e}")
            raise UpdateFailed(f"Error fetching data: {e}") from e

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

        if api_provider not in self.api_clients:
            self.api_clients[api_provider] = ATWAPIClient(self.hass, api_provider)
        api_client = self.api_clients[api_provider]

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
                LOGGER.info(f"Historical data retrieved for {asset_symbol}")
            else:
                LOGGER.warning(
                    f"No data returned for {asset_symbol} at interval {interval}"
                )

        except Exception as e:
            LOGGER.error(f"Error fetching historical data for {asset_symbol}: {e}")

    async def buy_stock(self, stock_symbol: str, amount: float, purchase_price: float):
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

                # Update the data store
                self.data_store.set_entry_data(entry_id, entry_data)
                await self.data_store.async_save()

                LOGGER.debug(
                    f"Updated entry {entry_id} for stock {stock_symbol}: amount={total_amount}, purchase_price={new_purchase_price}"
                )
                break
        else:
            LOGGER.warning(f"Stock symbol {stock_symbol} not found in any entry.")

    async def sell_stock(self, stock_symbol: str, amount: float):
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

                # Update the data store
                self.data_store.set_entry_data(entry_id, entry_data)
                await self.data_store.async_save()

                LOGGER.debug(
                    f"Updated entry {entry_id} for stock {stock_symbol}: amount={new_amount}"
                )
                break
        else:
            LOGGER.warning(f"Stock symbol {stock_symbol} not found in any entry.")

    async def buy_crypto(
        self, crypto_symbol: str, amount: float, purchase_price: float
    ):
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

                # Update the data store
                self.data_store.set_entry_data(entry_id, entry_data)
                await self.data_store.async_save()

                LOGGER.debug(
                    f"Updated entry {entry_id} for crypto {crypto_symbol}: amount={total_amount}, purchase_price={new_purchase_price}"
                )
                break
        else:
            LOGGER.warning(
                f"Cryptocurrency symbol {crypto_symbol} not found in any entry."
            )

    async def sell_crypto(self, crypto_symbol: str, amount: float):
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

                # Update the data store
                self.data_store.set_entry_data(entry_id, entry_data)
                await self.data_store.async_save()

                LOGGER.debug(
                    f"Updated entry {entry_id} for crypto {crypto_symbol}: amount={new_amount}"
                )
                break
            else:
                LOGGER.warning(
                    f"Cryptocurrency symbol {crypto_symbol} not found in any entry."
                )

    def calculate_total_investment(self):
        """Calculate the total amount invested in stocks and crypto."""
        total_investment = 0
        # Iterate over all entries
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            # Sum the total investment for stocks
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            stock_purchase_price = entry_data.get("stock_purchase_price", 0)
            total_investment += stock_amount_owned * stock_purchase_price

            # Sum the total investment for cryptos
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            crypto_purchase_price = entry_data.get("crypto_purchase_price", 0)
            total_investment += crypto_amount_owned * crypto_purchase_price

        return total_investment

    def calculate_total_value(self):
        """Calculate the total current value of stocks and crypto."""
        total_value = 0
        # Iterate over all entries
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            # Calculate stock values
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if not stock_symbol:
                    continue

                # Fetch stock price from coordinator data
                stock_data = self.data.get(stock_symbol)
                if stock_data and "quoteResponse" in stock_data:
                    stock_info = stock_data["quoteResponse"]["result"][0]
                    stock_price = stock_info.get("regularMarketPrice")
                    if stock_price is None:
                        # Handle pre/post market prices
                        market_state = stock_info.get("marketState")
                        if market_state in ["PRE", "PREPRE"]:
                            stock_price = stock_info.get("preMarketPrice")
                        elif market_state in ["POST", "POSTPOST"]:
                            stock_price = stock_info.get("postMarketPrice")
                    if stock_price is not None:
                        total_value += stock_price * stock_amount_owned

            # Calculate crypto values
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if not crypto_symbol:
                    continue

                # Fetch crypto price from coordinator data
                crypto_data = self.data.get(crypto_symbol)
                if crypto_data:
                    crypto_info = (
                        crypto_data[0] if isinstance(crypto_data, list) else crypto_data
                    )
                    crypto_price = crypto_info.get("current_price")
                    if crypto_price is not None:
                        total_value += crypto_price * crypto_amount_owned

        return total_value

    def calculate_percentage_change(self):
        """Calculate the percentage change of the portfolio."""
        total_investment = self.calculate_total_investment()
        total_value = self.calculate_total_value()
        if total_investment == 0:
            return 0
        return ((total_value - total_investment) / total_investment) * 100

    def calculate_total_variation(self):
        """Calculate the total variation (profit or loss) of the portfolio."""
        total_investment = self.calculate_total_investment()
        total_value = self.calculate_total_value()
        return total_value - total_investment
