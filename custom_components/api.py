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

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    text = await response.text()
                    self.crumb = text.strip()
                    self.cookies = response.cookies
                    LOGGER.debug(f"Fetched Yahoo Finance crumb: {self.crumb}")
                    return True
                else:
                    LOGGER.error(
                        f"Failed to fetch Yahoo Finance crumb: {response.status}"
                    )
                    return False

    async def _fetch_yahoo_stock(self, stock_symbol: str):
        """Fetch stock data with crumb handling."""
        if not self.crumb:
            await self._fetch_yahoo_crumb()

        url = f"{YAHOO_FINANCE_BASE_URL}{stock_symbol}&crumb={self.crumb}"
        async with aiohttp.ClientSession(cookies=self.cookies) as session:
            async with session.get(url, headers=YAHOO_HEADERS) as response:
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
        url = f"{COINGECKO_BASE_URL}/coins/markets?vs_currency={currency}&ids={crypto_symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
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
                    LOGGER.debug(f"Crypto data for {crypto_symbol}: {json_data}")
                    return json_data
                else:
                    LOGGER.error(f"Failed to fetch crypto data: {response.status}")
                    return None

    async def fetch_autocomplete(self, query: str, asset_type: str):
        """Fetch autocomplete suggestions from relevant APIs."""
        if asset_type == "Stock" and self.api_provider == "Yahoo Finance":
            url = f"{YAHOO_FINANCE_BASE_URL}/lookup/autocomplete?q={query}"
        elif asset_type == "Crypto" and self.api_provider == "CoinGecko":
            url = f"{COINGECKO_BASE_URL}/search?query={query}"
        else:
            raise ValueError("Invalid API provider")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 429:
                    retry_after = int(
                        response.headers.get("Retry-After", DEFAULT_RETRY_AFTER)
                    )
                    LOGGER.warning(
                        f"Rate limit hit. Retrying after {retry_after} seconds."
                    )
                    await asyncio.sleep(retry_after)
                    return None
                if response.status == 200:
                    return await response.json()
                else:
                    LOGGER.error(
                        f"Failed to fetch autocomplete data: {response.status}"
                    )
                    return None

    async def get_stock_historical_data(self, stock_symbol: str, interval: str):
        """Fetch historical stock data asynchronously."""
        if not self.crumb:
            await self._fetch_yahoo_crumb()

        url = f"{YAHOO_FINANCE_HISTORICAL_URL}{stock_symbol}?interval={interval}"

        async with aiohttp.ClientSession(cookies=self.cookies) as session:
            async with session.get(url, headers=YAHOO_HEADERS) as response:
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
        url = f"{COINGECKO_BASE_URL}/coins/{crypto_symbol}/market_chart?vs_currency=usd&days={interval}"
        LOGGER.debug(f"Requesting crypto historical data from {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
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
                    LOGGER.debug(
                        f"Crypto historical data for {crypto_symbol}: {json_data}"
                    )
                    return json_data
                else:
                    LOGGER.error(
                        f"Failed to fetch crypto historical data: {response.status}"
                    )
                    return None

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()
