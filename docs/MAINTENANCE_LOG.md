# VOX Database Maintenance Log

## 2026-06-20 — Major Deduplication & Cleanup

### Summary
Performed comprehensive database audit and cleanup across all 49 tables. Fixed duplicates, contradictions, and orphaned data in the watchlist and grading system.

### Changes Made

#### 1. vox_grades Deduplication
- **Before:** 28,858 rows
- **After:** 7,109 rows
- **Removed:** 21,749 duplicate rows
- **Strategy:** Kept highest `vox_grade` per `(ticker, DATE(generated_at))`
- **Impact:** Every ticker now has exactly 1 grade per day

#### 2. trade_signals Deduplication
- **Before:** 946 rows
- **After:** 514 rows
- **Removed:** 432 duplicate rows
- **Strategy:** Kept highest `composite_score` per `(ticker, DATE(created_at))`

#### 3. council_deliberations Deduplication
- **Before:** 937 rows
- **After:** 434 rows
- **Removed:** 503 duplicate rows
- **Strategy:** Kept highest `consensus_pct` per `(ticker, DATE(timestamp))`

#### 4. pattern_alerts Deduplication
- **Before:** 221 rows
- **After:** 70 rows
- **Removed:** 151 duplicate rows
- **Strategy:** Kept highest `conviction` per `(ticker, DATE(detected_at))`

#### 5. watchlist Cleanup
- **Before:** 555 rows (some tickers graded but not tracked)
- **After:** 1,350 rows
- **Added:** 796 tickers with status `untracked`
- **Reason:** All graded tickers should be in watchlist for consistency

#### 6. watchlist_old
- **Status:** Already empty (0 rows)
- **Action:** None needed

#### 7. JSON Archive
- **Action:** Moved 16 stale JSON files from `/Users/jos/vox_analysis/` to `/Users/jos/vox_analysis/archive/`
- **Files:** vox_report.json, vox_report_all.json, vox_report_small.json, watchlist_*.json, grades_*.json, etc.

### Verification Results

| Check | Result | Expected |
|-------|--------|----------|
| vox_grades duplicates | 0 | 0 |
| Grade contradictions | 0 | 0 |
| watchlist duplicates | 0 | 0 |
| watchlist status conflicts | 0 | 0 |
| Orphaned watchlist entries | 0 | 0 |
| Untracked graded tickers | 0 | 0 |
| trade_signals duplicates | 0 | 0 |
| council_deliberations duplicates | 0 | 0 |
| pattern_alerts duplicates | 0 | 0 |
| sp500_grades duplicates | 0 | 0 |
| liquid_universe duplicates | 0 | 0 |
| universe_tiers duplicates | 0 | 0 |
| unified_grades duplicates | 0 | 0 |

### Remaining Issues (Non-Critical)

| Issue | Count | Table | Priority |
|-------|-------|-------|----------|
| broker_positions orphans | 3 | broker_positions | P2 |
| positions orphans | 8 | positions | P2 |

These are positions that don't have matching broker records. They may be manual entries or legacy data. Safe to leave for now — will be cleaned up in future broker sync.

### SQL Used

```sql
-- Deduplicate vox_grades
CREATE TABLE vox_grades_dedup AS
SELECT DISTINCT ON (ticker, DATE(generated_at))
    *
FROM vox_grades
ORDER BY ticker, DATE(generated_at), vox_grade DESC, generated_at DESC;

-- Deduplicate trade_signals
CREATE TABLE trade_signals_dedup AS
SELECT DISTINCT ON (ticker, DATE(created_at))
    *
FROM trade_signals
ORDER BY ticker, DATE(created_at), composite_score DESC, created_at DESC;

-- Deduplicate council_deliberations
CREATE TABLE council_deliberations_dedup AS
SELECT DISTINCT ON (ticker, DATE(timestamp))
    *
FROM council_deliberations
ORDER BY ticker, DATE(timestamp), consensus_pct DESC, timestamp DESC;

-- Deduplicate pattern_alerts
CREATE TABLE pattern_alerts_dedup AS
SELECT DISTINCT ON (ticker, DATE(detected_at))
    *
FROM pattern_alerts
ORDER BY ticker, DATE(detected_at), conviction DESC, detected_at DESC;

-- Add untracked tickers to watchlist
INSERT INTO watchlist (ticker, name, status, added_at, notes)
SELECT DISTINCT g.ticker, g.name, 'untracked', NOW(), 'Auto-added from vox_grades dedup'
FROM vox_grades g
LEFT JOIN watchlist w ON g.ticker = w.ticker
WHERE w.ticker IS NULL;
```

### Next Maintenance

- **Daily:** Check cron_runs for failures, verify vox_grades has 1 row per ticker per day
- **Weekly:** Run duplicate check on all tables, check orphan counts
- **Monthly:** Full database audit, update documentation, backup

---

*Logged by: Hermes Agent*
*Date: 2026-06-20*
