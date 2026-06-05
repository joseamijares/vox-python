# VOX Portfolio System

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

## Features

| Feature | Status |
|---------|--------|
| Multi-broker sync (eToro, Binance, GBM, IBKR, Schwab, Bitso) | ✅ |
| Real-time stock grading (technical + fundamental) | ✅ |
| Daily price updates | ✅ |
| Telegram alerts (stop loss, daily moves) | ✅ |
| Delisted stock detection | ✅ |
| Garbage token filtering | ✅ |
| Railway deployment | ✅ |
| Railway Postgres database | ✅ |

---

## Cron Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| `vox-daily-sync` | Daily 7:30 AM CT | Update prices + check alerts + broker sync |

---

## Data Flow

```
Brokers (eToro API, Binance API, GBM JSON)
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
```

---

## Environment Variables

```bash
# Railway Postgres
PGHOST=postgres-flpd.railway.internal
PGPORT=5432
PGDATABASE=railway
PGUSER=railway
PGPASSWORD=your-password

# eToro API
ETORO_USERNAME=your-username
ETORO_PASSWORD=your-password

# Other brokers (JSON fallback)
GBM_MAIN_JSON={...}
GBM_USA_JSON={...}
BINANCE_JSON={...}
IBKR_JSON={...}
SCHWAB_JSON={...}

# APIs
POLYGON_API_KEY=your-key
FMP_API_KEY=your-key

# Telegram
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id
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

- **Positions:** 70
- **Watchlist:** 277 stocks
- **Total Value:** ~$185K
- **Brokers:** eToro, GBM, Binance, IBKR, Schwab, Bitso

---

*Last updated: 2026-06-05*
