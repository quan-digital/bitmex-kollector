# Bitmex Kollector
The ultimate data aggregator using Bitmex's Websocket

<img src="img/cover.jpg" align="center" />

## Setup & usage

- Setup your API key and secret on settings.py

- Run create_dirs.py to make data directories

- Run main.py


#### Public topics subscribed
```bash
"chat",                // Trollbox chat - cummulative push
"instrument",          // Instrument updates including turnover and bid/ask - continuous push overwrite 
"liquidation",         // Liquidation orders as they are entered into the book - push refreshed after 20 seconds
```

#### Private topics subscribed
```bash
"affiliate",   // Affiliate status, such as total referred users & payout % - TEST
"execution",   // Individual executions; can be multiple per order - push refreshed
"order",       // Live updates on your orders - continuous push overwrite
"margin",      // Updates on your current account balance and margin requirements - continuous push overwrite
"position",    // Updates on your positions - continuous push overwrite
"transact",    // Deposit/Withdrawal updates - TEST
"wallet"       // Bitcoin address balance data, including total deposits & withdrawals - continuous push overwrite
```

## Data

For every .csv file, the first two entries are 'DD-MM-YYYY' and 'HH:MM:SS' timestamp components.
Remaining columns are listed in order as follows.

#### Chat

- channelID

```bash
[
  {
    "id": 1,
    "name": "English"
  },
  {
    "id": 2,
    "name": "中文"
  },
  {
    "id": 3,
    "name": "Русский"
  },
  {
    "id": 4,
    "name": "한국어"
  },
  {
    "id": 5,
    "name": "日本語"
  },
  {
    "id": 6,
    "name": "Español"
  },
  {
    "id": 7,
    "name": "Français"
  }
]
```
- fromBot

- id

- message

- user

#### Liquidation

```bash
[
  {
    "orderID": "string",
    "symbol": "string",
    "side": "string",
    "price": 0,
    "leavesQty": 0
  }
]
```

### Future topics
Left out due to low update frequency/importance

```bash
"announcement",        // Site announcements - TEST
"connected",           // Statistics of connected users/bots - TEST
"insurance",           // Daily Insurance Fund updates - continuous push overwrite 
```

#### Total public topics
```bash
"announcement",        // Site announcements
"chat",                // Trollbox chat
"connected",           // Statistics of connected users/bots
"funding",             // Updates of swap funding rates. Sent every funding interval (usually 8hrs)
"instrument",          // Instrument updates including turnover and bid/ask
"insurance",           // Daily Insurance Fund updates
"liquidation",         // Liquidation orders as they are entered into the book
"orderBookL2_25",      // Top 25 levels of level 2 order book
"orderBookL2",         // Full level 2 order book
"orderBook10",         // Top 10 levels using traditional full book push
"publicNotifications", // System-wide notifications (used for short-lived messages)
"quote",               // Top level of the book
"quoteBin1m",          // 1-minute quote bins
"quoteBin5m",          // 5-minute quote bins
"quoteBin1h",          // 1-hour quote bins
"quoteBin1d",          // 1-day quote bins
"settlement",          // Settlements
"trade",               // Live trades
"tradeBin1m",          // 1-minute trade bins
"tradeBin5m",          // 5-minute trade bins
"tradeBin1h",          // 1-hour trade bins
"tradeBin1d",          // 1-day trade bins
```


#### Total private topics
```bash
"affiliate",   // Affiliate status, such as total referred users & payout %
"execution",   // Individual executions; can be multiple per order
"order",       // Live updates on your orders
"margin",      // Updates on your current account balance and margin requirements
"position",    // Updates on your positions
"privateNotifications", // Individual notifications - currently not used
"transact",    // Deposit/Withdrawal updates
"wallet"       // Bitcoin address balance data, including total deposits & withdrawals
```


