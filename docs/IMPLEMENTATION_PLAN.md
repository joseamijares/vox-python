# VOX System Rebuild — Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.  
> **Goal:** Fix critical bugs, build grading engine, add tests, stabilize system  
> **Timeline:** 2-3 weeks  
> **Priority:** P0 (critical) → P1 (important) → P2 (nice to have)

---

## Phase 0: Foundation (Day 1)

### Task 0.1: Fix .env file
**Objective:** Replace truncated Supabase key with full key

**Files:**
- Modify: `.env`

**Step 1: Write correct .env**
```bash
SUPABASE_URL=https://msvcrlijclhuifdjjmyy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zdmNybGlqY2xodWlmZGpqbXl5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTc5OTk2NiwiZXhwIjoyMDk1Mzc1OTY2fQ.RVGnYGVr88ZXNddPaiBJrRGg9knoVNKVeq8QqT5o7G8
POLYGON_API_KEY=your_polygon_key
FINNHUB_API_KEY=your_finnhub_key
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Step 2: Verify connection**
```bash
cd /Users/jos/dev/vox-python
python -c "from supabase import create_client; c = create_client('https://msvcrlijclhuifdjjmyy.supabase.co', 'eyJhbG...'); print('OK')"
```

**Step 3: Commit**
```bash
git add .env
git commit -m "fix: update supabase key"
```

---

### Task 0.2: Fix requirements.txt
**Objective:** Fix malformed dependency line

**Files:**
- Modify: `requirements.txt`

**Step 1: Write correct requirements.txt**
```
streamlit==1.50.0
supabase==2.30.0
plotly==6.7.0
pandas==2.3.3
requests==2.32.5
python-dotenv==1.2.1
python-binance==1.0.36
pydantic==2.11.0
pytest==8.4.0
pytest-cov==6.1.0
yfinance==0.2.65
```

**Step 2: Install and verify**
```bash
pip install -r requirements.txt
```

**Step 3: Commit**
```bash
git add requirements.txt
git commit -m "fix: correct requirements.txt formatting"
```

---

### Task 0.3: Create directory structure
**Objective:** Set up proper project layout

**Files:**
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `src/models.py`
- Create: `src/database.py`
- Create: `src/grading/__init__.py`
- Create: `src/sync/__init__.py`
- Create: `src/pricing/__init__.py`
- Create: `src/alerts/__init__.py`
- Create: `src/dashboard/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `scripts/run_sync.py`
- Create: `scripts/run_grader.py`

**Step 1: Create directories**
```bash
cd /Users/jos/dev/vox-python
mkdir -p src/{grading,sync,pricing,alerts,dashboard} tests scripts docs
```

**Step 2: Create __init__.py files**
```bash
touch src/__init__.py src/grading/__init__.py src/sync/__init__.py \
      src/pricing/__init__.py src/alerts/__init__.py src/dashboard/__init__.py \
      tests/__init__.py
```

**Step 3: Create config.py**
```python
"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # APIs
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET = os.getenv("BINANCE_SECRET", "")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / ".hermes" / "scripts"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Return list of missing required configs."""
        missing = []
        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")
        return missing
```

