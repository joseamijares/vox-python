"""Technical analysis scoring using yfinance."""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict

def get_stock_data(ticker: str, period: str = "6mo") -> Optional[pd.DataFrame]:
    """Fetch historical price data."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        return df if not df.empty else None
    except Exception:
        return None

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate RSI (0-100)."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

def calculate_macd(prices: pd.Series) -> tuple[float, float]:
    """Calculate MACD and signal line."""
    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd.iloc[-1], signal.iloc[-1]

def calculate_sma_trend(prices: pd.Series) -> float:
    """Calculate SMA trend score (-1 to 1)."""
    if len(prices) < 50:
        return 0.0
    sma20 = prices.rolling(20).mean().iloc[-1]
    sma50 = prices.rolling(50).mean().iloc[-1]
    current = prices.iloc[-1]
    
    if current > sma20 > sma50:
        return 1.0
    elif current > sma20:
        return 0.5
    elif current < sma20 < sma50:
        return -1.0
    elif current < sma20:
        return -0.5
    return 0.0

def score_technical(ticker: str) -> Dict:
    """Calculate technical score (0-100)."""
    df = get_stock_data(ticker)
    if df is None or len(df) < 50:
        return {"score": 50, "rsi": 50, "macd_bullish": False, "trend": 0, "volume_trend": "neutral", "error": "No data"}
    
    prices = df["Close"]
    
    # RSI score (lower RSI = more oversold = higher score for contrarian, but momentum matters)
    rsi = calculate_rsi(prices)
    # RSI 30-50 is bullish zone (recovering from oversold)
    # RSI 50-70 is strong momentum
    if 40 <= rsi <= 60:
        rsi_score = 70  # Sweet spot
    elif 30 <= rsi < 40 or 60 < rsi <= 70:
        rsi_score = 60
    elif rsi < 30:
        rsi_score = 80  # Oversold bounce potential
    else:
        rsi_score = 40  # Overbought
    
    # MACD score
    macd, signal = calculate_macd(prices)
    macd_score = 75 if macd > signal else 35
    
    # Trend score
    trend = calculate_sma_trend(prices)
    trend_score = int((trend + 1) * 50)
    
    # Volume trend
    if len(df) >= 25:
        volume_sma = df["Volume"].rolling(20).mean().iloc[-1]
        recent_volume = df["Volume"].iloc[-5:].mean()
        volume_score = 65 if recent_volume > volume_sma else 45
        volume_trend = "up" if recent_volume > volume_sma else "down"
    else:
        volume_score = 50
        volume_trend = "neutral"
    
    # Combined
    score = int(rsi_score * 0.25 + macd_score * 0.25 + trend_score * 0.30 + volume_score * 0.20)
    
    return {
        "score": max(0, min(100, score)),
        "rsi": round(rsi, 2),
        "macd_bullish": macd > signal,
        "trend": trend,
        "volume_trend": volume_trend
    }

if __name__ == "__main__":
    # Test
    print(score_technical("AAPL"))
