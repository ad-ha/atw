from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, API_PROVIDERS, DEFAULT_SCAN_INTERVAL


class StockCryptoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advanced Trading Wallet."""

    VERSION = 1

    def __init__(self):
        self.api_provider = None
        self.asset_type = None
        self.stock_data = None
        self.crypto_data = None
        self.preferred_currency = None

    async def async_step_user(self, user_input=None):
        """Handle the first step of the config flow, selecting the API provider."""
        errors = {}

        if user_input is not None:
            # Store the API provider and proceed to the asset type selection
            self.api_provider = user_input["api_provider"]
            # Store preferred currency in uppercase
            self.preferred_currency = user_input.get(
                "preferred_currency", "USD"
            ).upper()
            return await self.async_step_select_asset_type()

        # Show the form to select the API provider
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_provider", default=API_PROVIDERS[0]): vol.In(
                        API_PROVIDERS
                    ),
                    vol.Optional("preferred_currency", default="USD"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_select_asset_type(self, user_input=None):
        """Step to select whether to track stock or crypto."""
        errors = {}

        if user_input is not None:
            # Ensure that 'asset_type' is provided
            if "asset_type" in user_input:
                self.asset_type = user_input["asset_type"]
                if self.asset_type == "Stock":
                    return await self.async_step_select_stock()
                return await self.async_step_select_crypto()
            else:
                errors["base"] = "asset_type_missing"

        # Show the form to select the asset type
        return self.async_show_form(
            step_id="select_asset_type",
            data_schema=vol.Schema(
                {
                    vol.Required("asset_type", default="Stock"): vol.In(
                        ["Stock", "Crypto"]
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_select_stock(self, user_input=None):
        """Step for users to input stock data."""
        errors = {}

        data_schema = vol.Schema(
            {
                vol.Required("stocks_to_track"): str,
                vol.Optional("stock_amount_owned", default="0.0"): str,
                vol.Optional("stock_purchase_price", default="0.0"): str,
            }
        )

        if user_input is not None:
            try:
                stock_amount_owned = float(user_input.get("stock_amount_owned", "0.0"))
                stock_purchase_price = float(
                    user_input.get("stock_purchase_price", "0.0")
                )
            except ValueError:
                errors["base"] = "invalid_number"
                return self.async_show_form(
                    step_id="select_stock",
                    data_schema=data_schema,
                    errors=errors,
                )

            self.stock_data = {
                "stocks_to_track": user_input.get("stocks_to_track"),
                "stock_amount_owned": stock_amount_owned,
                "stock_purchase_price": stock_purchase_price,
            }
            return self.async_create_entry(
                title=f"Stock: {self.stock_data['stocks_to_track']}",
                data={
                    "api_provider": self.api_provider,
                    "preferred_currency": self.preferred_currency,
                    "stocks_to_track": self.stock_data["stocks_to_track"],
                    "stock_amount_owned": self.stock_data["stock_amount_owned"],
                    "stock_purchase_price": self.stock_data["stock_purchase_price"],
                    "crypto_to_track": "",
                    "crypto_display_symbol": "",
                    "crypto_amount_owned": 0.0,
                    "crypto_purchase_price": 0.0,
                },
            )

        return self.async_show_form(
            step_id="select_stock",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_select_crypto(self, user_input=None):
        """Step for users to input crypto data."""
        errors = {}

        data_schema = vol.Schema(
            {
                vol.Required("crypto_to_track"): str,
                vol.Optional("crypto_amount_owned", default="0.0"): str,
                vol.Optional("crypto_purchase_price", default="0.0"): str,
            }
        )

        if user_input is not None:
            try:
                crypto_symbol_input = user_input.get("crypto_to_track")
                crypto_symbol = crypto_symbol_input.lower().strip()
                crypto_display_symbol = crypto_symbol.upper()
                crypto_amount_owned = float(
                    user_input.get("crypto_amount_owned", "0.0")
                )
                crypto_purchase_price = float(
                    user_input.get("crypto_purchase_price", "0.0")
                )
            except ValueError:
                errors["base"] = "invalid_number"
                return self.async_show_form(
                    step_id="select_crypto",
                    data_schema=data_schema,
                    errors=errors,
                )

            self.crypto_data = {
                "crypto_to_track": crypto_symbol,
                "crypto_display_symbol": crypto_display_symbol,
                "crypto_amount_owned": crypto_amount_owned,
                "crypto_purchase_price": crypto_purchase_price,
            }
            return self.async_create_entry(
                title=f"Crypto: {self.crypto_data['crypto_to_track']}",
                data={
                    "api_provider": self.api_provider,
                    "preferred_currency": self.preferred_currency,
                    "crypto_to_track": self.crypto_data["crypto_to_track"],
                    "crypto_display_symbol": self.crypto_data["crypto_display_symbol"],
                    "crypto_amount_owned": self.crypto_data["crypto_amount_owned"],
                    "crypto_purchase_price": self.crypto_data["crypto_purchase_price"],
                    "stocks_to_track": "",
                    "stock_amount_owned": 0.0,
                    "stock_purchase_price": 0.0,
                },
            )

        return self.async_show_form(
            step_id="select_crypto",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return StockCryptoOptionsFlowHandler()


class StockCryptoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Advanced Trading Wallet."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "update_interval",
                    default=self.config_entry.options.get(
                        "update_interval", DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