**Step 4: Create models.py**
```python
"""Pydantic models for data validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class Position(BaseModel):
    """Portfolio position."""
    ticker: str = Field(..., min_length=1, max_length=20)
    name: Optional[str] = None
    shares: Decimal = Field(default=0, ge=0)
    avg_cost: Decimal = Field(default=0, ge=0)
    live_price: Decimal = Field(default=0, ge=0)
    live_value: Decimal = Field(default=0, ge=0)
    grade: int = Field(default=0, ge=0, le=100)
    council: Optional[str] = None
    brokers: List[str] = Field(default_factory=list)
    sector: Optional[str] = None
    asset_type: str = Field(default="stock", pattern="^(stock|crypto|etf|option)$")
    pnl_pct: Optional[float] = None
    updated_at: Optional[datetime] = None
    
    @field_validator("council")
    @classmethod
    def validate_council(cls, v):
        if v and v not in {"STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"}:
            raise ValueError(f"Invalid council: {v}")
        return v

class WatchlistItem(BaseModel):
    """Watchlist entry."""
    ticker: str = Field(..., min_length=1, max_length=20)
    name: Optional[str] = None
    sector: Optional[str] = None
    thesis: Optional[str] = None
    entry_price: Optional[Decimal] = None
    target_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    grade: int = Field(default=0, ge=0, le=100)
    council: Optional[str] = None
    status: str = Field(default="watching", pattern="^(watching|researching|ready|paused|delisted)$")
    sources: List[str] = Field(default_factory=list)
    added_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    notes: Optional[str] = None

class GradeResult(BaseModel):
    """Grading engine output."""
    ticker: str
    overall_grade: int = Field(..., ge=0, le=100)
    technical_score: int = Field(..., ge=0, le=100)
    fundamental_score: int = Field(..., ge=0, le=100)
    sentiment_score: int = Field(..., ge=0, le=100)
    momentum_score: int = Field(..., ge=0, le=100)
    risk_score: int = Field(..., ge=0, le=100)
    council: str
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    factors: dict = Field(default_factory=dict)
```

**Step 5: Create database.py**
```python
"""Supabase database client."""
from supabase import create_client, Client
from .config import Config

_client: Client | None = None

def get_client() -> Client:
    """Get or create Supabase client."""
    global _client
    if _client is None:
        missing = Config.validate()
        if missing:
            raise RuntimeError(f"Missing config: {', '.join(missing)}")
        _client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    return _client

def reset_client():
    """Reset client (for testing)."""
    global _client
    _client = None
```

**Step 6: Commit**
```bash
git add src/ tests/ scripts/ docs/
git commit -m "feat: create project structure with config, models, database"
```

---

## Phase 1: Grading Engine (Days 2-5)

### Task 1.1: Build technical grader
**Objective:** Calculate technical score from price data

**Files:**
- Create: `src/grading/technical.py`
- Test: `tests/test_technical.py`

**Implementation:**
```python
"""Technical analysis scoring."""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional

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

def score_technical(ticker: str) -> dict:
    """Calculate technical score (0-100)."""
    df = get_stock_data(ticker)
    if df is None:
        return {"score": 50, "rsi": 50, "macd_bullish": False, "trend": 0, "error": "No data"}
    
    prices = df["Close"]
    
    # RSI score (lower RSI = more oversold = higher score)
    rsi = calculate_rsi(prices)
    rsi_score = max(0, min(100, 100 - rsi))
    
    # MACD score
    macd, signal = calculate_macd(prices)
    macd_score = 70 if macd > signal else 30
    
    # Trend score
    trend = calculate_sma_trend(prices)
    trend_score = int((trend + 1) * 50)
    
    # Volume trend
    volume_sma = df["Volume"].rolling(20).mean().iloc[-1]
    recent_volume = df["Volume"].iloc[-5:].mean()
    volume_score = 60 if recent_volume > volume_sma else 40
    
    # Combined
    score = int(rsi_score * 0.3 + macd_score * 0.25 + trend_score * 0.3 + volume_score * 0.15)
    
    return {
        "score": score,
        "rsi": round(rsi, 2),
        "macd_bullish": macd > signal,
        "trend": trend,
        "volume_trend": "up" if recent_volume > volume_sma else "down"
    }
```

**Test:**
```python
"""Tests for technical grader."""
import pytest
from src.grading.technical import score_technical, calculate_rsi

def test_score_technical_returns_dict():
    result = score_technical("AAPL")
    assert isinstance(result, dict)
    assert "score" in result
    assert 0 <= result["score"] <= 100

def test_score_technical_invalid_ticker():
    result = score_technical("INVALID_TICKER_12345")
    assert result["score"] == 50
    assert "error" in result
```

**Step 5: Commit**
```bash
git add src/grading/technical.py tests/test_technical.py
git commit -m "feat: add technical analysis grader"
```

---

