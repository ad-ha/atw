import locale
import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (
    DOMAIN,
    LOGGER,
    DEFAULT_API_PROVIDER,
    SENSOR_TYPES_STOCK,
    SENSOR_TYPES_CRYPTO,
)
from .coordinator import ATWCoordinator

# Set the locale to the system's default
locale.setlocale(locale.LC_ALL, "")


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
                    sensor_type["name"],
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
                    sensor_type["name"],
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


class ATWSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for stock/crypto data."""

    def __init__(
        self,
        coordinator,
        symbol,
        sensor_name,
        data_key,
        device_class=None,
        preferred_currency=None,
        api_provider=None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = f"{symbol.upper()} {sensor_name}"
        self._symbol = symbol
        self._sensor_name = sensor_name
        self._data_key = data_key
        self._device_class = device_class
        self._preferred_currency = preferred_currency.upper()
        self._api_provider = api_provider
        self._state = None
        self._attr_device_class = device_class
        self._last_updated = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self._symbol)
        if not data:
            LOGGER.warning(
                f"No data for symbol: {self._symbol}, using last known value."
            )
            return self._state  # Return last known state

        if self._api_provider == "Yahoo Finance":
            data = data.get("quoteResponse", {}).get("result", [{}])[0]
        elif self._api_provider == "CoinGecko":
            data = data[0] if isinstance(data, list) else data
        else:
            LOGGER.error(f"Unknown API provider for {self._symbol}")
            return self._state  # Return last known state

        if self._data_key == "regularMarketPrice":
            # Handle stock price based on market state
            raw_value = self.get_stock_price(data)
        else:
            raw_value = data.get(self._data_key)

        if raw_value is not None:
            self._state = raw_value
            self._last_updated = dt_util.utcnow()
        else:
            LOGGER.warning(f"No data for {self._symbol}: {self._data_key}")
            # Do not update self._state if data is None

        return self._state

    def get_stock_price(self, data):
        market_state = data.get("marketState")
        if market_state in ["PRE", "PREPRE"] and "preMarketPrice" in data:
            return data["preMarketPrice"]
        elif market_state in ["POST", "POSTPOST"] and "postMarketPrice" in data:
            return data["postMarketPrice"]
        else:
            return data.get("regularMarketPrice")

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
            # Determine the number of decimal places based on asset type and sensor type
            if "amount" in self._name.lower():
                decimal_places = 4
            elif "crypto" in self._name.lower():
                decimal_places = 8
            elif "percentage" in self._name.lower():
                decimal_places = 2
            else:
                decimal_places = 2
            formatted_value = locale.format_string(
                f"%.{decimal_places}f", raw_value, grouping=True
            )
        else:
            formatted_value = raw_value

        return {
            "formatted_value": formatted_value,
            "symbol": self._symbol.upper(),
            "api_provider": self._api_provider,
            "last_updated": self._last_updated,
        }

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._device_class == SensorDeviceClass.MONETARY:
            return self._preferred_currency
        elif "percentage" in self._name.lower():
            return "%"
        else:
            return None

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._symbol)},
            "name": f"Asset: {self._symbol.upper()}",
            "manufacturer": "Advanced Trading Wallet",
        }

    @property
    def available(self):
        """Return True if sensor data is available."""
        data = self.coordinator.data.get(self._symbol)
        if not data:
            return False
        if self._api_provider == "Yahoo Finance":
            data = data.get("quoteResponse", {}).get("result", [{}])[0]
        elif self._api_provider == "CoinGecko":
            data = data[0] if isinstance(data, list) else data
        return self._data_key in data or self._data_key == "regularMarketPrice"


class StockAmountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for stock total amount owned."""

    def __init__(self, coordinator, stock_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stock_symbol = stock_symbol
        self._name = f"{stock_symbol.upper()} Total Amount"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        # Access per-entry amount owned
        self._state = self.entry_data.get("stock_amount_owned", 0)
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._stock_symbol}_{self.config_entry_id}_total_amount"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        raw_value = self.native_value
        formatted_value = locale.format_string("%.4f", raw_value, grouping=True)
        return {
            "formatted_value": formatted_value,
            "symbol": self._stock_symbol.upper(),
        }

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class StockPurchasePriceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for stock purchase price."""

    def __init__(self, coordinator, stock_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stock_symbol = stock_symbol
        self._name = f"{stock_symbol.upper()} Purchase Price"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.entry_data.get("stock_purchase_price", 0)
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._stock_symbol}_{self.config_entry_id}_purchase_price"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        raw_value = self.native_value
        formatted_value = locale.format_string("%.2f", raw_value, grouping=True)
        return {
            "formatted_value": formatted_value,
            "symbol": self._stock_symbol.upper(),
        }

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class CryptoAmountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for crypto total amount owned."""

    def __init__(self, coordinator, crypto_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._crypto_symbol = crypto_symbol
        self._name = f"{crypto_symbol.upper()} Total Amount"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.entry_data.get("crypto_amount_owned", 0)
        return self._state

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._crypto_symbol}_{self.config_entry_id}_total_amount"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        raw_value = self.native_value
        formatted_value = locale.format_string("%.4f", raw_value, grouping=True)
        return {
            "formatted_value": formatted_value,
            "symbol": self._crypto_symbol.upper(),
        }

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class CryptoPurchasePriceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for crypto purchase price."""

    def __init__(self, coordinator, crypto_symbol, entry_data, config_entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._crypto_symbol = crypto_symbol
        self._name = f"{crypto_symbol.upper()} Purchase Price"
        self._state = None
        self.entry_data = entry_data
        self.config_entry_id = config_entry_id
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.entry_data.get("crypto_purchase_price", 0)
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._crypto_symbol}_{self.config_entry_id}_purchase_price"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        raw_value = self.native_value
        formatted_value = locale.format_string("%.8f", raw_value, grouping=True)
        return {
            "formatted_value": formatted_value,
            "symbol": self._crypto_symbol.upper(),
        }

    @property
    def device_info(self):
        """Return the device info for the Portfolio."""
        return {
            "identifiers": {(DOMAIN, "global_portfolio")},
            "name": "Portfolio",
            "manufacturer": "Advanced Trading Wallet",
        }


class TotalPortfolioValueSensor(CoordinatorEntity, SensorEntity):
    """Sensor to track the total value of stocks and crypto in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator)
        self._name = "Total Portfolio Value"
        self._state = None
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.coordinator.calculate_total_value()
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        formatted_value = locale.format_string("%.2f", self._state, grouping=True)
        return {
            "formatted_value": formatted_value,
        }

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


