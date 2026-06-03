#!/usr/bin/env python3
"""
VOX PostgreSQL Sync Module
Replaces Supabase with direct PostgreSQL using psycopg2.
All scripts import this instead of vox_supabase_sync.
"""

import os
import json
import urllib.parse
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from contextlib import contextmanager

# -- Connection ---------------------------------------------------------------

def _get_conn_kwargs():
    """Build connection kwargs from env (Railway-style or local)."""
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and db_url.startswith("postgresql://"):
        parsed = urllib.parse.urlparse(db_url)
        return {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "user": parsed.username,
            "password": parsed.password,
            "dbname": parsed.path.lstrip("/"),
        }

    return {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": int(os.environ.get("PGPORT", "5432")),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
        "dbname": os.environ.get("PGDATABASE", "railway"),
    }


@contextmanager
def _get_cursor():
    """Yield a RealDictCursor, auto-commit + close."""
    kwargs = _get_conn_kwargs()
    conn = psycopg2.connect(**kwargs)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# -- Helpers ------------------------------------------------------------------

def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _to_jsonb(val):
    """Convert Python list/dict to JSONB string for Postgres."""
    if val is None:
        return "[]"
    return json.dumps(val)


# -- CRUD: positions ----------------------------------------------------------

def get_positions():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM positions ORDER BY live_value DESC")
        return [dict(r) for r in cur.fetchall()]


def upsert_position(record: dict):
    """Insert or update a position by ticker."""
    sql = """
    INSERT INTO positions (ticker, shares, avg_cost, live_price, live_value, grade, council, brokers, sector, updated_at)
    VALUES (%(ticker)s, %(shares)s, %(avg_cost)s, %(live_price)s, %(live_value)s, %(grade)s, %(council)s, %(brokers)s::jsonb, %(sector)s, %(updated_at)s)
    ON CONFLICT (ticker) DO UPDATE SET
        shares = EXCLUDED.shares,
        avg_cost = EXCLUDED.avg_cost,
        live_price = EXCLUDED.live_price,
        live_value = EXCLUDED.live_value,
        grade = EXCLUDED.grade,
        council = EXCLUDED.council,
        brokers = EXCLUDED.brokers,
        sector = EXCLUDED.sector,
        updated_at = EXCLUDED.updated_at
    """
    record["brokers"] = _to_jsonb(record.get("brokers", []))
    record.setdefault("updated_at", _now_iso())
    with _get_cursor() as cur:
        cur.execute(sql, record)


def delete_positions_by_broker(broker_name: str):
    """Delete positions where brokers array contains broker_name."""
    with _get_cursor() as cur:
        cur.execute(
            "DELETE FROM positions WHERE brokers @> to_jsonb(%s::text)",
            ([broker_name],)
        )


def update_position(ticker: str, fields: dict):
    """Partial update of a position."""
    if not fields:
        return
    set_clause = ", ".join(f"{k} = %({k})s" for k in fields)
    sql = f"UPDATE positions SET {set_clause} WHERE ticker = %(ticker)s"
    fields["ticker"] = ticker
    with _get_cursor() as cur:
        cur.execute(sql, fields)


def get_position_by_ticker(ticker: str):
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM positions WHERE ticker = %s", (ticker,))
        row = cur.fetchone()
        return dict(row) if row else None


# -- CRUD: watchlist ----------------------------------------------------------

def get_watchlist():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM watchlist ORDER BY grade DESC")
        return [dict(r) for r in cur.fetchall()]


