# VOX System Architecture

> **Version:** 1.0.0  
> **Last Updated:** 2026-05-29  
> **Status:** CRITICAL — Grade system broken, data pipeline incomplete

---

## 1. System Overview

VOX is a multi-broker portfolio intelligence system that aggregates positions from 7 brokers, grades stocks on a 0-100 scale, and provides buy/sell recommendations through a Streamlit dashboard.

### Current State (BROKEN)
- ✅ Supabase database connected
- ✅ Broker sync scripts (5 files, partial)
- ✅ Streamlit dashboard (deployed to Railway)
- ❌ **NO grade calculation engine** — grades are stale/manual
- ❌ **NO test suite** — zero tests
- ❌ **NO documentation** — zero docs
- ❌ **Broken data pipeline** — delisted stocks still graded, real stocks show Grade 0
- ❌ **Supabase key truncated** in .env file

### Target State
- ✅ Multi-factor grading engine (technical + fundamental + sentiment)
- ✅ Automated data pipeline with validation
- ✅ Comprehensive test suite (>80% coverage)
- ✅ Real-time price updates
- ✅ Alert system
- ✅ Clean architecture with separation of concerns

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│   eToro     │  GBM Main   │  GBM USA    │  Binance    │  IBKR/Schwab/Bitso  │
│   (API)     │  (JSON)     │  (JSON)     │   (API)     │     (JSON)          │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │             │                 │
       └─────────────┴─────────────┴─────────────┴─────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     SYNC LAYER (5 scripts)   │
                    │  • etoro_sync.py             │
                    │  • gbm_sync.py               │
                    │  • binance_sync.py           │
                    │  • remaining_sync.py         │
                    │  • vox_supabase_sync.py      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      SUPABASE (PostgreSQL)   │
                    │  ┌─────────────────────────┐ │
                    │  │  positions              │ │
                    │  │  watchlist              │ │
                    │  │  plays                  │ │
                    │  │  price_history          │ │
                    │  │  alerts                 │ │
                    │  │  grades                 │ │
                    │  └─────────────────────────┘ │
                    └──────────────┬──────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
┌──────▼──────┐         ┌──────────▼──────────┐    ┌───────────▼──────────┐
│   GRADING   │         │   PRICE UPDATER     │    │    ALERT ENGINE      │
│   ENGINE    │         │   (15-min cron)     │    │    (event-driven)    │
│             │         │                     │    │                      │
│ • Technical │         │ • Polygon.io API    │    │ • Stop loss hits     │
│ • Fundamental│        │ • Binance API       │    │ • >10% daily moves   │
│ • Sentiment │         │ • Update Supabase   │    │ • News triggers      │
│ • Risk      │         │ • Cache validation  │    │ • Telegram notify    │
└──────┬──────┘         └─────────────────────┘    └──────────────────────┘
       │
       └──────────────────────────────────────────────────────────────┐
                                                                      │
                    ┌─────────────────────────────────────────────────▼──────┐
                    │              STREAMLIT DASHBOARD                        │
                    │  ┌─────────────┬─────────────┬──────────────────────┐  │
                    │  │  Portfolio  │  Watchlist  │    Plays/Alerts      │  │
                    │  │  Overview   │  Grades     │    Council Review    │  │
                    │  └─────────────┴─────────────┴──────────────────────┘  │
                    └────────────────────────────────────────────────────────┘
