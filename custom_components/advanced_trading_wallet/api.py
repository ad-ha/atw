import aiohttp
import asyncio
from homeassistant.core import HomeAssistant
from .const import (
    YAHOO_FINANCE_BASE_URL,
    YAHOO_FINANCE_HISTORICAL_URL,
    COINGECKO_BASE_URL,
    YAHOO_HEADERS,
    GET_CRUMB_URL,
    LOGGER,
    DEFAULT_RETRY_AFTER,
)


class ATWAPIClient:
    """API client to fetch stock and crypto data."""

    def __init__(self, hass: HomeAssistant, api_provider: str):
        """Initialize the API client."""
        self.hass = hass
        self.api_provider = api_provider
        self.crumb = None
        self.cookies = None
        self.session = aiohttp.ClientSession()

    async def get_stock_data(self, stock_symbol: str):
        """Fetch stock data asynchronously."""
        if self.api_provider == "Yahoo Finance":
            return await self._fetch_yahoo_stock(stock_symbol)
        return None

    async def get_crypto_data(self, crypto_symbol: str, currency: str = "usd"):
        """Fetch crypto data asynchronously."""
        if self.api_provider == "CoinGecko":
            return await self._fetch_coingecko_crypto(crypto_symbol, currency)
        return None

    async def _fetch_yahoo_crumb(self):
        """Fetch crumb and cookies from Yahoo Finance."""
        if self.crumb:
            LOGGER.debug("Using cached crumb.")
            return True

        url = GET_CRUMB_URL
        headers = YAHOO_HEADERS

        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                text = await response.text()
                self.crumb = text.strip()
                self.cookies = response.cookies
                LOGGER.debug(f"Fetched Yahoo Finance crumb: {self.crumb}")
                return True
            else:
                LOGGER.error(f"Failed to fetch Yahoo Finance crumb: {response.status}")
                return False

    async def _fetch_yahoo_stock(self, stock_symbol: str):
        """Fetch stock data with crumb handling."""
        if not self.crumb:
            await self._fetch_yahoo_crumb()

        url = f"{YAHOO_FINANCE_BASE_URL}{stock_symbol}&crumb={self.crumb}"
        async with self.session.get(
            url, headers=YAHOO_HEADERS, cookies=self.cookies
        ) as response:
            if response.status == 429:
                retry_after = int(
                    response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
                )
                LOGGER.warning(
                    f"Rate limit hit for {stock_symbol}. Retrying after {retry_after} seconds."
                )
                await asyncio.sleep(retry_after)
                return None
            if response.status == 200:
                json_data = await response.json()
                LOGGER.debug(f"Stock data for {stock_symbol}: {json_data}")
                return json_data
            else:
                LOGGER.error(f"Failed to fetch stock data: {response.status}")
                return None

    async def _fetch_coingecko_crypto(self, crypto_symbol: str, currency: str = "usd"):
        crypto_symbol_lower = crypto_symbol.lower()
        url = f"{COINGECKO_BASE_URL}/coins/markets?vs_currency={currency}&ids={crypto_symbol_lower}"
        async with self.session.get(url) as response:
            if response.status == 429:
                retry_after = int(
                    response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
                )
                LOGGER.warning(
                    f"Rate limit hit for {crypto_symbol}. Retrying after {retry_after} seconds."
                )
                await asyncio.sleep(retry_after)
                return None
            if response.status == 200:
                json_data = await response.json()
                if json_data:
                    # Retrieve the symbol from the response
                    symbol = json_data[0].get("symbol", crypto_symbol).upper()
                    json_data[0]["symbol"] = symbol
                LOGGER.debug(f"Crypto data for {crypto_symbol}: {json_data}")
                return json_data
            else:
                LOGGER.error(f"Failed to fetch crypto data: {response.status}")
                return None

    async def get_stock_historical_data(self, stock_symbol: str, interval: str):
        """Fetch historical stock data asynchronously."""
        if not self.crumb:
            await self._fetch_yahoo_crumb()

        url = f"{YAHOO_FINANCE_HISTORICAL_URL}{stock_symbol}?interval={interval}"

        async with self.session.get(
            url, headers=YAHOO_HEADERS, cookies=self.cookies
        ) as response:
            if response.status == 429:
                retry_after = int(
                    response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
                )
                LOGGER.warning(
                    f"Rate limit hit for {stock_symbol}. Retrying after {retry_after} seconds."
                )
                await asyncio.sleep(retry_after)
                return None
            if response.status == 200:
                json_data = await response.json()
                LOGGER.debug(f"Historical data for {stock_symbol}: {json_data}")
                return json_data
            else:
                LOGGER.error(
                    f"Failed to fetch stock historical data: {response.status}"
                )
                return None

    async def get_crypto_historical_data(self, crypto_symbol: str, interval: str):
        """Fetch historical crypto data asynchronously."""
        crypto_symbol_lower = crypto_symbol.lower()
        url = f"{COINGECKO_BASE_URL}/coins/{crypto_symbol_lower}/market_chart?vs_currency=usd&days={interval}"
        LOGGER.debug(f"Requesting crypto historical data from {url}")
        async with self.session.get(url) as response:
            if response.status == 429:
                retry_after = int(
                    response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
                )
                LOGGER.warning(
                    f"Rate limit hit for {crypto_symbol}. Retrying after {retry_after} seconds."
                )
                await asyncio.sleep(retry_after)
                return None
            if response.status == 200:
                json_data = await response.json()
                LOGGER.debug(f"Crypto historical data for {crypto_symbol}: {json_data}")
                return json_data
            else:
                LOGGER.error(
                    f"Failed to fetch crypto historical data: {response.status}"
                )
                return None

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()
