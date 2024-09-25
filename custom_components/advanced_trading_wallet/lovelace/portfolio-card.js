class PortfolioCard extends HTMLElement {
    set hass(hass) {
        if (!this.content) {
            const card = document.createElement('ha-card');
            this.content = document.createElement('div');
            this.content.style.padding = '16px';
            card.appendChild(this.content);
            this.appendChild(card);

            const style = document.createElement('style');
            style.textContent = `
                ha-card {
                    background-color: var(--card-background-color);
                    color: var(--primary-text-color);
                    border-radius: var(--ha-card-border-radius, 4px);
                    box-shadow: var(--ha-card-box-shadow, none);
                    padding: 16px;
                    margin: 8px 0;
                }
                h2 {
                    font-size: 1.5em;
                    margin-bottom: 16px;
                }
                .grid {
                    display: grid;
                    grid-template-columns: auto auto;
                    justify-content: space-between;
                    align-items: center;
                    row-gap: 10px;
                }
                .icon {
                    margin-right: 10px;
                }
                .atw-value {
                    text-align: right;
                }
            `;
            card.appendChild(style);
        }

        const totalValue = hass.states['sensor.total_portfolio_value'].state;
        const totalStocksValue = hass.states['sensor.total_stocks_value'].state;
        const totalCryptoValue = hass.states['sensor.total_crypto_value'].state;
        const totalInvestment = hass.states['sensor.total_investment'].state;
        const percentageChange = hass.states['sensor.percentage_change'].state;
        const totalVariation = hass.states['sensor.total_variation'].state;

        const percentageChangeIcon = percentageChange >= 0 ? "mdi:trending-up" : "mdi:trending-down";
        const variationIcon = totalVariation >= 0 ? "mdi:trending-up" : "mdi:trending-down";

        this.content.innerHTML = `
            <h2>Portfolio Summary</h2>
            <div class="grid">
                <div><ha-icon class="icon" icon="mdi:wallet-bifold-outline"></ha-icon> Total Investment</div>
                <div class="atw-value">$${parseFloat(totalInvestment).toFixed(2)}</div>

                <div><ha-icon class="icon" icon="mdi:chart-line"></ha-icon> Total Portfolio Value</div>
                <div class="atw-value">$${parseFloat(totalValue).toFixed(2)}</div>

                <div><ha-icon class="icon" icon="${variationIcon}"></ha-icon> Total Variation</div>
                <div class="atw-value">$${parseFloat(totalVariation).toFixed(2)}</div>

                <div><ha-icon class="icon" icon="${percentageChangeIcon}"></ha-icon> Percentage Change</div>
                <div class="atw-value">${parseFloat(percentageChange).toFixed(2)}%</div>

                <div><ha-icon class="icon" icon="mdi:currency-usd"></ha-icon> Total Stocks Value</div>
                <div class="atw-value">$${parseFloat(totalStocksValue).toFixed(2)}</div>

                <div><ha-icon class="icon" icon="mdi:currency-btc"></ha-icon> Total Crypto Value</div>
                <div class="atw-value">$${parseFloat(totalCryptoValue).toFixed(2)}</div>
            </div>
        `;
    }

    setConfig(config) {
        // Set the configuration for the card
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('portfolio-card', PortfolioCard);
