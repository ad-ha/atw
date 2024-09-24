from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, API_PROVIDERS


class StockCryptoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advanced Trading Wallet."""

    VERSION = 1

    def __init__(self):
        self.api_provider = None
        self.asset_type = None
        self.stock_data = None
        self.crypto_data = None

    async def async_step_user(self, user_input=None):
        """Handle the first step of the config flow, selecting the API provider."""
        errors = {}

        if user_input is not None:
            # Store the API provider and proceed to the asset type selection
            self.api_provider = user_input["api_provider"]
            return await self.async_step_select_asset_type()

        # Show the form to select the API provider
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_provider", default=API_PROVIDERS[0]): vol.In(
                        API_PROVIDERS
                    ),
                    vol.Optional("preferred_currency"): str,
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
        if user_input is not None:
            self.stock_data = {
                "stocks_to_track": user_input.get("stocks_to_track"),
                "stock_amount_owned": user_input.get("stock_amount_owned"),
                "stock_purchase_price": user_input.get("stock_purchase_price"),
            }
            return await self.async_create_entry(user_input)

        return self.async_show_form(
            step_id="select_stock",
            data_schema=vol.Schema(
                {
                    vol.Required("stocks_to_track"): str,
                    vol.Optional("stock_amount_owned"): vol.Coerce(float),
                    vol.Optional("stock_purchase_price"): vol.Coerce(float),
                }
            ),
        )

    async def async_step_select_crypto(self, user_input=None):
        """Step for users to input crypto data."""
        if user_input is not None:
            self.crypto_data = {
                "crypto_to_track": user_input.get("crypto_to_track"),
                "crypto_amount_owned": user_input.get("crypto_amount_owned"),
                "crypto_purchase_price": user_input.get("crypto_purchase_price"),
            }
            return await self.async_create_entry(user_input)

        return self.async_show_form(
            step_id="select_crypto",
            data_schema=vol.Schema(
                {
                    vol.Required("crypto_to_track"): str,
                    vol.Optional("crypto_amount_owned"): vol.Coerce(float),
                    vol.Optional("crypto_purchase_price"): vol.Coerce(float),
                }
            ),
        )

    async def async_create_entry(self, user_input=None):
        """Create the final configuration entry."""
        title = ""
        if self.asset_type == "Stock":
            title = f"Stock: {self.stock_data.get('stocks_to_track', 'Unknown')}"
        elif self.asset_type == "Crypto":
            title = f"Crypto: {self.crypto_data.get('crypto_to_track', 'Unknown')}"

        return super().async_create_entry(
            title=title,
            data={
                "api_provider": self.api_provider,
                "preferred_currency": user_input.get("preferred_currency", "usd"),
                "stocks_to_track": self.stock_data.get("stocks_to_track", "")
                if self.stock_data
                else "",
                "crypto_to_track": self.crypto_data.get("crypto_to_track", "")
                if self.crypto_data
                else "",
                "stock_amount_owned": self.stock_data.get("stock_amount_owned", 0)
                if self.stock_data
                else 0,
                "stock_purchase_price": self.stock_data.get("stock_purchase_price", 0)
                if self.stock_data
                else 0,
                "crypto_amount_owned": self.crypto_data.get("crypto_amount_owned", 0)
                if self.crypto_data
                else 0,
                "crypto_purchase_price": self.crypto_data.get(
                    "crypto_purchase_price", 0
                )
                if self.crypto_data
                else 0,
            },
        )
