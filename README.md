# Bitmex Kollector
The ultimate data aggregator using Bitmex's Websocket

<img src="img/cover.jpg" align="center" />

## Setup & usage

- Setup your API key and secret on settings.py

- Run main.py

TODO:
log headers


#### Public topics subscribed
```bash
"chat",                // Trollbox chat - cummulative push
"instrument",          // Instrument updates including turnover and bid/ask - continuous push overwrite 
"liquidation",         // Liquidation orders as they are entered into the book - push refreshed after 20 seconds
```

#### Private topics subscribed
```bash
"execution",   // Individual executions; can be multiple per order - cummulative push
"order",       // Live updates on your orders - continuous push overwrite
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

{'account': 240020, 'symbol': 'XBTUSD', 'currency': 'XBt', 'underlying': 'XBT', 'quoteCurrency': 'USD', 'commission': 0.00075, 'initMarginReq': 0.01, 'maintMarginReq': 0.005, 'riskLimit': 20000000000, 'leverage': 100, 'crossMargin': True, 'deleveragePercentile': 1, 'rebalancedPnl': 64, 'prevRealisedPnl': -21, 'prevUnrealisedPnl': 0, 'prevClosePrice': 6863.05, 'openingTimestamp': '2020-04-12T19:00:00.000Z', 'openingQty': 0, 'openingCost': -17, 'openingComm': 60, 'openOrderBuyQty': 1, 'openOrderBuyCost': -14100, 'openOrderBuyPremium': 0, 'openOrderSellQty': 0, 'openOrderSellCost': 0, 'openOrderSellPremium': 0, 'execBuyQty': 2, 'execBuyCost': 28050, 'execSellQty': 1, 'execSellCost': 14026, 'execQty': 1, 'execCost': -14024, 'execComm': 30, 'currentTimestamp': '2020-04-12T19:35:30.382Z', 'currentQty': 1, 'currentCost': -14041, 'currentComm': 90, 'realisedCost': -16, 'unrealisedCost': -14025, 'grossOpenCost': 14100, 'grossOpenPremium': 0, 'grossExecCost': 14025, 'isOpen': True, 'markPrice': 7135.79, 'markValue': -14014, 'riskValue': 28114, 'homeNotional': 0.00014014, 'foreignNotional': -1, 'posState': '', 'posCost': -14025, 'posCost2': -14025, 'posCross': 0, 'posInit': 141, 'posComm': 11, 'posLoss': 0, 'posMargin': 152, 'posMaint': 129, 'posAllowance': 0, 'taxableMargin': 0, 'initMargin': 163, 'maintMargin': 163, 'sessionMargin': 0, 'targetExcessMargin': 0, 'varMargin': 0, 'realisedGrossPnl': 16, 'realisedTax': 0, 'realisedPnl': -74, 'unrealisedGrossPnl': 11, 'longBankrupt': 0, 'shortBankrupt': 0, 'taxBase': 0, 'indicativeTaxRate': None, 'indicativeTax': 0, 'unrealisedTax': 0, 'unrealisedPnl': 11, 'unrealisedPnlPcnt': 0.0008, 'unrealisedRoePcnt': 0.0784, 'simpleQty': None, 'simpleCost': None, 'simpleValue': None, 'simplePnl': None, 'simplePnlPcnt': None, 'avgCostPrice': 7130, 'avgEntryPrice': 7130, 'breakEvenPrice': 7135.5, 'marginCallPrice': 56.5, 'liquidationPrice': 56.5, 'bankruptPrice': 56.5, 'timestamp': '2020-04-12T19:35:30.382Z', 'lastPrice': 7135.79, 'lastValue': -14014}

{'orderID': '58c29050-3acf-3c29-80d3-0ed7ea50002c', 'clOrdID': '', 'clOrdLinkID': '', 'account': 240020, 'symbol': 'XBTUSD', 'side': 'Buy', 'simpleOrderQty': None, 'orderQty': 1, 'price': 7092, 'displayQty': None, 'stopPx': None, 'pegOffsetValue': None, 'pegPriceType': '', 'currency': 'USD', 'settlCurrency': 'XBt', 'ordType': 'Limit', 'timeInForce': 'GoodTillCancel', 'execInst': '', 'contingencyType': '', 'exDestination': 'XBME', 'ordStatus': 'New', 'triggered': '', 'workingIndicator': True, 'ordRejReason': '', 'simpleLeavesQty': None, 'leavesQty': 1, 'simpleCumQty': None, 'cumQty': 0, 'avgPx': None, 'multiLegReportingType': 'SingleSecurity', 'text': 'Submission from testnet.bitmex.com', 'transactTime': '2020-04-12T19:34:58.115Z', 'timestamp': '2020-04-12T19:34:58.115Z'}


[{'orderID': '58c29050-3acf-3c29-80d3-0ed7ea50002c', 'clOrdID': '', 'clOrdLinkID': '', 'account': 240020, 'symbol': 'XBTUSD', 'side': 'Buy', 'simpleOrderQty': None, 'orderQty': 1, 'price': 7092, 'displayQty': None, 'stopPx': None, 'pegOffsetValue': None, 'pegPriceType': '', 'currency': 'USD', 'settlCurrency': 'XBt', 'ordType': 'Limit', 'timeInForce': 'GoodTillCancel', 'execInst': '', 'contingencyType': '', 'exDestination': 'XBME', 'ordStatus': 'New', 'triggered': '', 'workingIndicator': True, 'ordRejReason': '', 'simpleLeavesQty': None, 'leavesQty': 1, 'simpleCumQty': None, 'cumQty': 0, 'avgPx': None, 'multiLegReportingType': 'SingleSecurity', 'text': 'Submission from testnet.bitmex.com', 'transactTime': '2020-04-12T19:34:58.115Z', 'timestamp': '2020-04-12T19:34:58.115Z'}, 

{'orderID': 'b62bb56f-3e71-06af-6163-79686ab35c4c', 'clOrdID': '', 'clOrdLinkID': '', 'account': 240020, 'symbol': 'XBTUSD', 'side': 'Buy', 'simpleOrderQty': None, 'orderQty': 1, 'price': 7082, 'displayQty': None, 'stopPx': None, 'pegOffsetValue': None, 'pegPriceType': '', 'currency': 'USD', 'settlCurrency': 'XBt', 'ordType': 'Limit', 'timeInForce': 'GoodTillCancel', 'execInst': '', 'contingencyType': '', 'exDestination': 'XBME', 'ordStatus': 'New', 'triggered': '', 'workingIndicator': True, 'ordRejReason': '', 'simpleLeavesQty': None, 'leavesQty': 1, 'simpleCumQty': None, 'cumQty': 0, 'avgPx': None, 'multiLegReportingType': 'SingleSecurity', 'text': 'Submission from testnet.bitmex.com', 'transactTime': '2020-04-12T19:37:01.311Z', 'timestamp': '2020-04-12T19:37:01.311Z'}, 

{'orderID': '4188f5b5-5f78-95ee-1cbd-c111cfe1bf5e', 'clOrdID': '', 'clOrdLinkID': '', 'account': 240020, 'symbol': 'XBTUSD', 'side': 'Buy', 'simpleOrderQty': None, 'orderQty': 1, 'price': 7052, 'displayQty': None, 'stopPx': None, 'pegOffsetValue': None, 'pegPriceType': '', 'currency': 'USD', 'settlCurrency': 'XBt', 'ordType': 'Limit', 'timeInForce': 'GoodTillCancel', 'execInst': '', 'contingencyType': '', 'exDestination': 'XBME', 'ordStatus': 'New', 'triggered': '', 'workingIndicator': True, 'ordRejReason': '', 'simpleLeavesQty': None, 'leavesQty': 1, 'simpleCumQty': None, 'cumQty': 0, 'avgPx': None, 'multiLegReportingType': 'SingleSecurity', 'text': 'Submission from testnet.bitmex.com', 'transactTime': '2020-04-12T19:37:05.828Z', 'timestamp': '2020-04-12T19:37:05.828Z'}]


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
"affiliate",   // Affiliate status, such as total referred users & payout % - push refreshed
"execution",   // Individual executions; can be multiple per order
"order",       // Live updates on your orders
"margin",      // Updates on your current account balance and margin requirements
"position",    // Updates on your positions
"privateNotifications", // Individual notifications - currently not used
"transact",    // Deposit/Withdrawal updates
"wallet"       // Bitcoin address balance data, including total deposits & withdrawals - continuous push overwrite
```


