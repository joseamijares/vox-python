# VOX Architecture v6

## Overview

VOX is a multi-layer portfolio intelligence system with:
- Multi-broker data sync (6 brokers)
- Real-time stock grading (technical + fundamental + macro + sentiment + weather)
- Famous trader tracking and consensus detection
- Daily price updates and alerts
- Next.js dashboard on Railway
- Railway Postgres database (single source of truth)

## Components

### 1. Data Layer
- **Railway Postgres**: Single source of truth
- **Tables**: 49 tables across 6 domains (portfolio, grades, signals, traders, weather, system)
- **Access**: `src/sync/vox_postgres_sync.py`
- **Legacy**: Supabase client still exists but unused (`src/sync/vox_supabase_sync.py`)

### 2. Grading Engine
- **Technical**: RSI, MACD, SMA, volume (`src/grading/technical.py`)
- **Fundamental**: P/E, growth, margins, debt, ROE (`src/grading/fundamental.py`)
- **Macro**: Economic indicators, Fed policy, inflation (`src/grading/macro.py`)
- **Sentiment**: Social media, news, analyst ratings (`src/grading/sentiment.py`)
- **Weather**: Market regime, volatility, correlation (`src/grading/weather.py`)
- **Orchestrator**: Combines scores → 0-100 grade + council signal (`src/grading/engine.py`)
- **Delisted Detection**: Validates tickers before grading (`src/grading/delisted.py`)
- **Unified**: Cross-source grade aggregation (`src/grading/unified.py`)

### 3. Sync Layer
- **Broker Scripts**: `src/brokers/` (eToro, Binance, GBM, IBKR, Schwab, Bitso)
- **GBM Importer**: `src/sync/gbm_importer.py` (manual JSON export)
- **Validator**: `src/sync/validator.py` (filters garbage, $10 min)
- **Postgres Sync**: `src/sync/vox_postgres_sync.py` (main sync client)

### 4. Pricing Layer
- **Updater**: `src/pricing/updater.py` (daily price refresh)
- **Sources**: Yahoo Finance for stocks, Binance for crypto
- **Commodities**: `src/pricing/commodities.py` (gold, oil, etc.)

### 5. Alert Layer
- **Notifier**: `src/alerts/notifier.py`
- **Checks**: Stop loss (-20%), daily moves (+/-10%), pattern alerts, trader consensus
- **Delivery**: Telegram bot
- **Digest Schedule**: Morning (6:30 AM), Midday (12 PM), Evening (4:30 PM), Weekly Deep (Tuesday), Auto-Discovery (Wednesday)

### 6. Trader Tracking Layer
- **Profiles**: `src/traders/profiles.py` (94 famous traders)
- **Mentions**: `src/traders/mentions.py` (X/Twitter scraping)
- **Consensus**: `src/traders/consensus.py` (2+ traders on same ticker = high conviction)
- **Calls**: `src/traders/calls.py` (trade call tracking)
- **Alerts**: `src/traders/alerts.py` (consensus alerts)

### 7. Weather Pattern Layer
- **Patterns**: `src/weather/patterns.py` (6,359 weather records)
- **Risks**: `src/weather/risks.py` (weather risk factors)
- **Sector Impact**: `src/weather/sector_impact.py` (affected sectors)

### 8. Dashboard
- **Next.js**: `vox-dashboard` (separate repo, deployed on Railway)
- **URL**: https://web-production-9e321.up.railway.app/
- **Legacy**: Streamlit dashboard (`src/dashboard/vox_dashboard.py`) — deprecated

## Data Flow

```
Brokers → Sync Scripts → Validator → Railway Postgres
                                              ↓
                                    Grading Engine (6 layers)
                                              ↓
                                    Council Deliberations (AI)
                                              ↓
                                    Trade Signals / Pattern Alerts
                                              ↓
                                    Telegram Alerts
                                              ↓
                                    Next.js Dashboard
```

## Database Schema

### Portfolio Domain
- `broker_accounts` — 6 connected brokers
- `broker_positions` — 108 live positions
- `broker_holdings` — 18 holdings
- `broker_status` — 1 status record
- `positions` — 72 consolidated positions
- `portfolio_goals` — 4 targets
- `portfolio_history` — 2 snapshots

