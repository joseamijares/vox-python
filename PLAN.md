# VOX Python Migration - Implementation Plan

## Current Status

### ✅ Completed
- **Supabase Data Fixed**: Real portfolio ~$195K (was showing wrong $181K)
- **Python Backend**: Streamlit dashboard reads from Supabase
- **Broker Sync Scripts**:
  - ✅ eToro: Live API sync ($85K)
  - ✅ Binance: Live API sync ($19K)
  - ⚠️ GBM Main/USA: JSON export sync (stale May 21, $73K + $14.5K)
  - ⚠️ IBKR/Schwab/Bitso: JSON export sync ($1.3K + $1.6K + $0.12)
- **Dashboard Deployed**: https://web-production-236e93.up.railway.app/

### ❌ Not Completed
- [ ] Dashboard styling (doesn't match Vercel design)
- [ ] Real-time price updates
- [ ] Automated alerts
- [ ] GBM/IBKR/Schwab/Bitso live API sync
- [ ] Crypto-specific grading
- [ ] Watchlist integration
- [ ] Council review system
- [ ] Agent pipeline migration

---

## Phase 1: Dashboard Styling (Priority: HIGH)

### Goal
Match Vercel dashboard design exactly

### Vercel Design Reference
- Background: `#0B0E14`
- Sidebar: `#141721`
- Cards: `#161B22`
- Primary Blue: `#3B82F6`
- Success Green: `#22C55E`
- Warning: `#F59E0B`
- Danger Red: `#EF4444`
- Text White: `#FFFFFF`
- Text Muted: `#8B949E`
- Rounded corners: 8-12px
- Thin borders: `#30363D`

### Tasks
1. [ ] Apply dark theme CSS to Streamlit
2. [ ] Create card-based layout for KPIs
3. [ ] Style sidebar navigation
4. [ ] Style tables (Portfolio, Watchlist)
5. [ ] Add hover effects
6. [ ] Match typography (Inter font, sizes)
7. [ ] Add gradient accents
8. [ ] Style buttons (Sync, primary actions)

### Files to Modify
- `vox_dashboard.py` - Main styling
- `requirements.txt` - Add streamlit-extras for better components

---

## Phase 2: Real-Time Price Updates (Priority: HIGH)

### Goal
Update prices every 15 minutes during market hours

### Approach
- Use Polygon.io API (existing key)
- Batch requests for all tickers
- Update Supabase `live_price` and `live_value`
- Run as background job on Railway

### Tasks
1. [ ] Create `price_updater.py`
2. [ ] Fetch prices from Polygon.io
3. [ ] Update Supabase positions
4. [ ] Handle crypto prices (Binance API)
5. [ ] Schedule on Railway (cron job)
6. [ ] Add price change indicators to dashboard

### Files to Create
- `price_updater.py`

---

## Phase 3: Automated Alerts (Priority: HIGH)

### Goal
Replace v8 alert system with Python implementation

### Alert Types
- Stop losses hit
- >10% daily moves
- High-relevance news
- Trump mentions
- Daily digest

### Tasks
1. [ ] Create `alert_engine.py`
2. [ ] Monitor price changes
3. [ ] Check stop losses
4. [ ] Integrate with news agents
5. [ ] Send alerts via Telegram
6. [ ] Max 3/day, 24h dedup

### Files to Create
- `alert_engine.py`
- `alert_history.json`

---

## Phase 4: Broker API Expansion (Priority: MEDIUM)

### Goal
Get live API access for remaining brokers

### Brokers
- **GBM Main/USA**: Contact GBM for API access
- **IBKR**: Interactive Brokers API (TWS/Gateway)
- **Schwab**: Schwab API (requires developer account)
- **Bitso**: Bitso API (already have?)

### Tasks
1. [ ] Research GBM API availability
2. [ ] Set up IBKR TWS API
3. [ ] Apply for Schwab developer account
4. [ ] Check Bitso API credentials
5. [ ] Create unified broker sync scheduler

---

## Phase 5: Crypto Grading (Priority: MEDIUM)

### Goal
Fix crypto grades (BTC/ETH showing 34, should be 65+)

### Approach
- Separate grading system for crypto
- Based on: market cap, momentum, network activity
- BTC/ETH: 65-75
- Altcoins: 35-55

### Tasks
1. [ ] Create `crypto_grader.py`
2. [ ] Define crypto scoring criteria
3. [ ] Update Supabase grades
4. [ ] Show crypto-specific metrics

---

## Phase 6: Watchlist Integration (Priority: MEDIUM)

### Goal
Full watchlist management in dashboard

### Features
- Add/remove tickers
- Set buy zones, stops, targets
- Grade tracking over time
- Council review status

### Tasks
1. [ ] Create watchlist page
2. [ ] CRUD operations for tickers
3. [ ] Grade history chart
4. [ ] Council vote tracking

---

## Phase 7: Agent Pipeline Migration (Priority: LOW)

### Goal
Move all 10 agents from shell scripts to Python

### Agents
1. News Agent
2. Trump Tracker
3. Reddit Agent
4. X/Twitter Agent
5. Volume Agent
6. Debrief Agent
7. Stock Researcher
8. Crypto Researcher
9. Macro Agent
10. Sector Agent

### Tasks
1. [ ] Convert each agent to Python
2. [ ] Unified orchestrator
3. [ ] Signal aggregation
4. [ ] Council review automation

---

## Phase 8: Testing & Deployment (Priority: HIGH)

### Goal
Production-ready system

### Tasks
1. [ ] Unit tests for sync scripts
2. [ ] Integration tests for dashboard
3. [ ] Error handling & logging
4. [ ] Performance optimization
5. [ ] Railway production config
6. [ ] Domain setup (custom URL)
7. [ ] SSL/HTTPS

---

## Best Practices

### Code Quality
- Type hints on all functions
- Docstrings for all modules
- Error handling with try/except
- Logging instead of print statements
- Unit tests for critical paths

### Data Integrity
- Supabase = single source of truth
- JSON files = cache/backup only
- Validate all API responses
- Never invent data
- Always verify with user before major changes

### Security
- API keys in .env only
- Never commit credentials
- Use Railway secrets for production
- Rate limit API calls

### Performance
- Cache data in Streamlit (ttl=60s)
- Batch Supabase operations
- Lazy load heavy components
- Use connection pooling

---

## Timeline

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Styling | 2-3 days | HIGH |
| Phase 2: Price Updates | 1-2 days | HIGH |
| Phase 3: Alerts | 2-3 days | HIGH |
| Phase 4: Broker APIs | 1-2 weeks | MEDIUM |
| Phase 5: Crypto Grading | 1 day | MEDIUM |
| Phase 6: Watchlist | 2-3 days | MEDIUM |
| Phase 7: Agents | 2-3 weeks | LOW |
| Phase 8: Testing | 1 week | HIGH |

**Total: 4-6 weeks for full migration**

---

## Next Immediate Actions

1. **Fix dashboard styling** — Match Vercel design
2. **Add price updater** — Real-time prices
3. **Set up alerts** — Replace v8 system

**Which phase should we start with?**