import datetime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, LOGGER, DEFAULT_API_PROVIDER

# Configuration for the available stock sensors (Yahoo Finance)
SENSOR_TYPES_STOCK = [
    {
        "name": "Stock Price",
        "key": "regularMarketPrice",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Market Cap",
        "key": "marketCap",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Day High",
        "key": "regularMarketDayHigh",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Day Low",
        "key": "regularMarketDayLow",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Post Market Price",
        "key": "postMarketPrice",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Post Market Change",
        "key": "postMarketChange",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {"name": "Bid", "key": "bid", "device_class": SensorDeviceClass.MONETARY},
    {"name": "Ask", "key": "ask", "device_class": SensorDeviceClass.MONETARY},
    {
        "name": "52-Week High",
        "key": "fiftyTwoWeekHigh",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "52-Week Low",
        "key": "fiftyTwoWeekLow",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Dividend Rate",
        "key": "dividendRate",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Earnings Per Share (EPS)",
        "key": "epsTrailingTwelveMonths",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {"name": "Price to Earnings (PE) Ratio", "key": "trailingPE", "device_class": None},
    {"name": "Volume", "key": "regularMarketVolume", "device_class": None},
    {
        "name": "Average Volume (3M)",
        "key": "averageDailyVolume3Month",
        "device_class": None,
    },
    {
        "name": "Average Volume (10D)",
        "key": "averageDailyVolume10Day",
        "device_class": None,
        "unit": "Shares",
    },
    {"name": "Shares Outstanding", "key": "sharesOutstanding", "device_class": None},
    {
        "name": "Book Value",
        "key": "bookValue",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {"name": "Market State", "key": "marketState", "device_class": None},
    {"name": "Currency", "key": "currency", "device_class": None},
    {"name": "Display Name", "key": "displayName", "device_class": None},
    {"name": "Symbol", "key": "symbol", "device_class": None},
    {"name": "Short Name", "key": "shortName", "device_class": None},
    {
        "name": "Average Analyst Rating",
        "key": "averageAnalystRating",
        "device_class": None,
    },
    {"name": "Bid Size", "key": "bidSize", "device_class": None, "unit": "Shares"},
    {"name": "Ask Size", "key": "askSize", "device_class": None, "unit": "Shares"},
    {
        "name": "50-Day Average",
        "key": "fiftyDayAverage",
        "device_class": SensorDeviceClass.MONETARY,
        "unit": "USD",
    },
    {
        "name": "200-Day Average",
        "key": "twoHundredDayAverage",
        "device_class": SensorDeviceClass.MONETARY,
        "unit": "USD",
    },
    {
        "name": "Dividend Yield",
        "key": "dividendYield",
        "device_class": None,
        "unit": "%",
    },
    {
        "name": "Historical Stock Data",
        "key": "historical_stock_data",
        "device_class": None,
    },
]

# Configuration for available crypto sensors (CoinGecko)
SENSOR_TYPES_CRYPTO = [
    {
        "name": "Crypto Price",
        "key": "current_price",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Market Cap",
        "key": "market_cap",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {"name": "Market Cap Rank", "key": "market_cap_rank", "device_class": None},
    {"name": "24h Volume", "key": "total_volume", "device_class": None},
    {"name": "24h High", "key": "high_24h", "device_class": SensorDeviceClass.MONETARY},
    {"name": "24h Low", "key": "low_24h", "device_class": SensorDeviceClass.MONETARY},
    {
        "name": "ATH (All Time High)",
        "key": "ath",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "ATL (All Time Low)",
        "key": "atl",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {"name": "Circulating Supply", "key": "circulating_supply", "device_class": None},
    {
        "name": "Price Change (24h)",
        "key": "price_change_percentage_24h",
        "device_class": None,
    },
    {
        "name": "Fully Diluted Valuation",
        "key": "fully_diluted_valuation",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {
        "name": "Market Cap Change 24h",
        "key": "market_cap_change_24h",
        "device_class": SensorDeviceClass.MONETARY,
    },
    {"name": "Total Supply", "key": "total_supply", "device_class": None},
    {
        "name": "Historical Crypto Data",
        "key": "historical_crypto_data",
        "device_class": None,
    },
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]

    # Fetch per-entry data
    entry_data = hass.data[DOMAIN][entry.entry_id]

    asset_sensors = []

    # Create sensors for stocks
    for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
        stock_symbol = stock_symbol.strip()
        if not stock_symbol:
            continue
        api_provider = entry_data.get("api_provider", DEFAULT_API_PROVIDER)
        # Loop through each sensor type defined in SENSOR_TYPES_STOCK
        for sensor_type in SENSOR_TYPES_STOCK:
            asset_sensors.append(
                ATWSensor(
                    coordinator,
                    stock_symbol,
                    f"{stock_symbol} {sensor_type['name']}",
                    sensor_type["key"],
                    sensor_type.get("device_class"),
                    coordinator.preferred_currency,
                    api_provider,
                )
            )
        # Create stock-specific total_amount and purchase_price sensors
        asset_sensors.append(
            StockAmountSensor(coordinator, stock_symbol, entry_data, entry.entry_id)
        )
        asset_sensors.append(
            StockPurchasePriceSensor(
                coordinator, stock_symbol, entry_data, entry.entry_id
            )
        )

    # Create sensors for crypto
    for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
        crypto_symbol = crypto_symbol.strip()
        if not crypto_symbol:
            continue
        api_provider = entry_data.get("api_provider", DEFAULT_API_PROVIDER)
        # Loop through each sensor type defined in SENSOR_TYPES_CRYPTO
        for sensor_type in SENSOR_TYPES_CRYPTO:
            asset_sensors.append(
                ATWSensor(
                    coordinator,
                    crypto_symbol,
                    f"{crypto_symbol} {sensor_type['name']}",
                    sensor_type["key"],
                    sensor_type.get("device_class"),
                    coordinator.preferred_currency,
                    api_provider,
                )
            )
        # Create crypto-specific total_amount and purchase_price sensors
        asset_sensors.append(
            CryptoAmountSensor(coordinator, crypto_symbol, entry_data, entry.entry_id)
        )
        asset_sensors.append(
            CryptoPurchasePriceSensor(
                coordinator, crypto_symbol, entry_data, entry.entry_id
            )
        )

    # If "portfolio_sensors_created" is not already set, create portfolio sensors
    if not hass.data[DOMAIN].get("portfolio_sensors_created"):
        # Create Portfolio sensors as a separate entry
        portfolio_sensors = [
            TotalPortfolioValueSensor(hass, coordinator),
            TotalStocksValueSensor(hass, coordinator),
            TotalCryptoValueSensor(hass, coordinator),
            TotalInvestmentSensor(hass, coordinator),
            PercentageChangeSensor(hass, coordinator),
            TotalVariationSensor(hass, coordinator),
        ]
        async_add_entities(portfolio_sensors, True)
        hass.data[DOMAIN]["portfolio_sensors_created"] = True

    async_add_entities(asset_sensors, True)

    # Ensure the coordinator updates its data
    await coordinator.async_request_refresh()


class ATWSensor(SensorEntity, RestoreEntity):
    """Generic sensor for stock/crypto data."""

    def __init__(
        self,
        coordinator,
        symbol,
        name,
        data_key,
        device_class=None,
        preferred_currency=None,
        api_provider=None,
    ):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._name = name
        self._symbol = symbol
        self._data_key = data_key
        self._device_class = device_class
        self._preferred_currency = preferred_currency
        self._api_provider = api_provider
        self._state = None
        self._attr_device_class = device_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            LOGGER.warning(f"No data available for {self._symbol}")
            return None

        data = self.coordinator.data.get(self._symbol)
        if not data:
            LOGGER.warning(f"No data for symbol: {self._symbol}")
            return None

        if self._api_provider == "Yahoo Finance":
            data = data.get("quoteResponse", {}).get("result", [{}])[0]
        elif self._api_provider == "CoinGecko":
            data = data[0] if isinstance(data, list) else data
        else:
            LOGGER.error(f"Unknown API provider for {self._symbol}")
            return None

        raw_value = data.get(self._data_key)
        if isinstance(raw_value, (int, float)):
            return raw_value

        LOGGER.warning(f"Invalid data format for {self._symbol}: {raw_value}")
        return raw_value

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._symbol}_{self._data_key}"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including a formatted value."""
        raw_value = self.native_value

        if isinstance(raw_value, (int, float)):
            formatted_value = f"{raw_value:,.2f}"
        else:
            formatted_value = raw_value

        return {
            "formatted_value": formatted_value,
            "symbol": self._symbol,
            "api_provider": self._api_provider,
        }

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._device_class == SensorDeviceClass.MONETARY:
            return self._preferred_currency
        return None

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._symbol)},
            "name": f"Asset: {self._symbol}",
            "manufacturer": "Advanced Trading Wallet",
        }

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()


class StockAmountSensor(SensorEntity, RestoreEntity):
    """Sensor for stock total amount owned."""

    def __init__(self, coordinator, stock_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._stock_symbol = stock_symbol
        self._name = f"{stock_symbol} Total Amount"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        # Access per-entry amount owned
        self._state = self.entry_data.get("stock_amount_owned", 0)
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._stock_symbol}_{self.config_entry_id}_total_amount"

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class StockPurchasePriceSensor(SensorEntity, RestoreEntity):
    """Sensor for stock purchase price."""

    def __init__(self, coordinator, stock_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._stock_symbol = stock_symbol
        self._name = f"{stock_symbol} Purchase Price"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        self._state = self.entry_data.get("stock_purchase_price", 0)
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._stock_symbol}_{self.config_entry_id}_purchase_price"

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class CryptoAmountSensor(SensorEntity, RestoreEntity):
    """Sensor for crypto total amount owned."""

    def __init__(self, coordinator, crypto_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._crypto_symbol = crypto_symbol
        self._name = f"{crypto_symbol} Total Amount"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        self._state = self.entry_data.get("crypto_amount_owned", 0)
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._crypto_symbol}_{self.config_entry_id}_total_amount"

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class CryptoPurchasePriceSensor(SensorEntity, RestoreEntity):
    """Sensor for crypto purchase price."""

    def __init__(self, coordinator, crypto_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._crypto_symbol = crypto_symbol
        self._name = f"{crypto_symbol} Purchase Price"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        self._state = self.entry_data.get("crypto_purchase_price", 0)
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._crypto_symbol}_{self.config_entry_id}_purchase_price"

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class TotalPortfolioValueSensor(SensorEntity, RestoreEntity):
    """Sensor to track the total value of stocks and crypto in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self._name = "Total Portfolio Value"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        total_value = 0

        # Fetch per-entry data from hass.data
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                LOGGER.warning(
                    f"Unexpected data type for entry_id '{entry_id}': {type(entry_data)}"
                )
                continue
            # Calculate stock values
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if not stock_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{stock_symbol.replace('-', '_')}_stock_price"

                stock_price_sensor = self.hass.states.get(entity_id)

                if stock_price_sensor and stock_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        stock_price = float(stock_price_sensor.state)
                        total_value += stock_price * stock_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {stock_symbol}: {e}"
                        )

            # Calculate crypto values
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if not crypto_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{crypto_symbol.replace('-', '_')}_crypto_price"

                crypto_price_sensor = self.hass.states.get(entity_id)

                if crypto_price_sensor and crypto_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        crypto_price = float(crypto_price_sensor.state)
                        total_value += crypto_price * crypto_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {crypto_symbol}: {e}"
                        )

        self._state = total_value
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return "global_portfolio_total_value"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class TotalStocksValueSensor(SensorEntity, RestoreEntity):
    """Sensor to track the total value of stocks in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self._name = "Total Stocks Value"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        total_stocks_value = 0

        # Fetch per-entry data from hass.data
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                LOGGER.warning(
                    f"Unexpected data type for entry_id '{entry_id}': {type(entry_data)}"
                )
                continue
            # Calculate stock values
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if not stock_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{stock_symbol.replace('-', '_')}_stock_price"

                stock_price_sensor = self.hass.states.get(entity_id)

                if stock_price_sensor and stock_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        stock_price = float(stock_price_sensor.state)
                        total_stocks_value += stock_price * stock_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {stock_symbol}: {e}"
                        )

        self._state = total_stocks_value
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return "global_portfolio_total_stocks_value"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class TotalCryptoValueSensor(SensorEntity, RestoreEntity):
    """Sensor to track the total value of crypto in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self._name = "Total Crypto Value"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        total_crypto_value = 0

        # Fetch per-entry data from hass.data
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                LOGGER.warning(
                    f"Unexpected data type for entry_id '{entry_id}': {type(entry_data)}"
                )
                continue
            # Calculate crypto values
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if not crypto_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{crypto_symbol.replace('-', '_')}_crypto_price"

                crypto_price_sensor = self.hass.states.get(entity_id)

                if crypto_price_sensor and crypto_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        crypto_price = float(crypto_price_sensor.state)
                        total_crypto_value += crypto_price * crypto_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {crypto_symbol}: {e}"
                        )

        self._state = total_crypto_value
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return "global_portfolio_total_crypto_value"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class TotalInvestmentSensor(SensorEntity, RestoreEntity):
    """Sensor to track the total investment value (stocks and crypto) in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self._name = "Total Investment"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        total_investment = 0

        # Iterate over all entries
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                LOGGER.warning(
                    f"Unexpected data type for entry_id '{entry_id}': {type(entry_data)}"
                )
                continue
            # Sum the total investment for stocks
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            stock_purchase_price = entry_data.get("stock_purchase_price", 0)
            total_investment += stock_amount_owned * stock_purchase_price

            # Sum the total investment for cryptos
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            crypto_purchase_price = entry_data.get("crypto_purchase_price", 0)
            total_investment += crypto_amount_owned * crypto_purchase_price

        self._state = total_investment
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return "global_portfolio_total_investment"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class PercentageChangeSensor(SensorEntity, RestoreEntity):
    """Sensor to track the percentage change in the portfolio value."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self._name = "Percentage Change"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        total_investment = 0
        total_value = 0

        # Iterate over all entries
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                LOGGER.warning(
                    f"Unexpected data type for entry_id '{entry_id}': {type(entry_data)}"
                )
                continue
            # Sum the total investment for stocks
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            stock_purchase_price = entry_data.get("stock_purchase_price", 0)
            total_investment += stock_amount_owned * stock_purchase_price

            # Sum the total investment for cryptos
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            crypto_purchase_price = entry_data.get("crypto_purchase_price", 0)
            total_investment += crypto_amount_owned * crypto_purchase_price

            # Calculate stock values
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if not stock_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{stock_symbol.replace('-', '_')}_stock_price"

                stock_price_sensor = self.hass.states.get(entity_id)

                if stock_price_sensor and stock_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        stock_price = float(stock_price_sensor.state)
                        total_value += stock_price * stock_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {stock_symbol}: {e}"
                        )

            # Calculate crypto values
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if not crypto_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{crypto_symbol.replace('-', '_')}_crypto_price"

                crypto_price_sensor = self.hass.states.get(entity_id)

                if crypto_price_sensor and crypto_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        crypto_price = float(crypto_price_sensor.state)
                        total_value += crypto_price * crypto_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {crypto_symbol}: {e}"
                        )

        if total_investment == 0:
            self._state = 0  # Avoid division by zero
        else:
            self._state = ((total_value - total_investment) / total_investment) * 100

        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return "global_portfolio_percentage_change"

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class TotalVariationSensor(SensorEntity, RestoreEntity):
    """Sensor to track the total variation (increase/decrease) in portfolio value."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        self.coordinator = coordinator
        self._name = "Total Variation"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state."""
        total_investment = 0
        total_value = 0

        # Iterate over all entries
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                LOGGER.warning(
                    f"Unexpected data type for entry_id '{entry_id}': {type(entry_data)}"
                )
                continue
            # Sum the total investment for stocks
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            stock_purchase_price = entry_data.get("stock_purchase_price", 0)
            total_investment += stock_amount_owned * stock_purchase_price

            # Sum the total investment for cryptos
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            crypto_purchase_price = entry_data.get("crypto_purchase_price", 0)
            total_investment += crypto_amount_owned * crypto_purchase_price

            # Calculate stock values
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if not stock_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{stock_symbol.replace('-', '_')}_stock_price"

                stock_price_sensor = self.hass.states.get(entity_id)

                if stock_price_sensor and stock_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        stock_price = float(stock_price_sensor.state)
                        total_value += stock_price * stock_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {stock_symbol}: {e}"
                        )

            # Calculate crypto values
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if not crypto_symbol:
                    continue

                # Generate the correct entity ID
                entity_id = f"sensor.{crypto_symbol.replace('-', '_')}_crypto_price"

                crypto_price_sensor = self.hass.states.get(entity_id)

                if crypto_price_sensor and crypto_price_sensor.state not in (
                    None,
                    "unknown",
                ):
                    try:
                        crypto_price = float(crypto_price_sensor.state)
                        total_value += crypto_price * crypto_amount_owned
                    except ValueError as e:
                        LOGGER.warning(
                            f"Error converting values for {crypto_symbol}: {e}"
                        )

        self._state = total_value - total_investment
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return "global_portfolio_total_variation"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }
