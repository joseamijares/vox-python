# VOX Portfolio System v6

**Real-time portfolio tracking, grading, and alerts.**

- **Dashboard:** https://web-production-9e321.up.railway.app/
- **Repo:** https://github.com/joseamijares/vox-python

---

## Quick Start

```bash
# Clone
git clone https://github.com/joseamijares/vox-python.git
cd vox-python

# Install
pip install -r requirements.txt

# Set env
cp .env.example .env
# Edit .env with your Railway Postgres credentials

# Run daily update
python scripts/run_daily_update.py

# Import GBM portfolio
python scripts/import_gbm.py
```

---

## Architecture

```
vox-python/
├── src/
│   ├── grading/          # Stock grading engine
│   │   ├── engine.py     # Main orchestrator
│   │   ├── technical.py  # RSI, MACD, SMA
│   │   ├── fundamental.py # P/E, growth, margins
│   │   └── delisted.py   # Dead stock detection
│   ├── pricing/          # Price updates
│   │   └── updater.py    # Daily price sync
│   ├── alerts/           # Notifications
│   │   └── notifier.py   # Telegram alerts
│   ├── sync/             # Data sync
│   │   ├── vox_postgres_sync.py  # Railway Postgres client
│   │   ├── vox_supabase_sync.py  # Supabase client (legacy)
│   │   ├── gbm_importer.py       # GBM JSON import
│   │   └── validator.py          # Data validation
│   ├── brokers/          # Broker sync scripts
│   │   ├── etoro_sync.py
│   │   ├── binance_sync.py
│   │   ├── gbm_sync.py
│   │   └── remaining_sync.py
│   └── dashboard/        # Streamlit UI (legacy)
│       └── vox_dashboard.py
├── scripts/              # CLI runners
│   ├── run_daily_update.py
│   ├── run_grader.py
│   ├── import_gbm.py
│   └── fix_delisted.py
├── tests/                # Test suite
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   └── GBM_IMPORT_GUIDE.md
└── railway.json          # Railway deployment config
```

---

## Database Schema

### Core Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `vox_grades` | 7,109 | Daily stock grades (1 per ticker per day) |
| `watchlist` | 1,350 | Tracked tickers across all tiers |
| `broker_positions` | 108 | Live positions across all brokers |
| `broker_accounts` | 6 | Connected broker accounts |
| `positions` | 72 | Consolidated portfolio view |
| `trade_signals` | 514 | Generated buy/sell signals |
| `council_deliberations` | 434 | AI council consensus votes |
| `pattern_alerts` | 70 | Technical pattern detections |
| `weather_patterns` | 6,359 | Market regime/weather data |
| `trader_profiles` | 94 | Famous trader tracking |
| `trader_calls` | 20 | Trader call records |
| `sentiment_scores` | 61 | Sentiment analysis |
| `sp500_grades` | 503 | S&P 500 universe grades |
| `sp500_universe` | 503 | S&P 500 constituent list |
| `liquid_universe` | 340 | Liquid/high-volume tickers |
| `universe_tiers` | 1,108 | Tier classification |
| `macro_signals` | 11 | Macroeconomic indicators |
| `sector_momentum` | 26 | Sector rotation data |
| `top_opportunities` | 68 | Best opportunities |
| `unified_grades` | 1,516 | Cross-source unified grades |
| `commodity_prices` | 837 | Commodity tracking |
| `alerts` | 39 | System alerts |
| `journal` | 6 | Trading journal entries |
| `portfolio_goals` | 4 | Portfolio targets |
| `portfolio_history` | 2 | Historical snapshots |
| `discovery_queue` | 20 | New ticker discovery |
| `geopolitical_events` | 4 | Geo events |
| `supply_chain_events` | 5 | Supply chain alerts |
| `weather_risks` | 5 | Weather risk factors |
| `system_logs` | 1 | System events |
| `cron_runs` | 97 | Cron execution history |
| `compounding_projections` | 5 | Growth projections |
| `plays` | 16 | Active trade plays |
| `trade_journal` | 0 | Trade journal (unused) |
| `trader_mentions` | 0 | Trader mentions (unused) |
| `trader_alerts` | 0 | Trader alerts (unused) |
| `performance_metrics` | 0 | Performance metrics (unused) |
| `theme_alignment` | 0 | Theme alignment (unused) |
| `sector_opportunities` | 0 | Sector opportunities (unused) |
| `discovery_history` | 0 | Discovery history (unused) |
| `watchlist_old` | 0 | Legacy watchlist (empty) |
| `watchlist_grades` | 27 | Watchlist-specific grades |

---

## Features

| Feature | Status |
|---------|--------|
| Multi-broker sync (eToro, Binance, GBM, IBKR, Schwab, Bitso) | ✅ |
| Real-time stock grading (technical + fundamental + macro + sentiment) | ✅ |
| Daily price updates | ✅ |
| Telegram alerts (stop loss, daily moves, pattern alerts) | ✅ |
| Delisted stock detection | ✅ |
| Garbage token filtering | ✅ |
| Famous trader tracking (94 traders) | ✅ |
| Trader consensus detection | ✅ |
| Weather pattern analysis | ✅ |
| SP500 grading | ✅ |
| Discovery queue | ✅ |
| Railway deployment | ✅ |
| Railway Postgres database | ✅ |
| Next.js Dashboard | ✅ |

---

