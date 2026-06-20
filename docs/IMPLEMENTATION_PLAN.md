# VOX System Rebuild — Implementation Plan v6

> **Status:** Phase 0-3 Complete ✅ | Phase 4-5 In Progress 🔄  
> **Last Updated:** 2026-06-20  
> **Goal:** Fix critical bugs, build grading engine, add tests, stabilize system  
> **Timeline:** 2-3 weeks (extended to 6 weeks for v6)  
> **Priority:** P0 (critical) → P1 (important) → P2 (nice to have)

---

## Phase 0: Foundation (Day 1) ✅ COMPLETE

### Task 0.1: Fix .env file ✅
**Objective:** Replace truncated Supabase key with full key

**Status:** DONE — Railway Postgres credentials configured  
**Note:** System migrated from Supabase to Railway Postgres in v5. Supabase client still exists but unused.

---

### Task 0.2: Fix requirements.txt ✅
**Objective:** Fix malformed dependency line

**Status:** DONE — requirements.txt updated with all dependencies

---

### Task 0.3: Create directory structure ✅
**Objective:** Set up proper project layout

**Status:** DONE — All directories created:
- `src/{grading,sync,pricing,alerts,dashboard,brokers,traders,weather}/`
- `tests/`
- `scripts/`
- `docs/`

---

## Phase 1: Grading Engine (Days 2-5) ✅ COMPLETE

### Task 1.1: Build technical grader ✅
**Objective:** Calculate technical score from price data

**Status:** DONE — `src/grading/technical.py`
- RSI, MACD, SMA, volume analysis
- Returns score 0-100 per ticker

---

### Task 1.2: Build fundamental grader ✅
**Objective:** Calculate fundamental score from financial data

**Status:** DONE — `src/grading/fundamental.py`
- P/E, revenue growth, margins, debt, ROE
- Finnhub API integration

---

### Task 1.3: Build grading engine orchestrator ✅
**Objective:** Combine all scoring modules into final grade

**Status:** DONE — `src/grading/engine.py`
- 6-layer scoring: technical (25%), fundamental (25%), sentiment (20%), momentum (20%), risk (10%)
- Council signal generation: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL

---

### Task 1.4: Add delisted detection ✅
**Objective:** Validate tickers before grading

**Status:** DONE — `src/grading/delisted.py`
- Detects dead/suspended tickers
- Filters garbage tokens

---

### Task 1.5: Add macro scoring ✅
**Objective:** Factor in macroeconomic conditions

**Status:** DONE — `src/grading/macro.py`
- Fed policy, inflation, GDP, employment
- `macro_signals` table (11 records)

---

### Task 1.6: Add sentiment scoring ✅
**Objective:** Factor in market sentiment

**Status:** DONE — `src/grading/sentiment.py`
- Social media, news, analyst ratings
- `sentiment_scores` table (61 records)

---

### Task 1.7: Add weather scoring ✅
**Objective:** Factor in market weather/regime

**Status:** DONE — `src/grading/weather.py`
- Volatility, correlation, regime detection
- `weather_patterns` table (6,359 records)

---

## Phase 2: Data Sync (Days 6-10) ✅ COMPLETE

### Task 2.1: Build Postgres sync client ✅
**Objective:** Replace Supabase with Railway Postgres

**Status:** DONE — `src/sync/vox_postgres_sync.py`
- Full CRUD operations
- Connection pooling
- Error handling

---

### Task 2.2: Build broker sync scripts ✅
**Objective:** Sync all 6 brokers

**Status:** DONE — `src/brokers/`
- `etoro_sync.py` — eToro API
- `binance_sync.py` — Binance API
- `gbm_sync.py` — GBM JSON import
- `ibkr_sync.py` — IBKR JSON import
- `schwab_sync.py` — Schwab JSON import
- `bitso_sync.py` — Bitso API

---

### Task 2.3: Build validator ✅
**Objective:** Filter garbage, validate data

**Status:** DONE — `src/sync/validator.py`
- $10 minimum price filter
- Garbage token detection
- Delisted stock removal

---

### Task 2.4: Build pricing updater ✅
**Objective:** Daily price refresh