### Task 1.2: Build fundamental grader
**Objective:** Calculate fundamental score from financial data

**Files:**
- Create: `src/grading/fundamental.py`
- Test: `tests/test_fundamental.py`

**Implementation:**
```python
"""Fundamental analysis scoring."""
import requests
from typing import Optional
from src.config import Config

def get_finnhub_data(ticker: str) -> dict:
    """Fetch fundamental data from Finnhub."""
    api_key = Config.FINNHUB_API_KEY
    if not api_key:
        return {}
    
    try:
        url = f"https://finnhub.io/api/v1/stock/metric"
        params = {"symbol": ticker, "metric": "all", "token": api_key}
        response = requests.get(url, params=params, timeout=10)
        return response.json() if response.status_code == 200 else {}
    except Exception:
        return {}

def score_fundamental(ticker: str) -> dict:
    """Calculate fundamental score (0-100)."""
    data = get_finnhub_data(ticker)
    metrics = data.get("metric", {})
    
    if not metrics:
        return {"score": 50, "error": "No data"}
    
    # P/E ratio (lower is better, but not too low)
    pe = metrics.get("peTTM", metrics.get("peNormalizedAnnual", 0))
    pe_score = 70 if 10 <= pe <= 25 else 50 if pe > 0 else 30
    
    # Revenue growth
    growth = metrics.get("revenueGrowth", 0)
    growth_score = min(100, max(0, int(growth * 10 + 50)))
    
    # Profit margin
    margin = metrics.get("netMargin", 0)
    margin_score = min(100, max(0, int(margin * 200 + 50)))
    
    # Debt/Equity
    de = metrics.get("totalDebt/totalEquity", 0)
    de_score = 80 if de < 0.5 else 60 if de < 1 else 40
    
    # ROE
    roe = metrics.get("roe", 0)
    roe_score = min(100, max(0, int(roe * 100 + 30)))
    
    score = int(pe_score * 0.2 + growth_score * 0.3 + margin_score * 0.2 + de_score * 0.15 + roe_score * 0.15)
    
    return {
        "score": score,
        "pe": pe,
        "revenue_growth": growth,
        "net_margin": margin,
        "debt_equity": de,
        "roe": roe
    }
```

**Step 4: Commit**
```bash
git add src/grading/fundamental.py tests/test_fundamental.py
git commit -m "feat: add fundamental analysis grader"
```

---

### Task 1.3: Build grading engine orchestrator
**Objective:** Combine all scoring modules into final grade

**Files:**
- Create: `src/grading/engine.py`
- Test: `tests/test_engine.py`

**Implementation:**
```python
"""Grading engine — combines all scoring modules."""
from .technical import score_technical
from .fundamental import score_fundamental
from src.models import GradeResult
from typing import Optional

def calculate_grade(ticker: str, use_fundamental: bool = True) -> GradeResult:
    """Calculate overall grade for a stock."""
    
    # Technical score
    tech = score_technical(ticker)
    technical_score = tech["score"]
    
    # Fundamental score
    if use_fundamental:
        fund = score_fundamental(ticker)
        fundamental_score = fund["score"]
    else:
        fundamental_score = 50
        fund = {}
    
    # Placeholder for sentiment and momentum (Phase 2)
    sentiment_score = 50
    momentum_score = 50
    
    # Risk score (inverse of volatility — placeholder)
    risk_score = 50
    
    # Weighted average
    overall = int(
        technical_score * 0.25 +
        fundamental_score * 0.25 +
        sentiment_score * 0.20 +
        momentum_score * 0.20 +
        risk_score * 0.10
    )
    
    # Determine council signal
    council = grade_to_council(overall)
    
    return GradeResult(
        ticker=ticker,
        overall_grade=overall,
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        sentiment_score=sentiment_score,
        momentum_score=momentum_score,
        risk_score=risk_score,
        council=council,
        factors={
            "technical": tech,
            "fundamental": fund,
            "sentiment": {"score": sentiment_score},
            "momentum": {"score": momentum_score},
            "risk": {"score": risk_score}
        }
    )

def grade_to_council(grade: int) -> str:
    """Convert numeric grade to council signal."""
    if grade >= 90:
        return "STRONG_BUY"
    elif grade >= 75:
        return "BUY"
    elif grade >= 50:
        return "HOLD"
    elif grade >= 25:
        return "SELL"
    else:
        return "STRONG_SELL"

def batch_grade(tickers: list[str]) -> list[GradeResult]:
    """Grade multiple stocks."""
    results = []
    for ticker in tickers:
        try:
            result = calculate_grade(ticker)
            results.append(result)
        except Exception as e:
            results.append(GradeResult(
                ticker=ticker,
                overall_grade=0,
                technical_score=0,
                fundamental_score=0,
                sentiment_score=0,
                momentum_score=0,
                risk_score=0,
                council="ERROR",
                factors={"error": str(e)}
            ))
    return results
```

