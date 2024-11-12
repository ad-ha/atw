import logging
from homeassistant.components.sensor import SensorDeviceClass

# Domain name for the integration
DOMAIN = "advanced_trading_wallet"

# API Providers
API_PROVIDERS = ["Yahoo Finance", "CoinGecko"]

# API base URLs
YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
YAHOO_FINANCE_HISTORICAL_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Crumb and consent-related URLs for Yahoo Finance
GET_CRUMB_URL = "https://query2.finance.yahoo.com/v1/test/getcrumb"

# Yahoo Request headers
YAHOO_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/91.0.4472.124 Safari/537.36",
}

# Default retry after hitting the rate limit
DEFAULT_RETRY_AFTER = 60  # seconds

# Historical data intervals
DEFAULT_HISTORICAL_INTERVALS = ["1d", "5d", "1wk", "1mo", "1y", "5y"]
DEFAULT_HISTORICAL_INTERVAL = "1wk"

# Available platforms (sensor, etc.)
PLATFORMS = ["sensor"]

# Default values
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_API_PROVIDER = "Yahoo Finance"

# Services
SERVICE_REFRESH_DATA = "refresh_data"
SERVICE_GET_HISTORICAL_DATA = "get_historical_data"
SERVICE_BUY_STOCKS = "buy_stocks"
SERVICE_SELL_STOCKS = "sell_stocks"
SERVICE_BUY_CRYPTO = "buy_crypto"
SERVICE_SELL_CRYPTO = "sell_crypto"

# Attributes for services
ATTR_STOCK_SYMBOL = "stock_symbol"
ATTR_CRYPTO_SYMBOL = "crypto_symbol"

# Device classes
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

# Logger declaration
LOGGER = logging.getLogger(__name__)
