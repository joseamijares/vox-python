#!/usr/bin/env python3
"""
Daily update script — run this every morning.

What it does:
    1. Updates all position prices
    2. Checks for alerts (stop loss, daily moves)
    3. Sends Telegram notifications
    4. Generates daily report

Usage:
    python scripts/run_daily_update.py

Cron setup (every day at 9 AM):
    0 9 * * * cd ~/dev/vox-python && python scripts/run_daily_update.py
"""

import sys
import os

sys.path.insert(0, 'src')

# Load .env
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k, v = line.strip().split('=', 1)
            os.environ[k] = v

from sync.vox_supabase_sync import get_client
from pricing.updater import update_all_prices
from alerts.notifier import run_daily_alerts


def main():
    print("=" * 60)
    print("VOX DAILY UPDATE")
    print("=" * 60)
    print()
    
    # Connect to Supabase
    sb = get_client()  # was: create_client(os.environ['DATABASE_URL'], os.environ['DATABASE_URL'])
    
    # Update prices
    print("📊 Updating prices...")
    price_result = update_all_prices(sb)
    print(f"  ✅ Updated: {price_result['updated']}")
    print(f"  ❌ Failed: {price_result['failed']}")
    print()
    
    # Check alerts
    print("🔍 Checking alerts...")
    alert_result = run_daily_alerts(sb)
    print(f"  Alerts found: {alert_result['alerts_found']}")
    print(f"  Telegram sent: {alert_result['telegram_sent']}")
    print()
    
    # Summary
    print("=" * 60)
    print("DAILY UPDATE COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
