#!/usr/bin/env python3
"""Fix delisted stocks in watchlist — marks them as delisted and sets grade to 0."""
import sys
sys.path.insert(0, "/Users/jos/dev/vox-python/src")

from grading.delisted import validate_watchlist
import json

def main():
    # Load watchlist
    watchlist_file = "/Users/jos/dev/vox-python/.hermes/scripts/vox_watchlist_current.json"
    
    try:
        with open(watchlist_file) as f:
            watchlist = json.load(f)
        tickers = [w["ticker"] for w in watchlist]
    except FileNotFoundError:
        print(f"Watchlist file not found: {watchlist_file}")
        # Use known problematic tickers
        tickers = ["LILM", "SIDU", "SPIR", "MNTS", "HEMI"]
    
    # Validate all
    results = validate_watchlist(tickers)
    
    # Generate fix commands
    print("\n" + "="*60)
    print("FIX COMMANDS FOR SUPABASE:")
    print("="*60)
    
    for d in results["delisted"]:
        ticker = d["ticker"]
        print(f"\n-- Fix {ticker}")
        print(f"UPDATE watchlist SET status = 'delisted', grade = 0, council = 'STRONG_SELL' WHERE ticker = '{ticker}';")
    
    # Save report
    report = {
        "checked_at": str(datetime.utcnow()),
        "total_checked": results["total"],
        "delisted": [d["ticker"] for d in results["delisted"]],
        "valid": [v["ticker"] for v in results["valid"]]
    }
    
    with open("/Users/jos/dev/vox-python/delisted_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to delisted_report.json")
    print(f"\nRun the SQL commands above in your Supabase SQL Editor to fix the database.")

if __name__ == "__main__":
    from datetime import datetime
    main()
