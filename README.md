# Bitmex Kollector
The ultimate data aggregator using Bitmex's Websocket - FATALITY 💉💀🗡

<img src="img/cover.jpg" align="center" />

## Setup & usage

- pip3 install git+https://github.com/quan-digital/bitmex-kollector#egg=bitmex_kollector

- copy, config and run main.py :)

- data will be stored in settings.DATA_DIR ('data/' by default, change for deploy).

- run on EC2 eu-west-1 (Ireland) because that's where Bitmex' Websocket is hosted.

- base Kollector will generate about 140MB of data a day, with more than half going towards 'instrument'. So estimate around 3GB of data a month, or 50GB a year. For bot operation, you can divide that by 60 at least.

#### Public topics subscribed

```bash
"chat",                // Trollbox chat - cummulative push
"instrument",          // Instrument updates including turnover and bid/ask - continuous push overwrite 
"liquidation",         // Liquidation orders as they are entered into the book - push refreshed after 20 seconds
"quoteBin1m",          // 1-minute quote bins - cummulative push
"tradeBin1m",          // 1-minute trade bins - cummulative push
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

```bash
{
  "channelID": 0,
  "fromBot": false,
  "id": 0,
  "message": "string",
  "user": "string"
}

# "channelID" as follows
{
1 : "English",
2 : "中文",
3 : "Русский",
4 : "한국어",
5 : "日本語",
6 : "Español",
7 : "Français"
}
```

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
    "text": "string"
  }
```

#### Execution 

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

#### Instrument

Instrument data is updated every settings.LOOP_INTERVAL seconds (default is 1 second).

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
### Trade

Trade data is updated every minute.

```bash
{
"symbol": "string",
"open": 0,
"high": 0,
"low": 0,
"close": 0,
"trades": 0,
"volume": 0,
"vwap": 0,
"lastSize": 0,
"turnover": 0,
"homeNotional": 0,
"foreignNotional": 0
}
```

### Quote

Quote data is updated every minute.

```bash
{ 
"symbol": "string", 
"bidSize": 0, 
"bidPrice": 0, 
"askPrice": 0, 
"askSize": 0
}
```

#### Margin

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

#### Position

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
    "bankruptPrice": 0
  }
```


### Websocket Rate Limits

```bash
Subscription: Consumes one token from your request limiter.
Connection: 20 per hour, on a separate limiter.

# Responses
{"status":429,"error":"Rate limit exceeded, retry in 1 seconds.","meta":{"retryAfter":1},"request":{"op":"subscribe","args":"orderBook"}}

HTTP/1.1 429 Too Many Requests
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1506983924
Retry-After: 29
Content-Type: application/json
Content-Length: 55
Date: Mon, 02 Oct 2017 21:43:49 GMT
Connection: keep-alive

{"error":"Rate limit exceeded, retry in 29 seconds."}
```

### Total public topics
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
"tradeBin1d"           // 1-day trade bins
```


### Total private topics
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

### Left out topics

Left out due to low update frequency/importance. 

```bash
"announcement",        // Site announcements - low frequency & easily fetchable via rest
"connected",           // Statistics of connected users/bots - apparently discontinued
"insurance",           // Daily Insurance Fund updates - liquidation already gets it, continuous push overwrite 
"orders"               // Live updates on your orders - our bots already deals with orders via POST orders anyway, and generic order data is already fetched through the 'position' topic, continuous push overwrite
```
