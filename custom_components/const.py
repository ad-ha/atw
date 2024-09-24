import logging

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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

# Default retry after hitting the rate limit
DEFAULT_RETRY_AFTER = 60  # seconds

# Historical data intervals
DEFAULT_HISTORICAL_INTERVALS = ["1d", "5d", "1wk", "1mo", "1y", "5y"]
DEFAULT_HISTORICAL_INTERVAL = "1wk"  # Default interval for historical data

# Available platforms (sensor, etc.)
PLATFORMS = ["sensor"]

# Default values
DEFAULT_SCAN_INTERVAL = 10  # minutes
DEFAULT_API_PROVIDER = "Yahoo Finance"

# Services
SERVICE_REFRESH_DATA = "refresh_data"
SERVICE_GET_HISTORICAL_DATA = "get_historical_data"
SERVICE_BUY_STOCKS = "buy_stocks"
SERVICE_SELL_STOCKS = "sell_stocks"
SERVICE_BUY_CRIPTO = "buy_stocks"
SERVICE_SELL_CRIPTO = "sell_stocks"

# Attributes for services
ATTR_STOCK_SYMBOL = "stock_symbol"
ATTR_CRYPTO_SYMBOL = "crypto_symbol"

# Device classes
STOCK_SENSOR_TYPES = [
    "Stock Price",
    "Market Cap",
    "Day High",
    "Day Low",
    "Post Market Price",
    "Post Market Change",
    "Bid",
    "Ask",
    "52-Week High",
    "52-Week Low",
    "Dividend Rate",
    "Earnings Per Share (EPS)",
    "Price to Earnings (PE) Ratio",
    "Volume",
    "Shares Outstanding",
    "Book Value",
]

CRYPTO_SENSOR_TYPES = [
    "Crypto Price",
    "Market Cap",
    "24h High",
    "24h Low",
    "ATH (All Time High)",
    "ATL (All Time Low)",
    "Circulating Supply",
    "Price Change (24h)",
]

# Logger declaration
LOGGER = logging.getLogger(__name__)
