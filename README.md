# bitcoin-paper-trading-sim
Bitcoin paper trading simulator that simulates long and short positions based on bitcoin price data from coinbase. Implements short/long position signaling from MA50(moving average for 50 time units) crossing MA20.

# More in depth explanation
This program (or app, when packaged through PyInstaller) simulates paper trades using price data from Coinbase, accessible via the API at [https://api.coinbase.com/v2/prices/spot?currency=USD](https://api.coinbase.com/v2/prices/spot?currency=USD). The simulation supports both long and short positions, without accounting for simulated exchange or network fees. 

Long positions are entered and exited based on current price data from Coinbase, which may not be precisely accurate to market data. Short positions are simulated without interest, utilizing 50% collateral. For example, a $50 allocation would simulate a short sale of $100 worth of Bitcoin. Returns for short positions are calculated as follows: collateral + ((price_sold - price_to_exit) * ((collateral * 2) / price_sold)).

The application features a graph that displays the imported price data from Coinbase, along with moving averages for 5, 20, and 50 time intervals. Users can toggle the visibility of the graph using a button located at the bottom of the interface. The top left corner displays your simulated profit or loss as a percentage of your initial balance. The bottom right corner shows the frequency of price data updates on the graph and the price display at the top of the UI. 

A menu/settings button is located at the top right. When clicked, it allows users to change the time interval for price updates or update/change their balance. Updating or changing the balance resets price history data, moving average history data, active long/short positions, and all display buttons to their default or updated values. The menu also provides an option to modify the time interval for price and graph updates, with a default interval of 5 seconds, which can be changed to any value in seconds. This action resets the price data and moving average data but does not close active positions.

The moving average indicators change color based on the following conditions: they turn green when the MA50 crosses above the MA20 (indicating a long position) and serve as a short indicator when the MA50 crosses below the MA20.



# Variables
price_history - tracks bitcoin price history since either 1: user opened program 2: user adjusted time interval that the program updates

ma5_history/ma20_history/ma_50_history - contains the moving average history since either 1: user opened program 2: user adjusted time interval that the program updates

original_balance - original balance that doesn't change trade to trade, used to calculate P/L. Only changed with settings balance change

capital - balance that changes trade to trade, what is displayed at top of screen

invested_long - tracks the size of open long positions, measured in btc

open_short_positions - tracks all short position, array of array, [position_id, price_sold, collateral]

update_time - time between UI updates (excluding UI updates triggered by user events, such as sells or buys) and price updates