**Step 3: Commit**
```bash
git add src/grading/engine.py tests/test_engine.py
git commit -m "feat: add grading engine orchestrator"
```

---

### Task 1.4: Build grade sync script
**Objective:** Recalculate all grades and update Supabase

**Files:**
- Create: `scripts/run_grader.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""Recalculate grades for all watchlist stocks."""
import sys
sys.path.insert(0, "/Users/jos/dev/vox-python/src")

from src.database import get_client
from src.grading.engine import batch_grade
from src.models import GradeResult
from datetime import datetime

def main():
    sb = get_client()
    
    # Get all watchlist tickers
    response = sb.table("watchlist").select("ticker").execute()
    tickers = [r["ticker"] for r in response.data]
    
    print(f"Grading {len(tickers)} stocks...")
    
    # Calculate grades in batches
    batch_size = 10
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        results = batch_grade(batch)
        
        # Update watchlist
        for result in results:
            sb.table("watchlist").update({
                "grade": result.overall_grade,
                "council": result.council,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("ticker", result.ticker).execute()
            
            # Save to grades history
            sb.table("grades").insert({
                "ticker": result.ticker,
                "overall_grade": result.overall_grade,
                "technical_score": result.technical_score,
                "fundamental_score": result.fundamental_score,
                "sentiment_score": result.sentiment_score,
                "momentum_score": result.momentum_score,
                "risk_score": result.risk_score,
                "council": result.council,
                "calculated_at": datetime.utcnow().isoformat(),
                "factors": result.factors
            }).execute()
            
            print(f"  {result.ticker}: Grade {result.overall_grade} ({result.council})")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
```

**Step 2: Make executable and test**
```bash
chmod +x scripts/run_grader.py
python scripts/run_grader.py
```

**Step 3: Commit**
```bash
git add scripts/run_grader.py
git commit -m "feat: add grade recalculation script"
```

---

## Phase 2: Data Pipeline Fixes (Days 6-8)

### Task 2.1: Mark delisted stocks
**Objective:** Find and mark dead stocks in watchlist

**Files:**
- Create: `scripts/cleanup_watchlist.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""Clean up watchlist — mark delisted stocks."""
import sys
sys.path.insert(0, "/Users/jos/dev/vox-python/src")

from src.database import get_client
import yfinance as yf

def check_ticker(ticker: str) -> dict:
    """Check if ticker is valid and active."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "valid": True,
            "delisted": info.get("regularMarketPrice") is None and info.get("currentPrice") is None,
            "name": info.get("longName", info.get("shortName", ticker))
        }
    except Exception as e:
        return {"valid": False, "delisted": True, "error": str(e)}

def main():
    sb = get_client()
    
    # Get all watchlist items
    response = sb.table("watchlist").select("ticker").execute()
    tickers = [r["ticker"] for r in response.data]
    
    print(f"Checking {len(tickers)} tickers...")
    
    for ticker in tickers:
        result = check_ticker(ticker)
        
        if result.get("delisted") or not result["valid"]:
            print(f"  ⚠️ {ticker}: DELISTED — marking")
            sb.table("watchlist").update({
                "status": "delisted",
                "grade": 0,
                "council": "STRONG_SELL"
            }).eq("ticker", ticker).execute()
        else:
            print(f"  ✅ {ticker}: OK")
    
    print("\nCleanup complete!")

if __name__ == "__main__":
    main()
```

