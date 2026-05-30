# VOX Architecture

## Overview

VOX is a portfolio tracking and grading system with:
- Multi-broker data sync
- Real-time stock grading (technical + fundamental)
- Daily price updates and alerts
- Streamlit dashboard

## Components

### 1. Data Layer
- **Supabase**: Single source of truth
- **Tables**: `positions`, `watchlist`, `plays`
- **Access**: `src/sync/vox_supabase_sync.py`

### 2. Grading Engine
- **Technical**: RSI, MACD, SMA, volume (`src/grading/technical.py`)
- **Fundamental**: P/E, growth, margins, debt, ROE (`src/grading/fundamental.py`)
- **Orchestrator**: Combines scores → 0-100 grade + council signal (`src/grading/engine.py`)
- **Delisted Detection**: Validates tickers before grading (`src/grading/delisted.py`)

### 3. Sync Layer
- **Broker Scripts**: `src/brokers/` (eToro, Binance, GBM, IBKR, Schwab, Bitso)
- **GBM Importer**: `src/sync/gbm_importer.py` (manual JSON export)
- **Validator**: `src/sync/validator.py` (filters garbage, $10 min)

### 4. Pricing Layer
- **Updater**: `src/pricing/updater.py` (daily price refresh)
- **Sources**: Yahoo Finance for stocks, Binance for crypto

### 5. Alert Layer
- **Notifier**: `src/alerts/notifier.py`
- **Checks**: Stop loss (-20%), daily moves (+/-10%)
- **Delivery**: Telegram

### 6. Dashboard
- **Streamlit**: `src/dashboard/vox_dashboard.py`
- **Hosted**: Railway.app

## Data Flow

```
Brokers → Sync Scripts → Validator → Supabase → Grading → Dashboard
                                              ↓
                                        Pricing Updater
                                              ↓
                                        Alert Notifier
```

## Deployment

- **Platform**: Railway.app
- **Config**: `railway.json`, `Procfile`
- **Auto-deploy**: On push to `main`

## Cron Jobs

| Job | Schedule | Script |
|-----|----------|--------|
| Daily Update | 0 9 * * * | `scripts/run_daily_update.py` |
| Weekly GBM Import | 0 9 * * 1 | `scripts/import_gbm.py` |
