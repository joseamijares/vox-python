#!/usr/bin/env python3
"""Recalculate grades for all watchlist stocks."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grading.engine import batch_grade
from sync.vox_supabase_sync import get_client
import json


def main():
    # Load watchlist from Supabase
    print("Loading watchlist from Supabase...")
    sb = get_client()
    resp = sb.table('watchlist').select('ticker').execute()
    tickers = [w['ticker'] for w in resp.data]
    
    print(f"Grading {len(tickers)} stocks...\n")
    results = batch_grade(tickers)
    
    # Update Supabase with new grades
    print("\nUpdating Supabase...")
    updated = 0
    for r in results:
        try:
            sb.table('watchlist').update({
                'grade': r.overall_grade,
                'council': r.council
            }).eq('ticker', r.ticker).execute()
            updated += 1
        except Exception as e:
            print(f"  ❌ {r.ticker}: {e}")
    
    print(f"\n✅ Updated {updated} grades in Supabase")
    
    # Also update positions
    print("\nUpdating portfolio positions...")
    pos_resp = sb.table('positions').select('ticker').execute()
    pos_tickers = [p['ticker'] for p in pos_resp.data]
    pos_results = batch_grade(pos_tickers)
    
    pos_updated = 0
    for r in pos_results:
        try:
            sb.table('positions').update({
                'grade': r.overall_grade,
                'council': r.council
            }).eq('ticker', r.ticker).execute()
            pos_updated += 1
        except Exception as e:
            print(f"  ❌ {r.ticker}: {e}")
    
    print(f"✅ Updated {pos_updated} positions in Supabase")
    
    # Print top 10
    print("\n🏆 TOP 10 WATCHLIST:")
    sorted_results = sorted(results, key=lambda x: x.overall_grade, reverse=True)
    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i:2d}. {r.ticker:6s} | Grade: {r.overall_grade:3d} | {r.council:12s} | {r.name[:30]}")


if __name__ == "__main__":
    main()