**Step 3: Commit**
```bash
git add scripts/cleanup_watchlist.py
git commit -m "feat: add watchlist cleanup for delisted stocks"
```

---

### Task 2.2: Refactor sync scripts
**Objective:** Move sync logic to `src/sync/` package

**Files:**
- Create: `src/sync/base.py`
- Create: `src/sync/gbm.py`
- Modify: `gbm_sync.py` → deprecate, call new module

**Implementation (base.py):**
```python
"""Base broker sync interface."""
from abc import ABC, abstractmethod
from typing import List
from src.models import Position

class BrokerSync(ABC):
    """Abstract base class for broker sync."""
    
    broker_name: str = ""
    
    @abstractmethod
    def fetch_positions(self) -> List[Position]:
        """Fetch positions from broker."""
        pass
    
    @abstractmethod
    def normalize_position(self, raw: dict) -> Position:
        """Convert broker format to Position model."""
        pass
    
    def sync_to_supabase(self):
        """Sync positions to Supabase."""
        from src.database import get_client
        sb = get_client()
        
        positions = self.fetch_positions()
        
        for pos in positions:
            # Upsert logic
            existing = sb.table("positions").select("*").eq("ticker", pos.ticker).execute()
            
            if existing.data:
                old_brokers = existing.data[0].get("brokers", []) or []
                new_brokers = list(set(old_brokers + [self.broker_name]))
                
                sb.table("positions").update({
                    "shares": float(pos.shares),
                    "avg_cost": float(pos.avg_cost),
                    "live_price": float(pos.live_price),
                    "live_value": float(pos.live_value),
                    "brokers": new_brokers,
                    "updated_at": "now()"
                }).eq("ticker", pos.ticker).execute()
            else:
                sb.table("positions").insert({
                    "ticker": pos.ticker,
                    "shares": float(pos.shares),
                    "avg_cost": float(pos.avg_cost),
                    "live_price": float(pos.live_price),
                    "live_value": float(pos.live_value),
                    "brokers": [self.broker_name],
                    "updated_at": "now()"
                }).execute()
```

**Step 3: Commit**
```bash
git add src/sync/base.py src/sync/gbm.py
git commit -m "refactor: extract sync base class and GBM sync"
```

---

## Phase 3: Testing & CI (Days 9-10)

### Task 3.1: Add pytest configuration
**Objective:** Set up test runner with coverage

**Files:**
- Create: `pytest.ini`
- Create: `.github/workflows/ci.yml`

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

**ci.yml:**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
```

**Step 3: Commit**
```bash
git add pytest.ini .github/workflows/ci.yml
git commit -m "ci: add pytest and GitHub Actions"
```

---

### Task 3.2: Write comprehensive tests
**Objective:** Test all core modules

**Files:**
- Create: `tests/test_models.py`
- Create: `tests/test_database.py`
- Create: `tests/test_sync.py`

**test_models.py:**
```python
"""Tests for Pydantic models."""
import pytest
from decimal import Decimal
from src.models import Position, WatchlistItem, GradeResult

def test_position_valid():
    pos = Position(ticker="AAPL", shares=Decimal("100"), avg_cost=Decimal("150.50"))
    assert pos.ticker == "AAPL"
    assert pos.shares == 100

def test_position_invalid_grade():
    with pytest.raises(ValueError):
        Position(ticker="AAPL", grade=101)

def test_watchlist_invalid_status():
    with pytest.raises(ValueError):
        WatchlistItem(ticker="AAPL", status="invalid")

def test_grade_result_council_mapping():
    from src.grading.engine import grade_to_council
    assert grade_to_council(95) == "STRONG_BUY"
    assert grade_to_council(80) == "BUY"
    assert grade_to_council(60) == "HOLD"
    assert grade_to_council(30) == "SELL"
    assert grade_to_council(10) == "STRONG_SELL"