**Status:** DONE — `src/pricing/updater.py`
- Yahoo Finance for stocks
- Binance for crypto
- `commodity_prices` table (837 records)

---

## Phase 3: Alerts & Notifications (Days 11-14) ✅ COMPLETE

### Task 3.1: Build Telegram notifier ✅
**Objective:** Send alerts to Telegram

**Status:** DONE — `src/alerts/notifier.py`
- Stop loss alerts (-20%)
- Daily move alerts (+/-10%)
- Pattern alerts
- Trader consensus alerts

---

### Task 3.2: Build digest system ✅
**Objective:** Scheduled digest messages

**Status:** DONE — 5 digest schedules:
- Morning digest (6:30 AM CT)
- Midday digest (12:00 PM CT)
- Evening digest (4:30 PM CT)
- Weekly deep digest (Tuesday 7 AM)
- Auto-discovery (Wednesday)

---

### Task 3.3: Build pattern alerts ✅
**Objective:** Detect technical patterns

**Status:** DONE — `src/alerts/patterns.py`
- `pattern_alerts` table (70 records)
- Conviction scoring
- Direction detection

---

## Phase 4: Trader Tracking (Days 15-18) ✅ COMPLETE

### Task 4.1: Build trader profiles ✅
**Objective:** Track famous traders

**Status:** DONE — `src/traders/profiles.py`
- 94 trader profiles
- Weight system (Shay Boloor = 1.0)
- `trader_profiles` table (94 records)

---

### Task 4.2: Build trader consensus ✅
**Objective:** Detect when 2+ traders agree

**Status:** DONE — `src/traders/consensus.py`
- Consensus detection algorithm
- High conviction signal (2+ traders on same ticker)
- Current consensus: IONQ (Boloor+Wood), MSTR (Saylor+Raoul)

---

### Task 4.3: Build trader calls tracking ✅
**Objective:** Record trade calls

**Status:** DONE — `src/traders/calls.py`
- `trader_calls` table (20 records)
- Call validation

---

## Phase 5: Advanced Features (Days 19-25) 🔄 IN PROGRESS

### Task 5.1: Build unified grades ✅
**Objective:** Cross-source grade aggregation

**Status:** DONE — `src/grading/unified.py`
- `unified_grades` table (1,516 records)
- Combines multiple grade sources

---

### Task 5.2: Build discovery queue ✅
**Objective:** Auto-discover new tickers

**Status:** DONE — `src/discovery/queue.py`
- `discovery_queue` table (20 records)
- Auto-add from trader mentions, news, scans

---

### Task 5.3: Build sector momentum ✅
**Objective:** Track sector rotation

**Status:** DONE — `src/sector/momentum.py`
- `sector_momentum` table (26 records)
- Buy/hold/sell counts per sector

---

### Task 5.4: Build SP500 grading ✅
**Objective:** Grade all S&P 500 constituents

**Status:** DONE — `src/grading/sp500.py`
- `sp500_grades` table (503 records)
- `sp500_universe` table (503 records)
- 100% S&P 500 coverage

---

### Task 5.5: Build liquid universe ✅
**Objective:** Track high-volume liquid tickers

**Status:** DONE — `src/universe/liquid.py`
- `liquid_universe` table (340 records)
- Volume and liquidity filters

---

### Task 5.6: Build universe tiers ✅
**Objective:** Tier classification system

**Status:** DONE — `src/universe/tiers.py`
- `universe_tiers` table (1,108 records)
- Tier 1 (core), Tier 2 (growth), Tier 3 (speculative)

---

### Task 5.7: Build council deliberations ✅
**Objective:** AI council consensus system

**Status:** DONE — `src/council/deliberations.py`
- `council_deliberations` table (434 records)
- OpenAI-powered consensus
- Risk veto system

---

### Task 5.8: Build trade signals ✅
**Objective:** Generate actionable trade signals

**Status:** DONE — `src/signals/trade.py`
- `trade_signals` table (514 records)
- Composite scoring
- Expiration dates

---

### Task 5.9: Build top opportunities ✅
**Objective:** Generate best opportunities list

**Status:** DONE — `src/opportunities/top.py`
- `top_opportunities` table (68 records)
- Ranked by composite score

---

### Task 5.10: Build market regime ✅
**Objective:** Track market regime changes

