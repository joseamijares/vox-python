# GBM Portfolio Import Guide

> **For:** GBM Plus (Mexico) — Manual JSON Export System
> **No API available** — Uses weekly/daily JSON exports

---

## Quick Start (30 seconds)

### 1. Export from GBM Plus

**Web:**
1. Log in to https://gbm.com
2. Go to **Portfolio** → **Export**
3. Select **JSON format**
4. Download file

**App:**
1. Open GBM Plus app
2. Go to **Portfolio** → **More** → **Export Data**
3. Select **JSON**
4. Share/download file

### 2. Save to Correct Location

```bash
# Rename the downloaded file and move it:
mv ~/Downloads/gbm_export.json ~/.hermes/scripts/gbm_main_portfolio.json
```

### 3. Run Import

```bash
cd ~/dev/vox-python
python scripts/import_gbm.py
```

**Optional — Override MXN/USD rate:**
```bash
python scripts/import_gbm.py 18.2
```

---

## What the System Does

```
GBM JSON Export
      ↓
[Parse] — Extract SIC + National positions
      ↓
[Validate] — Filter garbage, verify tickers
      ↓
[Convert] — MXN → USD (live rate)
      ↓
[Sync] — Update Supabase (merge with existing)
      ↓
[Report] — Generate audit report
```

### Validation Rules

| Rule | Action |
|------|--------|
| Value < $10 | Reject (dust) |
| Known garbage tokens | Reject (meme coins) |
| Invalid stock ticker | Reject (Yahoo Finance check) |
| Single-letter crypto | Reject (suspicious) |
| Duplicate tickers | Merge brokers, sum values |

---

## File Locations

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/gbm_main_portfolio.json` | GBM Main export (MXN) |
| `~/.hermes/scripts/gbm_usa_portfolio.json` | GBM USA export (USD) |
| `src/sync/gbm_importer.py` | Import engine |
| `src/sync/validator.py` | Validation rules |
| `scripts/import_gbm.py` | CLI runner |

---

## Output Example

```
🚀 Starting GBM Portfolio Sync...

📁 Loading GBM Main: /Users/jos/.hermes/scripts/gbm_main_portfolio.json
  Found 18 raw positions
  ✅ Valid: 18 | ❌ Rejected: 0

💰 Total value synced: $71,177.28

--- SYNCED TO SUPABASE ---
  Inserted: 1
  Updated: 17
  Failed: 0

📝 Report saved: gbm_sync_report_20260529_181655.txt
```

---

## Troubleshooting

### "File not found"
```bash
# Check if file exists
ls ~/.hermes/scripts/gbm_main_portfolio.json

# If not, check Downloads
ls ~/Downloads/*.json
```

### "Invalid JSON"
- Make sure you exported as **JSON**, not CSV or Excel
- Try re-exporting from GBM

### "Wrong exchange rate"
```bash
# Check current rate
curl -s "https://api.exchangerate-api.com/v4/latest/MXN" | grep USD

# Override when running
python scripts/import_gbm.py 18.5
```

### "Positions missing"
- Check if they're in the JSON export
- If value < $10, they're filtered as dust
- Check report for rejected positions

---

## Weekly Workflow

```bash
# 1. Export from GBM (Monday morning)
# 2. Save file
mv ~/Downloads/gbm*.json ~/.hermes/scripts/gbm_main_portfolio.json

# 3. Run import
cd ~/dev/vox-python
python scripts/import_gbm.py

# 4. Check report
cat ~/.hermes/scripts/gbm_sync_report_*.txt
```

---

## Automation (Optional)

### Cron Job — Weekly Auto-Import

```bash
# Edit crontab
crontab -e

# Add line for Monday 9 AM
0 9 * * 1 cd ~/dev/vox-python && python scripts/import_gbm.py >> ~/.hermes/scripts/gbm_cron.log 2>&1
```

### Telegram Notification

Add to `scripts/import_gbm.py`:
```python
import requests

def notify_telegram(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})
```

---

## Data Safety

- **Never deletes** positions from other brokers
- **Only updates** GBM positions
- **Merges** brokers if same ticker exists (e.g., VOO on eToro + GBM)
- **Saves report** for audit trail
- **Validates** every ticker before sync

---

## Need Help?

Check the latest sync report:
```bash
ls -lt ~/.hermes/scripts/gbm_sync_report_*.txt | head -1
```
