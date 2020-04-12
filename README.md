# Bitmex Kollector
The ultimate data aggregator using Bitmex's Websocket

<img src="img/cover.jpg" align="center" />

## Setup & usage

- Setup your API key and secret on settings.py

- pip3 install -U websocket-client

- Run main.py


#### Public topics subscribed

```bash
"chat",                // Trollbox chat - cummulative push
"instrument",          // Instrument updates including turnover and bid/ask - continuous push overwrite 
"liquidation",         // Liquidation orders as they are entered into the book - push refreshed after 20 seconds
```

#### Private topics subscribed

```bash
"execution",   // Individual executions; can be multiple per order - cummulative push
"margin",      // Updates on your current account balance and margin requirements - continuous push overwrite
"position",    // Updates on your positions - continuous push overwrite
"transact",    // Deposit/Withdrawal updates - cummulative push
```

## Data

For every .csv file, the first two entries are 'DD-MM-YYYY' and 'HH:MM:SS' timestamp components.
Remaining columns are listed in order as follows.

#### Chat

Chat data is updated on arrival.

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

Liquidation data is updated on arrival.

```bash
  {
    "orderID": "string",
    "symbol": "string",
    "side": "string",
    "price": 0,
    "leavesQty": 0
  }
```

#### Transact

Transact data is updated on arrival.

```bash
  {
    "transactID": "string",
    "account": 0,
    "currency": "string",
    "transactType": "string",
    "amount": 0,
    "fee": 0,
    "transactStatus": "string",
    "address": "string",
    "text": "string",
  }
```

### Execution 

Execution data is updated on arrival.

```bash
  {
    "execID": "string",
    "orderID": "string",
    "clOrdID": "string",
    "account": 0,
    "symbol": "string",
    "side": "string",
    "orderQty": 0,
    "price": 0,
    "execType": "string",
    "ordType": "string",
    "commission": 0,
    "text": "string"
  }
```

### Instrument

Instrument data is updated every settings.LOOP_INTERVAL seconds (standard is 1 second).

```bash
  {
    "symbol": "string",
    "state": "string",
    "fundingRate": 0,
    "indicativeFundingRate": 0,
    "prevClosePrice": 0,
    "totalVolume": 0,
    "volume": 0,
    "volume24h": 0,
    "totalTurnover": 0,
    "turnover": 0,
    "turnover24h": 0,
    "homeNotional24h": 0,
    "foreignNotional24h": 0,
    "prevPrice24h": 0,
    "vwap": 0,
    "highPrice": 0,
    "lowPrice": 0,
    "lastPrice": 0,
    "lastPriceProtected": 0,
    "lastTickDirection": "string",
    "lastChangePcnt": 0,
    "bidPrice": 0,
    "midPrice": 0,
    "askPrice": 0,
    "impactBidPrice": 0,
    "impactMidPrice": 0,
    "impactAskPrice": 0,
    "openInterest": 0,
    "openValue": 0,
    "markPrice": 0,
    "indicativeSettlePrice": 0
  }
```

### Margin

Margin data is updated on every change.

```bash
{
  "account": 0,
  "currency": "string",
  "amount": 0,
  "realisedPnl": 0,
  "unrealisedPnl": 0,
  "indicativeTax": 0,
  "unrealisedProfit": 0,
  "walletBalance": 0,
  "marginBalance": 0,
  "marginLeverage": 0,
  "marginUsedPcnt": 0,
  "availableMargin": 0,
  "withdrawableMargin": 0
}
```

### Position

Position data is updated on every change.

```bash
  {
    "account": 0,
    "symbol": "string",
    "commission": 0,
    "leverage": 0,
    "crossMargin": true,
    "rebalancedPnl": 0,
    "openOrderBuyQty": 0,
    "openOrderBuyCost": 0,
    "openOrderSellQty": 0,
    "openOrderSellCost": 0,
    "execBuyQty": 0,
    "execBuyCost": 0,
    "execSellQty": 0,
    "execSellCost": 0,
    "currentQty": 0,
    "currentCost": 0,
    "isOpen": true,
    "markPrice": 0,
    "markValue": 0,
    "homeNotional": 0,
    "foreignNotional": 0,
    "posState": "string",
    "realisedPnl": 0,
    "unrealisedPnl": 0,
    "avgCostPrice": 0,
    "avgEntryPrice": 0,
    "breakEvenPrice": 0,
    "liquidationPrice": 0,
    "bankruptPrice": 0,
  }
```


### Future topics

Left out due to low update frequency/importance. May never be necessary.

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
"affiliate",   // Affiliate status, such as total referred users & payout % - push refreshed
"execution",   // Individual executions; can be multiple per order
"order",       // Live updates on your orders - continuous push overwrite
"margin",      // Updates on your current account balance and margin requirements
"position",    // Updates on your positions
"privateNotifications", // Individual notifications - currently not used
"transact",    // Deposit/Withdrawal updates
"wallet"       // Bitcoin address balance data, including total deposits & withdrawals - continuous push overwrite
```