```

**Step 2: Run tests**
```bash
pytest tests/ -v
```

**Step 3: Commit**
```bash
git add tests/
git commit -m "test: add comprehensive test suite"
```

---

## Phase 4: Price Updater (Days 11-12)

### Task 4.1: Build price updater
**Objective:** Fetch live prices and update Supabase

**Files:**
- Create: `src/pricing/sources.py`
- Create: `src/pricing/updater.py`
- Create: `scripts/run_pricer.py`

**sources.py:**
```python
"""Price data sources."""
import requests
from typing import Optional
from src.config import Config

def get_polygon_price(ticker: str) -> Optional[float]:
    """Get latest price from Polygon.io."""
    api_key = Config.POLYGON_API_KEY
    if not api_key:
        return None
    
    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
        response = requests.get(url, params={"apiKey": api_key}, timeout=10)
        data = response.json()
        if data.get("results"):
            return data["results"][0]["c"]
    except Exception:
        pass
    return None

def get_binance_price(symbol: str) -> Optional[float]:
    """Get crypto price from Binance."""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, params={"symbol": symbol.upper() + "USDT"}, timeout=10)
        data = response.json()
        return float(data.get("price", 0))
    except Exception:
        return None
```

**updater.py:**
```python
"""Price update orchestrator."""
from src.database import get_client
from src.pricing.sources import get_polygon_price, get_binance_price
from datetime import datetime

