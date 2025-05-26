//@version=6
strategy("Thank You, Hashem! (BTCUSDT Optimized)", overlay=true, default_qty_type=strategy.fixed, default_qty_value=1)

// === INPUTS === //
useFix1 = input.bool(true, title="✅ Use Fix 1: Early Price Momentum Entry")
useFix2 = input.bool(true, title="✅ Use Fix 2: Adaptive SL/TP")
useFix3 = input.bool(true, title="✅ Use Fix 3: EMA Slope TrendDir")

fastEMA_len     = input.int(8, title="Fast EMA Length")
slowEMA_len     = input.int(21, title="Slow EMA Length")
atrLen          = input.int(14, title="ATR Length")
supertrend_mult = input.float(1.5, title="Supertrend ATR Mult (Fallback)")
fixedSL_ATR     = input.float(0.9, title="Fixed SL ATR (if Fix2 Off)")
trailTP_ATR     = input.float(2.8, title="Trail TP ATR (if Fix2 Off)")
minProfitPerc   = input.float(0.4, title="Minimum Profit % Before Trail", minval=0.1)

// === CALCULATIONS === //
fastEMA = ta.ema(close, fastEMA_len)
slowEMA = ta.ema(close, slowEMA_len)
atr = ta.atr(atrLen)

emaSlope = slowEMA - slowEMA[1]
trendDir_ema = emaSlope > 0 ? 1 : -1

hl2 = (high + low) / 2
upperBand = hl2 + supertrend_mult * atr
lowerBand = hl2 - supertrend_mult * atr

var float finalUpperBand = na
var float finalLowerBand = na
var int trendDir_super = 1

finalUpperBand := na(finalUpperBand[1]) ? upperBand : (close[1] > finalUpperBand[1] ? math.max(upperBand, finalUpperBand[1]) : upperBand)
finalLowerBand := na(finalLowerBand[1]) ? lowerBand : (close[1] < finalLowerBand[1] ? math.min(lowerBand, finalLowerBand[1]) : lowerBand)

trendDir_super := na(trendDir_super[1]) ? 1 :
     trendDir_super[1] == -1 and close > finalUpperBand[1] ? 1 :
     trendDir_super[1] == 1 and close < finalLowerBand[1] ? -1 : trendDir_super[1]

trendDir = useFix3 ? trendDir_ema : trendDir_super

// === ENTRY CONDITIONS === //
fix1Long   = close > fastEMA and fastEMA > slowEMA and close > close[1]
fix1Short  = close < fastEMA and fastEMA < slowEMA and close < close[1]
classicLong = ta.crossover(fastEMA, slowEMA)
classicShort = ta.crossunder(fastEMA, slowEMA)

momentumBoostLong  = fix1Long and close > close[2]
momentumBoostShort = fix1Short and close < close[2]

longCondition  = (useFix1 ? (fix1Long or momentumBoostLong) : classicLong) and trendDir == 1
shortCondition = (useFix1 ? (fix1Short or momentumBoostShort) : classicShort) and trendDir == -1

// === STOPS AND TRAILS === //
stopMult  = useFix2 ? (trendDir == 1 ? 1.2 : 1.0) : fixedSL_ATR
trailMult = useFix2 ? (trendDir == 1 ? 2.6 : 2.0) : trailTP_ATR

long_stop  = close - atr * stopMult
short_stop = close + atr * stopMult

trail_min_offset = close * (minProfitPerc / 100)
long_trail  = math.max(close + atr * trailMult, close + trail_min_offset)
short_trail = math.min(close - atr * trailMult, close - trail_min_offset)

// === POSITION STATE TRACKER === //
var string lastPosition = "none"

// === STRATEGY EXECUTION === //
if barstate.isconfirmed
    if longCondition and lastPosition != "long"
        strategy.entry("Long", strategy.long)
        alert('{"actions": ["close", "buy"]}', alert.freq_once_per_bar)
        lastPosition := "long"

    if shortCondition and lastPosition != "short"
        strategy.entry("Short", strategy.short)
        alert('{"actions": ["close", "sell"]}', alert.freq_once_per_bar)
        lastPosition := "short"

    if strategy.position_size == 0
        lastPosition := "none"

// === EXIT STRATEGY === //
strategy.exit("Long Exit", from_entry="Long", stop=long_stop, trail_price=long_trail, trail_offset=atr)
strategy.exit("Short Exit", from_entry="Short", stop=short_stop, trail_price=short_trail, trail_offset=atr)

// === VISUALS === //
plot(fastEMA, color=color.orange, title="Fast EMA")
plot(slowEMA, color=color.blue, title="Slow EMA")