def upsert_watchlist(record: dict):
    sql = """
    INSERT INTO watchlist (ticker, name, sector, thesis, entry_price, target_price, stop_loss, grade, council, status, added_at, notes)
    VALUES (%(ticker)s, %(name)s, %(sector)s, %(thesis)s, %(entry_price)s, %(target_price)s, %(stop_loss)s, %(grade)s, %(council)s, %(status)s, %(added_at)s, %(notes)s)
    ON CONFLICT (ticker) DO UPDATE SET
        name = EXCLUDED.name,
        sector = EXCLUDED.sector,
        thesis = EXCLUDED.thesis,
        entry_price = EXCLUDED.entry_price,
        target_price = EXCLUDED.target_price,
        stop_loss = EXCLUDED.stop_loss,
        grade = EXCLUDED.grade,
        council = EXCLUDED.council,
        status = EXCLUDED.status,
        notes = EXCLUDED.notes
    """
    record.setdefault("added_at", _now_iso())
    with _get_cursor() as cur:
        cur.execute(sql, record)


# -- CRUD: plays --------------------------------------------------------------

def get_plays():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM plays ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]


def insert_play(record: dict):
    sql = """
    INSERT INTO plays (ticker, action, shares, price, notional, broker, reason, grade_at_entry, council_at_entry, notes, closed, exit_price, exit_date, pnl, pnl_pct)
    VALUES (%(ticker)s, %(action)s, %(shares)s, %(price)s, %(notional)s, %(broker)s, %(reason)s, %(grade_at_entry)s, %(council_at_entry)s, %(notes)s, %(closed)s, %(exit_price)s, %(exit_date)s, %(pnl)s, %(pnl_pct)s)
    RETURNING id
    """
    with _get_cursor() as cur:
        cur.execute(sql, record)
        return cur.fetchone()["id"]


# -- CRUD: alerts -------------------------------------------------------------

def get_alerts():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM alerts ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]


# -- CRUD: sector_momentum ----------------------------------------------------

def get_sector_momentum():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM sector_momentum")
        return [dict(r) for r in cur.fetchall()]


def upsert_sector_momentum(record: dict):
    sql = """
    INSERT INTO sector_momentum (sector, score, trend, top_tickers, updated_at)
    VALUES (%(sector)s, %(score)s, %(trend)s, %(top_tickers)s::jsonb, %(updated_at)s)
    ON CONFLICT (sector) DO UPDATE SET
        score = EXCLUDED.score,
        trend = EXCLUDED.trend,
        top_tickers = EXCLUDED.top_tickers,
        updated_at = EXCLUDED.updated_at
    """
    record["top_tickers"] = _to_jsonb(record.get("top_tickers", []))
    record.setdefault("updated_at", _now_iso())
    with _get_cursor() as cur:
        cur.execute(sql, record)


# -- CRUD: weather_patterns ---------------------------------------------------

def get_weather_patterns():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM weather_patterns")
        return [dict(r) for r in cur.fetchall()]


def insert_weather_pattern(record: dict):
    sql = """
    INSERT INTO weather_patterns (ticker, sector, pattern, confidence, expected_return, timeframe, updated_at)
    VALUES (%(ticker)s, %(sector)s, %(pattern)s, %(confidence)s, %(expected_return)s, %(timeframe)s, %(updated_at)s)
    """
    record.setdefault("updated_at", _now_iso())
    with _get_cursor() as cur:
        cur.execute(sql, record)


# -- CRUD: macro_signals ------------------------------------------------------

def get_macro_signals():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM macro_signals")
        return [dict(r) for r in cur.fetchall()]


def upsert_macro_signal(record: dict):
    sql = """
    INSERT INTO macro_signals (signal_name, signal_type, value, direction, confidence, notes, updated_at)
    VALUES (%(signal_name)s, %(signal_type)s, %(value)s, %(direction)s, %(confidence)s, %(notes)s, %(updated_at)s)
    ON CONFLICT (signal_name) DO UPDATE SET
        signal_type = EXCLUDED.signal_type,
        value = EXCLUDED.value,
        direction = EXCLUDED.direction,
        confidence = EXCLUDED.confidence,
        notes = EXCLUDED.notes,
        updated_at = EXCLUDED.updated_at
    """
    record.setdefault("updated_at", _now_iso())
    with _get_cursor() as cur:
        cur.execute(sql, record)