```

---

## 3. Data Model

### 3.1 Positions Table
```sql
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    shares DECIMAL(20,8) NOT NULL DEFAULT 0,
    avg_cost DECIMAL(20,8) NOT NULL DEFAULT 0,
    live_price DECIMAL(20,8) NOT NULL DEFAULT 0,
    live_value DECIMAL(20,2) NOT NULL DEFAULT 0,
    grade INTEGER CHECK (grade >= 0 AND grade <= 100),
    council VARCHAR(20), -- STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    brokers TEXT[], -- ['eToro', 'GBM Main']
    sector VARCHAR(50),
    asset_type VARCHAR(20), -- stock, crypto, etf, option
    pnl_pct DECIMAL(10,4),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker)
);
```

### 3.2 Watchlist Table
```sql
CREATE TABLE watchlist (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100),
    sector VARCHAR(50),
    thesis TEXT,
    entry_price DECIMAL(20,8),
    target_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    grade INTEGER CHECK (grade >= 0 AND grade <= 100),
    council VARCHAR(20),
    status VARCHAR(20), -- watching, researching, ready, paused, delisted
    sources TEXT[], -- ['reddit', 'trump', 'news', 'x']
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);
```

### 3.3 Grades Table (NEW)
```sql
CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    overall_grade INTEGER CHECK (grade >= 0 AND grade <= 100),
    technical_score INTEGER,
    fundamental_score INTEGER,
    sentiment_score INTEGER,
    momentum_score INTEGER,
    risk_score INTEGER,
    council VARCHAR(20),
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    factors JSONB, -- detailed breakdown
    UNIQUE(ticker, calculated_at)
);
```

### 3.4 Price History Table (NEW)
```sql
CREATE TABLE price_history (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    volume BIGINT,
    source VARCHAR(20), -- polygon, binance, manual
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_price_history_ticker_time ON price_history(ticker, timestamp DESC);
```

---

## 4. Component Design

### 4.1 Sync Layer
**Responsibility:** Pull data from brokers, normalize, write to Supabase

**Current Problems:**
- Each script fetches watchlist grades independently (N+1 queries)
- No validation of incoming data
- No error recovery
- Hardcoded paths

**Fix:**
- Create `vox/sync/` package
- Unified broker interface
- Batch operations
- Data validation with pydantic
- Idempotent writes

### 4.2 Grading Engine (MISSING)
**Responsibility:** Calculate 0-100 grades for all stocks

**Algorithm:**
```
Grade = weighted_average(
    technical_score    * 0.25,
    fundamental_score  * 0.25,
    sentiment_score    * 0.20,
    momentum_score     * 0.20,
    risk_score         * 0.10
)

Council = grade_to_signal(grade):
    90-100: STRONG_BUY
    75-89:  BUY
    50-74:  HOLD
    25-49:  SELL
    0-24:   STRONG_SELL
```

**Data Sources:**
- Technical: Yahoo Finance (RSI, MACD, SMA, volume)
- Fundamental: Finnhub (P/E, growth, margins)
- Sentiment: Custom agents (news, Reddit, Trump)
- Momentum: Price performance vs sector
- Risk: Volatility, beta, max drawdown

### 4.3 Price Updater (MISSING)
**Responsibility:** Update live prices every 15 minutes

**Implementation:**
- Polygon.io for stocks/ETFs
- Binance API for crypto
- Batch requests (max 100 tickers per call)
- Write to `price_history` + update `positions.live_price`

### 4.4 Alert Engine (MISSING)
**Responsibility:** Monitor conditions, send Telegram alerts

**Rules:**
- Stop loss hit: position drops below stop
- Daily move: >10% up/down
- News trigger: high-relevance mention
- Grade change: significant upgrade/downgrade
- Max 3 alerts/day, 24h dedup

---

## 5. File Structure

```
vox-python/
├── README.md
├── requirements.txt
├── .env.example
├── pytest.ini
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── src/
│   ├── __init__.py
│   ├── config.py              # Settings, env vars
│   ├── models.py              # Pydantic models
│   ├── database.py            # Supabase client
│   ├── grading/
│   │   ├── __init__.py
│   │   ├── engine.py          # Main grading logic
│   │   ├── technical.py       # RSI, MACD, etc.
│   │   ├── fundamental.py     # P/E, growth, etc.
│   │   ├── sentiment.py       # News/social scoring
│   │   └── risk.py            # Volatility, drawdown
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract broker class
│   │   ├── etoro.py           # eToro API sync
│   │   ├── gbm.py             # GBM JSON sync
│   │   ├── binance.py         # Binance API sync
│   │   ├── remaining.py       # IBKR/Schwab/Bitso
│   │   └── pipeline.py        # Orchestrator
│   ├── pricing/
│   │   ├── __init__.py
│   │   ├── updater.py         # Price update cron
│   │   └── sources.py         # Polygon, Binance
│   ├── alerts/
│   │   ├── __init__.py
│   │   ├── engine.py          # Alert rules
│   │   └── telegram.py        # Telegram bot
│   └── dashboard/
│       ├── __init__.py
│       └── app.py             # Streamlit app
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_grading.py
│   ├── test_sync.py
│   └── test_pricing.py
└── scripts/
    ├── run_sync.py            # Manual sync trigger
    ├── run_grader.py          # Manual grade recalc
    └── run_alerts.py          # Manual alert check
```

---

## 6. Critical Bugs to Fix

| Priority | Bug | Impact | Fix |
|----------|-----|--------|-----|
| **P0** | No grade calculation engine | All grades stale/meaningless | Build `grading/engine.py` |
| **P0** | Supabase key truncated in .env | Cannot connect to database | Update .env with full key |
| **P0** | LILM delisted but Grade 86 | Recommends bankrupt stock | Add delisted validation |
| **P1** | Grade 0 on real stocks | 29 stocks incorrectly scored | Implement proper grading |
| **P1** | No test suite | Cannot verify changes | Add pytest + CI |
| **P1** | requirements.txt malformed | `python-dotenv==1.2.1python-binance` | Fix formatting |
| **P2** | No price history | Cannot track performance | Add `price_history` table |
| **P2** | No alert system | Miss stop losses, big moves | Build `alerts/engine.py` |
| **P2** | Dashboard reads wrong path | `sys.path.insert(0, '/Users/jos/.hermes/scripts')` | Use relative imports |

---

## 7. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Streamlit | 1.50.0 |
| Database | Supabase (PostgreSQL) | 15+ |
| ORM/Client | supabase-py | 2.30.0 |
| Data | Pandas | 2.3.3 |
| Visualization | Plotly | 6.7.0 |
| Validation | Pydantic | 2.x |
| Testing | pytest | 8.x |
| Linting | ruff | 0.9.x |
| Type Checking | mypy | 1.x |
| Deployment | Railway | latest |
| Price Data | Polygon.io | API v2 |
| Crypto Data | Binance API | REST |
| News Data | Finnhub | API |

---

## 8. Deployment

### Local Development
```bash
git clone <repo>
cd vox-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
streamlit run src/dashboard/app.py
```

### Railway Production
```bash
railway login
railway link
railway variables set SUPABASE_URL=xxx
railway variables set SUPABASE_KEY=xxx
railway up
```

### Cron Jobs (Railway)
- **Price updates:** Every 15 min during market hours
- **Grade recalculation:** Daily at 6 AM ET
- **Alert checks:** Every 5 minutes
- **Full sync:** Daily at 7 AM ET

---

## 9. Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test coverage | 0% | >80% |
| Grade accuracy | ~30% (stale) | >90% |
| Data freshness | Days old | <15 min |
| False alerts | N/A | <5% |
| Delisted stocks in watchlist | 1+ | 0 |
| Documentation | None | Complete |

---

## 10. Next Steps

1. **Fix P0 bugs** (today)
2. **Implement grading engine** (this week)
3. **Add test suite** (this week)
4. **Build price updater** (next week)
5. **Build alert system** (next week)
6. **Refactor dashboard** (next week)
7. **Full deployment** (week 3)

---

*This document is living — update as architecture evolves.*