## Cron Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| `vox-daily-sync` | Daily 7:30 AM CT | Update prices + check alerts + broker sync |
| `vox-morning-digest` | Daily 6:30 AM CT | Morning trader digest |
| `vox-midday-digest` | Daily 12:00 PM CT | Midday trader digest |
| `vox-evening-digest` | Daily 4:30 PM CT | Evening trader digest |
| `vox-weekly-deep` | Tuesday 7:00 AM CT | Weekly deep digest |
| `vox-auto-discovery` | Wednesday | Auto ticker discovery |
| `vox-broker-reminder` | Friday 9:00 AM CT | Broker statement reminder |
| `vox-grades` | Daily | Grade all watchlist tickers |
| `vox-sp500-sync` | Daily | Update S&P 500 grades |
| `vox-weather` | Daily | Update weather patterns |
| `vox-sentiment` | Daily | Update sentiment scores |
| `vox-council` | Daily | Run council deliberations |
| `vox-discovery` | Daily | Process discovery queue |
| `vox-sector-momentum` | Daily | Update sector rotation |
| `vox-macro` | Daily | Update macro signals |
| `vox-top-opportunities` | Daily | Generate top opportunities |
| `vox-unified-grades` | Daily | Generate unified grades |
| `vox-pattern-alerts` | Daily | Detect technical patterns |
| `vox-trade-signals` | Daily | Generate trade signals |
| `vox-commodity` | Daily | Update commodity prices |
| `vox-journal` | Daily | Trading journal entries |
| `vox-portfolio-history` | Daily | Portfolio snapshot |
| `vox-liquid-universe` | Daily | Update liquid universe |
| `vox-universe-tiers` | Daily | Update tier classifications |
| `vox-technical-signals` | Daily | Update technical signals |
| `vox-market-regime` | Daily | Update market regime |
| `vox-geopolitical` | Daily | Update geopolitical events |
| `vox-supply-chain` | Daily | Update supply chain events |
| `vox-weather-risks` | Daily | Update weather risks |
| `vox-system-logs` | Daily | System health checks |
| `vox-cron-runs` | Daily | Cron execution tracking |
| `vox-compounding` | Daily | Update compounding projections |
| `vox-plays` | Daily | Update active plays |
| `vox-trade-journal` | Daily | Trade journal sync |
| `vox-trader-mentions` | Daily | Update trader mentions |
| `vox-trader-alerts` | Daily | Update trader alerts |
| `vox-performance-metrics` | Daily | Update performance metrics |
| `vox-theme-alignment` | Daily | Update theme alignment |
| `vox-sector-opportunities` | Daily | Update sector opportunities |

---

## Data Flow

```
Brokers (eToro API, Binance API, GBM JSON, IBKR, Schwab, Bitso)
    ↓
Sync Scripts (src/brokers/)
    ↓
Validator (src/sync/validator.py)
    ↓
Railway Postgres (Single source of truth)
    ↓
Grading Engine (src/grading/)
    ↓
Dashboard (Next.js on Railway)
    ↓
Telegram Alerts
```

---

## Environment Variables

```bash
# Railway Postgres
PGHOST=postgres-flpd.railway.internal
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=***

# eToro API
ETORO_USERNAME=your-username
ETORO_PASSWORD=***

# Other brokers (JSON fallback)
GBM_MAIN_JSON={...}
GBM_USA_JSON={...}
BINANCE_JSON={...}
IBKR_JSON={...}
SCHWAB_JSON={...}

# APIs
POLYGON_API_KEY=***
FMP_API_KEY=***
FINNHUB_API_KEY=***

# Telegram
TELEGRAM_BOT_TOKEN=***
TELEGRAM_CHAT_ID=your-chat-id

# OpenAI (for council deliberations)
OPENAI_API_KEY=***
```

---

## Commands

```bash
# Grade all stocks
python scripts/run_grader.py

# Update prices
python scripts/run_daily_update.py

# Import GBM
python scripts/import_gbm.py

# Fix delisted
python scripts/fix_delisted.py

# Run tests
python -m pytest tests/
```

---

## Portfolio Stats

- **Positions:** ~70 across 6 brokers
- **Watchlist:** 1,350 tickers (all tiers)
- **Total Value:** ~$198K USD
- **Brokers:** eToro, GBM (MXN/USD), Binance, IBKR, Schwab, Bitso
- **Tracked Traders:** 94 (Shay Boloor, Cathie Wood, Raoul Pal, Michael Saylor, etc.)
- **Daily Grades:** 1,350 tickers
- **S&P 500 Coverage:** 503 tickers
- **Liquid Universe:** 340 tickers

---

## Database Maintenance

### Deduplication History

| Date | Table | Before | After | Removed |
|------|-------|--------|-------|---------|
| 2026-06-20 | `vox_grades` | 28,858 | 7,109 | 21,749 |
| 2026-06-20 | `trade_signals` | 946 | 514 | 432 |
| 2026-06-20 | `council_deliberations` | 937 | 434 | 503 |
| 2026-06-20 | `pattern_alerts` | 221 | 70 | 151 |

**Strategy:** Keep highest score/grade per (ticker, day). Added `untracked` status for 796 tickers that were graded but not in watchlist.

### Maintenance Commands

```sql
-- Check for duplicates
SELECT ticker, DATE(generated_at), COUNT(*) 
FROM vox_grades 
GROUP BY ticker, DATE(generated_at) 
HAVING COUNT(*) > 1;

-- Check for orphans
SELECT w.ticker 
FROM watchlist w 
LEFT JOIN vox_grades g ON w.ticker = g.ticker 
WHERE g.ticker IS NULL;

-- Check table sizes
SELECT pg_size_pretty(pg_total_relation_size('vox_grades'));
```

---

*Last updated: 2026-06-20*