# -- CRUD: technical_signals --------------------------------------------------

def get_technical_signals():
    with _get_cursor() as cur:
        cur.execute("SELECT * FROM technical_signals")
        return [dict(r) for r in cur.fetchall()]


def upsert_technical_signal(record: dict):
    sql = """
    INSERT INTO technical_signals (ticker, score, signals, updated_at)
    VALUES (%(ticker)s, %(score)s, %(signals)s::jsonb, %(updated_at)s)
    ON CONFLICT (ticker) DO UPDATE SET
        score = EXCLUDED.score,
        signals = EXCLUDED.signals,
        updated_at = EXCLUDED.updated_at
    """
    record["signals"] = _to_jsonb(record.get("signals", []))
    record.setdefault("updated_at", _now_iso())
    with _get_cursor() as cur:
        cur.execute(sql, record)


# -- Batch helpers ------------------------------------------------------------

def sync_positions(positions_data):
    """Batch upsert positions."""
    count = 0
    for p in positions_data:
        if p.get("ticker") == "TOTAL":
            continue
        upsert_position({
            "ticker": p.get("ticker", ""),
            "shares": p.get("shares", 0) or p.get("quantity", 0),
            "avg_cost": p.get("cost_basis", 0) or p.get("avg_cost", 0),
            "live_price": p.get("live_price", 0),
            "live_value": p.get("live_value", p.get("value", 0)),
            "grade": p.get("grade", 0),
            "council": p.get("council", ""),
            "brokers": p.get("brokers", []),
            "sector": p.get("sector", ""),
        })
        count += 1
    return count


def sync_watchlist(watchlist_data):
    """Batch upsert watchlist."""
    count = 0
    for w in watchlist_data:
        sources = w.get("sources", [])
        notes = " | ".join(sources) if sources else ""
        upsert_watchlist({
            "ticker": w.get("ticker", ""),
            "name": w.get("ticker", ""),
            "sector": w.get("sector", ""),
            "thesis": notes[:200],
            "entry_price": w.get("buy_zone", 0),
            "target_price": w.get("target_1", 0),
            "stop_loss": w.get("stop_loss", 0),
            "grade": w.get("grade", 0),
            "council": w.get("signal", ""),
            "status": "watching",
            "notes": notes[:500],
        })
        count += 1
    return count


def sync_play(play_dict):
    """Insert a single play."""
    return insert_play({
        "ticker": play_dict["ticker"],
        "action": play_dict["action"],
        "shares": play_dict["shares"],
        "price": play_dict["price"],
        "notional": play_dict.get("notional", play_dict["shares"] * play_dict["price"]),
        "broker": play_dict.get("broker", ""),
        "reason": play_dict.get("reason", ""),
        "grade_at_entry": play_dict.get("grade_at_entry", 0),
        "council_at_entry": play_dict.get("council_at_entry", ""),
        "notes": play_dict.get("notes", ""),
        "closed": play_dict.get("closed", False),
        "exit_price": play_dict.get("exit_price"),
        "exit_date": play_dict.get("exit_date"),
        "pnl": play_dict.get("pnl"),
        "pnl_pct": play_dict.get("pnl_pct"),
    })


def snapshot_to_history(date_str=None):
    """Copy current positions to position_history."""
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    positions = get_positions()
    with _get_cursor() as cur:
        for p in positions:
            cur.execute("""
                INSERT INTO position_history (ticker, date, shares, price, value, grade, council)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticker, date) DO UPDATE SET
                    shares = EXCLUDED.shares,
                    price = EXCLUDED.price,
                    value = EXCLUDED.value,
                    grade = EXCLUDED.grade,
                    council = EXCLUDED.council
            """, (
                p["ticker"], date_str, p.get("shares", 0), p.get("live_price", 0),
                p.get("live_value", 0), p.get("grade", 0), p.get("council", "")
            ))
    return len(positions)


# -- Back-compat: get_client --------------------------------------------------

