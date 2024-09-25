[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/custom_components)
![GitHub Release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/ad-ha/atw?include_prereleases)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/ad-ha/atw/latest/total)

[![HACS Action](https://github.com/ad-ha/atw/actions/workflows/validate.yml/badge.svg)](https://github.com/ad-ha/atw/actions/workflows/validate.yml)
[![Hassfest](https://github.com/ad-ha/atw/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/ad-ha/atw/actions/workflows/hassfest.yaml)

![logo-512](https://github.com/user-attachments/assets/489dda3f-d008-490b-88fe-331af026ad27)

# Advanced Trading Wallet

<a href="https://buymeacoffee.com/varetas3d" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

Track your stock and cryptocurrency portfolio directly in Home Assistant. The Advanced Trading Wallet integration allows you to monitor your investments, view real-time data, and perform virtual buy/sell transactions, all within your smart home ecosystem.

## Introduction

The Advanced Trading Wallet (ATW) integration brings your financial portfolio into Home Assistant, providing real-time tracking of stocks and cryptocurrencies. With support for multiple API providers and customizable updates, you can keep a close eye on your investments and manage them efficiently.

## Features

- **Portfolio Tracking**: Monitor your stocks and cryptocurrencies in real-time.
- **Virtual Transactions**: Log virtual buy and sell orders for stocks and cryptocurrencies.
- **Comprehensive Sensors**: Access detailed information through various sensors, including total portfolio value, percentage change, and individual asset summaries.
- **Lovelace Cards**: Visualize your portfolio using custom Lovelace cards.
  - **Portfolio Summary Card**: Overview of your entire portfolio.
  - **Transaction Recorder Card**: Log virtual transactions directly from the UI.
  - **Asset Summary Card**: Detailed view of individual assets.
- **Localization**: Support for multiple languages, including English and Spanish.
- **Customizable Update Intervals**: Set how often the integration fetches data from API providers.

## Installation

### HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed in your Home Assistant setup.
2. Go to **HACS** in the sidebar.
3. Click on **Integrations**.
4. Click the **+ Explore & Download Repositories** button.
5. Search for **Advanced Trading Wallet**.
6. Click **Download** to install the integration.
7. Restart Home Assistant.

### Manual Installation

1. Download the `advanced_trading_wallet` folder from the [GitHub repository](https://github.com/ad-ha/atw) and place it in your `config/custom_components` directory.
   - Your directory structure should look like this: `config/custom_components/advanced_trading_wallet/`
2. Restart Home Assistant.

## Configuration

### Adding the Integration

1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Click on **+ Add Integration**.
3. Search for **Advanced Trading Wallet** and select it.
4. Follow the setup wizard:
   - **API Provider**: Choose your preferred API provider (e.g., Yahoo Finance, CoinGecko).
   - **Preferred Currency**: Optionally set your preferred currency (default is USD).
5. Select the asset type you want to track:
   - **Stocks** or **Cryptocurrencies**.
6. Enter the details of the assets you wish to track:
   - **Symbol**: Stock ticker or cryptocurrency symbol (e.g., AAPL, bitcoin).
   - **Amount Owned**: The amount of the asset you own.
   - **Purchase Price**: The average price at which you purchased the asset.
7. Repeat the process to add more assets or asset types.

### Options

You can adjust the scan interval to control how often the integration updates data from API providers.

1. Go to **Settings** > **Devices & Services**.
2. Find the **Advanced Trading Wallet** integration and click **Configure**.
3. Set the desired **Scan Interval** in minutes.

## Services

The integration provides services to log virtual buy and sell transactions, allowing you to update your portfolio dynamically.

### Available Services

- `advanced_trading_wallet.buy_stock`
- `advanced_trading_wallet.sell_stock`
- `advanced_trading_wallet.buy_crypto`
- `advanced_trading_wallet.sell_crypto`

### Service Data Examples

#### Buy Stock

```yaml
service: advanced_trading_wallet.buy_stock
data:
  stock_symbol: "AAPL"
  amount: 10
  purchase_price: 150.25
```

```yaml
service: advanced_trading_wallet.sell_crypto
data:
  crypto_symbol: "bitcoin"
  amount: 0.5
```

## Sensors and Entities
The integration creates various sensors to help you monitor your portfolio:

### Sensors
* Total Portfolio Value (sensor.total_portfolio_value)
* Total Stocks Value (sensor.total_stocks_value)
* Total Crypto Value (sensor.total_crypto_value)
* Total Investment (sensor.total_investment)
* Percentage Change (sensor.percentage_change)
* Total Variation (sensor.total_variation)
* Individual Asset Sensors:
* Stock Price (sensor.{symbol}_stock_price)
* Crypto Price (sensor.{symbol}_crypto_price)
* Amount Owned (sensor.{symbol}_total_amount)
* Purchase Price (sensor.{symbol}_purchase_price)

### Lovelace Cards
Enhance your Home Assistant dashboard with custom Lovelace cards designed for the Advanced Trading Wallet integration.

Add the resources to your Lovelace configuration:

```yaml
resources:
  - url: /hacsfiles/advanced_trading_wallet/lovelace/portfolio-card.js
    type: module
  - url: /hacsfiles/advanced_trading_wallet/lovelace/transaction-card.js
    type: module
  - url: /hacsfiles/advanced_trading_wallet/lovelace/asset-summary-card.js
    type: module
```

Restart Home Assistant or reload the Lovelace resources.

Usage
Portfolio Summary Card

```yaml
type: 'custom:portfolio-card'
```

Transaction Recorder Card

```yaml
type: 'custom:transaction-card'
```

Asset Summary Card

```yaml
type: 'custom:asset-summary-card'
symbol: 'AAPL'  # Replace with your asset symbol
```

## Localization of the Integration
The integration itself supports multiple languages. Translations are stored in the translations directory.

### Available Languages
* English (en.json)
* Spanish (es.json)

## Contributing
Contributions are welcome! If you have suggestions, encounter issues, or wish to add support for more languages, please open an issue or submit a pull request on the GitHub repository.


## Changelog
```
0.1.0
* Initial release of the Advanced Trading Wallet integration.
* Support for tracking stocks and cryptocurrencies.
* Virtual buy and sell services.
* Custom Lovelace cards for portfolio summary, transaction recording, and asset summaries.
* Localization support for English and Spanish.
```


## Credits
This integration was inspired by the need to monitor investment portfolios within Home Assistant, providing a seamless and integrated experience.


## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
THIS PROJECT IS NOT IN ANY WAY ASSOCIATED OR RELATED TO YAHOO OR COINGECKO. The use of Yahoo Finance and CoinGecko APIs is intended only to retrieve realtime data as provided by the APIs.
The information here and online is for educational and resource purposes only and therefore the developers do not endorse or condone any inappropriate use of it, and take no legal responsibility for the functionality or security of your devices.
Stock markets or cryptomarkets are volatile and your investments may suffer losses, which cannot, in any way, endorsed to the developers of this project. This integration is limited to show the current data and status fof your investments or general stocks or crypto coins, and is not to be used as an advisor as it does not provide any relevant information or recommendation on actions to be taken with your own investments.