### Grading Domain
- `vox_grades` — 7,109 daily grades (1 per ticker per day)
- `sp500_grades` — 503 S&P 500 grades
- `sp500_universe` — 503 constituents
- `watchlist` — 1,350 tracked tickers
- `watchlist_grades` — 27 watchlist-specific grades
- `unified_grades` — 1,516 cross-source grades
- `liquid_universe` — 340 liquid tickers
- `universe_tiers` — 1,108 tier classifications

### Signals Domain
- `trade_signals` — 514 generated signals
- `council_deliberations` — 434 AI council votes
- `pattern_alerts` — 70 technical patterns
- `technical_signals` — 126 technical indicators
- `top_opportunities` — 68 best opportunities
- `sector_momentum` — 26 sector rotation records
- `sector_opportunities` — 0 (unused)
- `discovery_queue` — 20 new tickers
- `discovery_history` — 0 (unused)

### Trader Domain
- `trader_profiles` — 94 famous traders
- `trader_calls` — 20 trade calls
- `trader_mentions` — 0 (unused)
- `trader_alerts` — 0 (unused)

### Weather Domain
- `weather_patterns` — 6,359 weather records
- `weather_risks` — 5 risk factors
- `macro_signals` — 11 macro indicators
- `market_regime` — 29 regime records
- `geopolitical_events` — 4 geo events
- `supply_chain_events` — 5 supply chain alerts
- `sentiment_scores` — 61 sentiment records
- `commodity_prices` — 837 commodity prices

### System Domain
- `alerts` — 39 system alerts
- `cron_runs` — 97 execution records
- `system_logs` — 1 log
- `journal` — 6 trading journal entries
- `trade_journal` — 0 (unused)
- `compounding_projections` — 5 projections
- `plays` — 16 active plays
- `performance_metrics` — 0 (unused)
- `theme_alignment` — 0 (unused)
- `watchlist_old` — 0 (legacy, empty)

## Deployment

- **Platform**: Railway.app
- **Config**: `railway.json`, `Procfile`
- **Auto-deploy**: On push to `main`
- **Database**: Railway Postgres (postgres-flpd)
- **Dashboard**: Next.js service (web)
- **Grader**: Python service (grader)

## Cron Jobs

36 cron jobs running daily/weekly across all layers. See README.md for full schedule.

## Key Metrics

- **Total Tickers Graded Daily**: 1,350
- **S&P 500 Coverage**: 503/503 (100%)
- **Liquid Universe**: 340 tickers
- **Famous Traders Tracked**: 94
- **Broker Accounts**: 6
- **Portfolio Value**: ~$198K USD
- **Daily Alerts**: ~20-50
- **Database Size**: ~20MB (healthy)

## Deduplication History

| Date | Table | Before | After | Removed | Strategy |
|------|-------|--------|-------|---------|----------|
| 2026-06-20 | `vox_grades` | 28,858 | 7,109 | 21,749 | Keep max grade per (ticker, day) |
| 2026-06-20 | `trade_signals` | 946 | 514 | 432 | Keep max composite_score per (ticker, day) |
| 2026-06-20 | `council_deliberations` | 937 | 434 | 503 | Keep max consensus_pct per (ticker, day) |
| 2026-06-20 | `pattern_alerts` | 221 | 70 | 151 | Keep max conviction per (ticker, day) |

## Maintenance

### Check for Duplicates
```sql
SELECT ticker, DATE(generated_at), COUNT(*) 
FROM vox_grades 
GROUP BY ticker, DATE(generated_at) 
HAVING COUNT(*) > 1;
```

### Check for Orphans
```sql
-- Watchlist tickers without grades
SELECT w.ticker 
FROM watchlist w 
LEFT JOIN vox_grades g ON w.ticker = g.ticker 
WHERE g.ticker IS NULL;

-- Graded tickers not in watchlist
SELECT g.ticker 
FROM vox_grades g 
LEFT JOIN watchlist w ON g.ticker = w.ticker 
WHERE w.ticker IS NULL;
```

### Check Table Sizes
```sql
SELECT 
    schemaname, tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

*Last updated: 2026-06-20*