class _FakeSupabase:
    """Minimal wrapper that looks like Supabase client for back-compat."""

    def table(self, name):
        return _FakeTable(name)


class _FakeTable:
    def __init__(self, name):
        self._name = name
        self._filters = []
        self._select_cols = "*"
        self._order_col = None
        self._order_desc = False

    def select(self, cols="*"):
        self._select_cols = cols
        return self

    def eq(self, col, val):
        self._filters.append(("eq", col, val))
        return self

    def order(self, col, desc=False):
        self._order_col = col
        self._order_desc = desc
        return self

    def insert(self, record):
        self._insert_record = record
        return self

    def upsert(self, record, on_conflict=None):
        self._upsert_record = record
        return self

    def update(self, fields):
        self._update_fields = fields
        return self

    def delete(self):
        return self

    def execute(self):
        # Route select queries
        if not hasattr(self, "_insert_record") and not hasattr(self, "_upsert_record") and not hasattr(self, "_update_fields"):
            if self._name == "positions":
                if self._order_col == "live_value" and self._order_desc:
                    return type("R", (), {"data": get_positions()})()
                if any(f[1] == "ticker" for f in self._filters):
                    ticker = next(f[2] for f in self._filters if f[1] == "ticker")
                    row = get_position_by_ticker(ticker)
                    return type("R", (), {"data": [row] if row else []})()
                return type("R", (), {"data": get_positions()})()

            if self._name == "watchlist":
                return type("R", (), {"data": get_watchlist()})()

            if self._name == "plays":
                return type("R", (), {"data": get_plays()})()

            if self._name == "alerts":
                return type("R", (), {"data": get_alerts()})()

            if self._name == "sector_momentum":
                return type("R", (), {"data": get_sector_momentum()})()

            if self._name == "weather_patterns":
                return type("R", (), {"data": get_weather_patterns()})()

            if self._name == "macro_signals":
                return type("R", (), {"data": get_macro_signals()})()

            if self._name == "technical_signals":
                return type("R", (), {"data": get_technical_signals()})()

            return type("R", (), {"data": []})()

        # Handle insert
        if hasattr(self, "_insert_record"):
            if self._name == "plays":
                insert_play(self._insert_record)
            elif self._name == "weather_patterns":
                insert_weather_pattern(self._insert_record)
            return type("R", (), {"data": [self._insert_record]})()

        # Handle upsert
        if hasattr(self, "_upsert_record"):
            if self._name == "positions":
                if isinstance(self._upsert_record, list):
                    for r in self._upsert_record:
                        upsert_position(r)
                else:
                    upsert_position(self._upsert_record)
            elif self._name == "watchlist":
                if isinstance(self._upsert_record, list):
                    for r in self._upsert_record:
                        upsert_watchlist(r)
                else:
                    upsert_watchlist(self._upsert_record)
            elif self._name == "sector_momentum":
                upsert_sector_momentum(self._upsert_record)
            elif self._name == "macro_signals":
                upsert_macro_signal(self._upsert_record)
            elif self._name == "technical_signals":
                upsert_technical_signal(self._upsert_record)
            return type("R", (), {"data": [self._upsert_record]})()

        # Handle update
        if hasattr(self, "_update_fields"):
            if any(f[1] == "ticker" for f in self._filters):
                ticker = next(f[2] for f in self._filters if f[1] == "ticker")
                update_position(ticker, self._update_fields)
            return type("R", (), {"data": [self._update_fields]})()

        return type("R", (), {"data": []})()


def get_client():
    """Return a fake Supabase client that routes to PostgreSQL."""
    return _FakeSupabase()


# -- Test ----------------------------------------------------------------------

if __name__ == "__main__":
    print("Testing PostgreSQL sync...")
    positions = get_positions()
    print(f"Loaded {len(positions)} positions from PostgreSQL")
    plays = get_plays()
    print(f"Loaded {len(plays)} plays from PostgreSQL")
