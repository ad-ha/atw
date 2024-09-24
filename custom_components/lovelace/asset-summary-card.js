class AssetSummaryCard extends HTMLElement {
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
                h1 {
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
                .value {
                    text-align: right;
                    font-weight: bold;
                }
                .positive {
                    color: var(--label-badge-green);
                }
                .negative {
                    color: var(--label-badge-red);
                }
            `;
            card.appendChild(style);
        }

        const symbol = this.config.symbol;
        const safeSymbol = symbol.toLowerCase().replace(/-/g, '_');

        const hassStates = hass.states;

        let isStock = false;
        let isCrypto = false;

        if (`sensor.${safeSymbol}_stock_price` in hassStates) {
            isStock = true;
        } else if (`sensor.${safeSymbol}_crypto_price` in hassStates) {
            isCrypto = true;
        } else {
            // Display error: symbol not found
            this.content.innerHTML = `<p style="color:red;">Symbol ${symbol} not found.</p>`;
            return;
        }

        const amountOwnedEntity = `sensor.${safeSymbol}_total_amount`;
        const purchasePriceEntity = `sensor.${safeSymbol}_purchase_price`;

        let currentPriceEntity;

        if (isStock) {
            currentPriceEntity = `sensor.${safeSymbol}_stock_price`;
        } else if (isCrypto) {
            currentPriceEntity = `sensor.${safeSymbol}_crypto_price`;
        }

        const amountOwnedState = hassStates[amountOwnedEntity];
        const purchasePriceState = hassStates[purchasePriceEntity];
        const currentPriceState = hassStates[currentPriceEntity];

        if (!amountOwnedState || !purchasePriceState || !currentPriceState) {
            this.content.innerHTML = `<p style="color:red;">Data for ${symbol.toUpperCase()} not available.</p>`;
            return;
        }

        const amountOwned = parseFloat(amountOwnedState.state);
        const purchasePrice = parseFloat(purchasePriceState.state);
        const currentPrice = parseFloat(currentPriceState.state);

        const investment = amountOwned * purchasePrice;
        const currentValue = amountOwned * currentPrice;
        const variation = currentValue - investment;
        const variationPercent = investment !== 0 ? (variation / investment) * 100 : 0;

        const variationIcon = variation >= 0 ? "mdi:trending-up" : "mdi:trending-down";
        const variationPercentIcon = variationPercent >= 0 ? "mdi:trending-up" : "mdi:trending-down";
        const variationClass = variation >= 0 ? "positive" : "negative";
        const variationPercentClass = variationPercent >= 0 ? "positive" : "negative";

        // Format numbers to fixed decimal places
        const amountOwnedFormatted = amountOwned.toFixed(4); // Adjust decimals as needed
        const purchasePriceFormatted = purchasePrice.toFixed(2);
        const currentPriceFormatted = currentPrice.toFixed(2);
        const investmentFormatted = investment.toFixed(2);
        const currentValueFormatted = currentValue.toFixed(2);
        const variationFormatted = variation.toFixed(2);
        const variationPercentFormatted = variationPercent.toFixed(2);

        this.content.innerHTML = `
            <h1>${symbol.toUpperCase()} Summary</h1>
            <div class="grid">
                <div><ha-icon class="icon" icon="mdi:scale-balance"></ha-icon> Amount Owned</div>
                <div class="value">${amountOwnedFormatted}</div>

                <div><ha-icon class="icon" icon="mdi:cash-plus"></ha-icon> Purchase Price</div>
                <div class="value">$${purchasePriceFormatted}</div>

                <div><ha-icon class="icon" icon="mdi:cash-multiple"></ha-icon> Current Price</div>
                <div class="value">$${currentPriceFormatted}</div>

                <div><ha-icon class="icon" icon="mdi:wallet-plus"></ha-icon> Investment</div>
                <div class="value">$${investmentFormatted}</div>

                <div><ha-icon class="icon" icon="mdi:wallet"></ha-icon> Current Value</div>
                <div class="value">$${currentValueFormatted}</div>

                <div><ha-icon class="icon" icon="${variationIcon}"></ha-icon> Variation</div>
                <div class="value ${variationClass}">$${variationFormatted}</div>

                <div><ha-icon class="icon" icon="${variationPercentIcon}"></ha-icon> Variation %</div>
                <div class="value ${variationPercentClass}">${variationPercentFormatted}%</div>
            </div>
        `;
    }

    setConfig(config) {
        if (!config.symbol) {
            throw new Error('You need to define a symbol');
        }
        this.config = config;
    }

    getCardSize() {
        return 3;
    }
}

customElements.define('asset-summary-card', AssetSummaryCard);