class TotalStocksValueSensor(CoordinatorEntity, SensorEntity):
    """Sensor to track the total value of stocks in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator)
        self._name = "Total Stocks Value"
        self._state = None
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        total_stocks_value = 0
        # Iterate over all entries to calculate stock values
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            stock_amount_owned = entry_data.get("stock_amount_owned", 0)
            for stock_symbol in entry_data.get("stocks_to_track", "").split(","):
                stock_symbol = stock_symbol.strip()
                if not stock_symbol:
                    continue
                # Fetch stock price from coordinator data
                stock_data = self.coordinator.data.get(stock_symbol)
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
                        total_stocks_value += stock_price * stock_amount_owned
        self._state = total_stocks_value
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        formatted_value = locale.format_string("%.2f", self._state, grouping=True)
        return {
            "formatted_value": formatted_value,
        }

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


class TotalCryptoValueSensor(CoordinatorEntity, SensorEntity):
    """Sensor to track the total value of crypto in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator)
        self._name = "Total Crypto Value"
        self._state = None
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        total_crypto_value = 0
        # Iterate over all entries to calculate crypto values
        for entry_id, entry_data in self.hass.data[DOMAIN].items():
            if entry_id in ("coordinator", "portfolio_sensors_created"):
                continue
            if not isinstance(entry_data, dict):
                continue
            crypto_amount_owned = entry_data.get("crypto_amount_owned", 0)
            for crypto_symbol in entry_data.get("crypto_to_track", "").split(","):
                crypto_symbol = crypto_symbol.strip()
                if not crypto_symbol:
                    continue
                # Fetch crypto price from coordinator data
                crypto_data = self.coordinator.data.get(crypto_symbol)
                if crypto_data:
                    crypto_info = (
                        crypto_data[0] if isinstance(crypto_data, list) else crypto_data
                    )
                    crypto_price = crypto_info.get("current_price")
                    if crypto_price is not None:
                        total_crypto_value += crypto_price * crypto_amount_owned
        self._state = total_crypto_value
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        formatted_value = locale.format_string("%.2f", self._state, grouping=True)
        return {
            "formatted_value": formatted_value,
        }

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


class TotalInvestmentSensor(CoordinatorEntity, SensorEntity):
    """Sensor to track the total investment value (stocks and crypto) in the portfolio."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator)
        self._name = "Total Investment"
        self._state = None
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.coordinator.calculate_total_investment()
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        formatted_value = locale.format_string("%.2f", self._state, grouping=True)
        return {
            "formatted_value": formatted_value,
        }

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


class PercentageChangeSensor(CoordinatorEntity, SensorEntity):
    """Sensor to track the percentage change in the portfolio value."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator)
        self._name = "Percentage Change"
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.coordinator.calculate_percentage_change()
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        formatted_value = locale.format_string("%.2f", self._state, grouping=True)
        return {
            "formatted_value": formatted_value,
        }

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


class TotalVariationSensor(CoordinatorEntity, SensorEntity):
    """Sensor to track the total variation (increase/decrease) in portfolio value."""

    def __init__(self, hass, coordinator):
        """Initialize the sensor."""
        self.hass = hass
        super().__init__(coordinator)
        self._name = "Total Variation"
        self._state = None
        self._preferred_currency = coordinator.preferred_currency

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the current state."""
        self._state = self.coordinator.calculate_total_variation()
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._preferred_currency

    @property
    def extra_state_attributes(self):
        """Return extra state attributes, including formatted value."""
        formatted_value = locale.format_string("%.2f", self._state, grouping=True)
        return {
            "formatted_value": formatted_value,
        }

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