**Status:** DONE — `src/market/regime.py`
- `market_regime` table (29 records)
- Bull/bear/sideways detection

---

### Task 5.11: Build compounding projections ✅
**Objective:** Project portfolio growth

**Status:** DONE — `src/portfolio/compounding.py`
- `compounding_projections` table (5 records)
- Goal-based projections

---

### Task 5.12: Build plays tracking ✅
**Objective:** Track active trade plays

**Status:** DONE — `src/plays/tracker.py`
- `plays` table (16 records)
- Active play management

---

## Phase 6: Testing & Stabilization (Days 26-30) 🔄 IN PROGRESS

### Task 6.1: Write tests 🔄
**Objective:** Test coverage for core modules

**Status:** IN PROGRESS
- `tests/test_technical.py` — DONE
- `tests/test_fundamental.py` — DONE
- `tests/test_engine.py` — PENDING
- `tests/test_sync.py` — PENDING
- `tests/test_alerts.py` — PENDING

---

### Task 6.2: Fix edge cases 🔄
**Objective:** Handle edge cases and errors

**Status:** IN PROGRESS
- Delisted stock handling ✅
- API rate limiting ✅
- Database connection retries ✅
- Missing data handling ✅
- Duplicate prevention ✅ (DONE 2026-06-20)

---

### Task 6.3: Performance optimization 🔄
**Objective:** Speed up grading and sync

**Status:** IN PROGRESS
- Batch processing ✅
- Connection pooling ✅
- Parallel grading (partial)
- Caching layer (pending)

---

### Task 6.4: Documentation update ✅
**Objective:** Update all docs

**Status:** DONE (2026-06-20)
- `README.md` — Updated with v6 stats, tables, features
- `ARCHITECTURE.md` — Updated with full schema, data flow, metrics
- `IMPLEMENTATION_PLAN.md` — This file, updated with completion status

---

## Phase 7: Future Enhancements (P2) 📋 BACKLOG

### Task 7.1: Options grading
**Objective:** Grade options strategies
**Status:** BACKLOG

---

### Task 7.2: Crypto DeFi tracking
**Objective:** Track DeFi protocols and yields
**Status:** BACKLOG

---

### Task 7.3: International markets
**Objective:** Add HK, EU, JP market coverage
**Status:** BACKLOG
- 0700.HK already in universe

---

### Task 7.4: Machine learning grades
**Objective:** ML-based grade prediction
**Status:** BACKLOG

---

### Task 7.5: Backtesting framework
**Objective:** Backtest strategies
**Status:** BACKLOG

---

### Task 7.6: Mobile app
**Objective:** React Native mobile app
**Status:** BACKLOG

---

## Known Issues & Fixes

| Issue | Date Fixed | Description |
|-------|-----------|-------------|
| vox_grades duplicates | 2026-06-20 | 21,749 duplicate rows removed |
| trade_signals duplicates | 2026-06-20 | 432 duplicate rows removed |
| council_deliberations duplicates | 2026-06-20 | 503 duplicate rows removed |
| pattern_alerts duplicates | 2026-06-20 | 151 duplicate rows removed |
| Untracked graded tickers | 2026-06-20 | 796 tickers added to watchlist with 'untracked' status |
| broker_positions orphans | 2026-06-20 | 3 orphaned positions identified (pending fix) |
| positions orphans | 2026-06-20 | 8 orphaned positions identified (pending fix) |

---

## Database Maintenance Checklist

### Daily
- [ ] Check cron_runs for failures
- [ ] Verify vox_grades has 1 row per ticker per day
- [ ] Check alerts table for new alerts

### Weekly
- [ ] Run duplicate check on all tables
- [ ] Check orphan counts (broker_positions, positions)
- [ ] Review discovery_queue for new tickers
- [ ] Archive old JSON files from vox_analysis/

### Monthly
- [ ] Full database audit (all 49 tables)
- [ ] Update documentation if schema changes
- [ ] Review and clean unused tables
- [ ] Backup database

---

## Commands Reference

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

# Check database health
python scripts/db_health_check.py

# Manual deduplication
python scripts/dedup_vox_grades.py
```

---

*Last updated: 2026-06-20*
