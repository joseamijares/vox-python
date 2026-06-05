#!/usr/bin/env python3
"""Fix delisted stocks in watchlist — marks them as delisted and sets grade to 0."""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grading.delisted import validate_watchlist
from sync.vox_postgres_sync import get_client
from datetime import datetime


def main():
    # Load watchlist from Postgres
    print("Loading watchlist from Postgres...")
    sb = get_client()
    resp = sb.table('watchlist').select('ticker').execute()
    tickers = [w['ticker'] for w in resp.data]
    
    # Validate all
    print(f"Checking {len(tickers)} stocks for delisted...")
    results = validate_watchlist(tickers)
    
    # Auto-fix delisted in Postgres
    print("\n" + "="*60)
    print("FIXING DELISTED STOCKS:")
    print("="*60)
    
    fixed = 0
    for d in results["delisted"]:
        ticker = d["ticker"]
        try:
            sb.table('watchlist').update({
                'status': 'delisted',
                'grade': 0,
                'council': 'STRONG_SELL'
            }).eq('ticker', ticker).execute()
            print(f"  ✅ Fixed {ticker} → delisted")
            fixed += 1
        except Exception as e:
            print(f"  ❌ {ticker}: {e}")
    
    print(f"\n✅ Fixed {fixed} delisted stocks")
    
    # Save report
    report = {
        "checked_at": str(datetime.utcnow()),
        "total_checked": results["total"],
        "delisted": [d["ticker"] for d in results["delisted"]],
        "valid": [v["ticker"] for v in results["valid"]]
    }
    
    report_file = os.path.join(os.path.dirname(__file__), '..', 'delisted_report.json')
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved to delisted_report.json")


if __name__ == "__main__":
    main()
