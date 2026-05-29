#!/usr/bin/env python3
"""Recalculate grades for all watchlist stocks."""
import sys
sys.path.insert(0, "/Users/jos/dev/vox-python/src")

from grading.engine import batch_grade
import json

def main():
    # Load watchlist from JSON or Supabase
    watchlist_file = "/Users/jos/dev/vox-python/.hermes/scripts/vox_watchlist_current.json"
    
    try:
        with open(watchlist_file) as f:
            watchlist = json.load(f)
        tickers = [w["ticker"] for w in watchlist]
    except FileNotFoundError:
        print(f"Watchlist file not found: {watchlist_file}")
        print("Using test tickers...")
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMD", "META", "AMZN"]
    
    print(f"Grading {len(tickers)} stocks...\n")
    results = batch_grade(tickers)
    
    # Save results
    output = {
        "calculated_at": str(results[0].calculated_at) if results else "",
        "grades": [
            {
                "ticker": r.ticker,
                "name": r.name,
                "grade": r.overall_grade,
                "council": r.council,
                "technical": r.technical_score,
                "fundamental": r.fundamental_score,
                "sector": r.sector
            }
            for r in results
        ]
    }
    
    output_file = "/Users/jos/dev/vox-python/grades_output.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Grades saved to {output_file}")
    
    # Print top 10
    print("\n🏆 TOP 10 STOCKS:")
    sorted_results = sorted(results, key=lambda x: x.overall_grade, reverse=True)
    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i:2d}. {r.ticker:6s} | Grade: {r.overall_grade:3d} | {r.council:12s} | {r.name[:30]}")

if __name__ == "__main__":
    main()