def update_all_prices():
    """Update prices for all positions."""
    sb = get_client()
    
    # Get all positions
    response = sb.table("positions").select("ticker,asset_type").execute()
    positions = response.data
    
    updated = 0
    for pos in positions:
        ticker = pos["ticker"]
        asset_type = pos.get("asset_type", "stock")
        
        if asset_type == "crypto":
            price = get_binance_price(ticker)
        else:
            price = get_polygon_price(ticker)
        
        if price:
            # Update position
            sb.table("positions").update({
                "live_price": price,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("ticker", ticker).execute()
            
            # Save to history
            sb.table("price_history").insert({
                "ticker": ticker,
                "price": price,
                "source": "binance" if asset_type == "crypto" else "polygon",
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
            
            updated += 1
            print(f"  ✅ {ticker}: ${price}")
        else:
            print(f"  ❌ {ticker}: No price")
    
    print(f"\nUpdated {updated}/{len(positions)} prices")
```

**Step 3: Commit**
```bash
git add src/pricing/ scripts/run_pricer.py
git commit -m "feat: add price updater with Polygon and Binance"
```

---

## Phase 5: Alert System (Days 13-14)

### Task 5.1: Build alert engine
**Objective:** Monitor conditions and send alerts

**Files:**
- Create: `src/alerts/engine.py`
- Create: `src/alerts/telegram.py`
- Create: `scripts/run_alerts.py`

**engine.py:**
```python
"""Alert engine — monitors conditions and triggers alerts."""
from src.database import get_client
from datetime import datetime, timedelta
from typing import List, Dict

class AlertEngine:
    """Monitor portfolio conditions and generate alerts."""
    
    def __init__(self):
        self.sb = get_client()
        self.alerts_today = 0
        self.max_alerts_per_day = 3
    
    def check_stop_losses(self) -> List[Dict]:
        """Check if any positions hit stop loss."""
        alerts = []
        
        # Get positions with stop losses
        response = self.sb.table("watchlist").select("ticker,stop_loss").not_eq("stop_loss", 0).execute()
        stops = {r["ticker"]: r["stop_loss"] for r in response.data}
        
        # Get current prices
        positions = self.sb.table("positions").select("ticker,live_price").execute().data
        
        for pos in positions:
            ticker = pos["ticker"]
            price = pos["live_price"]
            stop = stops.get(ticker)
            
            if stop and price <= stop:
                alerts.append({
                    "type": "stop_loss",
                    "ticker": ticker,
                    "message": f"🛑 {ticker} hit stop loss at ${stop} (current: ${price})"
                })
        
        return alerts
    
    def check_daily_moves(self, threshold: float = 0.10) -> List[Dict]:
        """Check for large daily moves."""
        alerts = []
        
        # Get yesterday's prices
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        positions = self.sb.table("positions").select("ticker,live_price,avg_cost").execute().data
        
        for pos in positions:
            ticker = pos["ticker"]
            current = pos["live_price"]
            cost = pos["avg_cost"]
            
            if cost > 0:
                change = (current - cost) / cost
                if abs(change) >= threshold:
                    direction = "📈" if change > 0 else "📉"
                    alerts.append({
                        "type": "daily_move",
                        "ticker": ticker,
                        "message": f"{direction} {ticker} moved {change*100:.1f}% today"
                    })
        
        return alerts
    
    def run(self):
        """Run all alert checks."""
        if self.alerts_today >= self.max_alerts_per_day:
            print("Max alerts reached for today")
            return []
        
        all_alerts = []
        all_alerts.extend(self.check_stop_losses())
        all_alerts.extend(self.check_daily_moves())
        
        # Deduplicate (check if already sent today)
        new_alerts = []
        for alert in all_alerts:
            if not self._already_sent(alert["ticker"], alert["type"]):
                new_alerts.append(alert)
                self._mark_sent(alert)
                self.alerts_today += 1
                
                if self.alerts_today >= self.max_alerts_per_day:
                    break
        
        return new_alerts
    
    def _already_sent(self, ticker: str, alert_type: str) -> bool:
        """Check if alert was already sent today."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        response = self.sb.table("alerts").select("*").eq("ticker", ticker).eq("type", alert_type).like("sent_at", f"{today}%").execute()
        return len(response.data) > 0
    
    def _mark_sent(self, alert: Dict):
        """Mark alert as sent."""
        self.sb.table("alerts").insert({
            "ticker": alert["ticker"],
            "type": alert["type"],
            "message": alert["message"],
            "sent_at": datetime.utcnow().isoformat()
        }).execute()
```

**Step 3: Commit**
```bash
git add src/alerts/ scripts/run_alerts.py
git commit -m "feat: add alert engine with stop loss and daily move checks"
```

---

## Phase 6: Documentation (Day 15)

### Task 6.1: Write README
**Objective:** Complete project documentation

**Files:**
- Create: `README.md`

**Content:**
```markdown
# VOX Portfolio Intelligence

Multi-broker portfolio tracker with AI-powered stock grading.

## Features

- 📊 **Multi-Broker Sync**: eToro, GBM, Binance, IBKR, Schwab, Bitso
- 🎯 **Stock Grading**: 0-100 score based on technical, fundamental, sentiment
- 📈 **Real-Time Prices**: Polygon.io + Binance APIs
- 🚨 **Smart Alerts**: Stop losses, daily moves, news triggers
- 🖥️ **Dashboard**: Streamlit web interface

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd vox-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run sync
python scripts/run_sync.py

# Recalculate grades
python scripts/run_grader.py

# Start dashboard
streamlit run src/dashboard/app.py
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Testing

```bash
pytest tests/ -v --cov=src
```

## Deployment

### Railway
```bash
railway login
railway up
```

## License

MIT
```

**Step 2: Commit**
```bash
git add README.md
git commit -m "docs: add comprehensive README"
```

---

## Summary

| Phase | Tasks | Duration | Deliverable |
|-------|-------|----------|-------------|
| 0 | 3 tasks | Day 1 | Fixed .env, requirements, structure |
| 1 | 4 tasks | Days 2-5 | Working grading engine |
| 2 | 2 tasks | Days 6-8 | Clean data pipeline |
| 3 | 2 tasks | Days 9-10 | Test suite + CI |
| 4 | 1 task | Days 11-12 | Price updater |
| 5 | 1 task | Days 13-14 | Alert system |
| 6 | 1 task | Day 15 | Documentation |

**Total: 14 tasks, ~15 days**

---

Ready to execute. Shall I start with Phase 0?
