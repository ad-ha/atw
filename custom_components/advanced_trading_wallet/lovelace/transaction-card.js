class TransactionCard extends HTMLElement {
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
                button {
                    background-color: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 5px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: var(--primary-color-dark);
                }
                input, select {
                    margin: 5px;
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid var(--divider-color);
                    width: 100%;
                }
                label {
                    display: block;
                    margin-top: 10px;
                }
            `;
            card.appendChild(style);
        }

        // Extract stock and crypto symbols from the Home Assistant state
        const stockSymbols = Object.keys(hass.states).filter(e => e.startsWith('sensor.') && e.endsWith('_stock_price')).map(e => e.replace('sensor.', '').replace('_stock_price', '').toUpperCase());
        const cryptoSymbols = Object.keys(hass.states).filter(e => e.startsWith('sensor.') && e.endsWith('_crypto_price')).map(e => e.replace('sensor.', '').replace('_crypto_price', '').toUpperCase());

        // Check if symbols exist
        if (stockSymbols.length === 0 && cryptoSymbols.length === 0) {
            this.content.innerHTML = `<p style="color:red;">No stocks or crypto available</p>`;
            return;
        }

        // Clear content to prevent duplication
        this.content.innerHTML = '';

        // Create a toggle for Buy/Sell actions
        const buySellToggle = document.createElement('div');
        buySellToggle.innerHTML = `
            <h2>Transaction Recorder</h2>
            <label>Action:</label>
            <select id="action-select">
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
            </select>
        `;
        this.content.appendChild(buySellToggle);

        // Create a container for the form that updates dynamically
        const formContainer = document.createElement('div');
        formContainer.id = "form-container";
        this.content.appendChild(formContainer);

        const actionSelect = buySellToggle.querySelector('#action-select');

        // Function to update form based on the selected action (Buy/Sell)
        const updateForm = () => {
            const action = actionSelect.value;
            formContainer.innerHTML = ''; // Clear form content on action change

            const symbolSelect = document.createElement('select');
            symbolSelect.id = "symbol-select";
            symbolSelect.innerHTML = `
                ${stockSymbols.map(symbol => `<option value="${symbol}">${symbol} (Stock)</option>`).join('')}
                ${cryptoSymbols.map(symbol => `<option value="${symbol}">${symbol} (Crypto)</option>`).join('')}
            `;
            formContainer.innerHTML += `<label>Stock/Crypto to ${action.charAt(0).toUpperCase() + action.slice(1)}:</label>`;
            formContainer.appendChild(symbolSelect);

            // Create input for amount
            const amountInput = document.createElement('input');
            amountInput.id = "amount-input";
            amountInput.type = "number";
            amountInput.placeholder = "Amount";
            formContainer.appendChild(amountInput);

            // Create input for price per unit if action is Buy
            if (action === 'buy') {
                const priceInput = document.createElement('input');
                priceInput.id = "price-input";
                priceInput.type = "number";
                priceInput.placeholder = "Price per unit";
                formContainer.appendChild(priceInput);
            }

            // Create confirmation button
            const confirmButton = document.createElement('button');
            confirmButton.innerText = action.charAt(0).toUpperCase() + action.slice(1);
            formContainer.appendChild(confirmButton);

            // Add event listener for the confirmation button
            confirmButton.addEventListener('click', () => {
                const symbol = symbolSelect.value;
                const amount = parseFloat(amountInput.value);
                const price = action === 'buy' ? parseFloat(formContainer.querySelector('#price-input').value) : null;

                // Call Home Assistant service for Buy or Sell based on action
                if (action === 'buy') {
                    hass.callService('advanced_trading_wallet', 'buy_stock', {
                        stock_symbol: symbol,
                        amount: amount,
                        purchase_price: price,
                    }).then(() => {
                        alert('Buy transaction successful!');
                    });
                } else if (action === 'sell') {
                    hass.callService('advanced_trading_wallet', 'sell_stock', {
                        stock_symbol: symbol,
                        amount: amount,
                    }).then(() => {
                        alert('Sell transaction successful!');
                    });
                }
            });
        };

        // Load the form initially
        updateForm();

        // Update form when the action changes (Buy/Sell)
        actionSelect.addEventListener('change', updateForm);
    }

    setConfig(config) {
        // Set the configuration for the card (if needed)
    }

    getCardSize() {
        return 2; // Size of the card
    }
}

customElements.define('transaction-card', TransactionCard);
