#!/usr/bin/env python3
"""
Auto-grade all ungraded positions in Railway Postgres.
Runs the full 6-layer VOX grading engine (Python backend).
Called by cron or manually after eToro sync.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sync.vox_postgres_sync import get_positions, update_position, save_vox_grade
from grading.engine import calculate_grade


def auto_grade_all():
    """Grade all positions with grade=0 or grade IS NULL."""
    positions = get_positions()
    
    # Filter ungraded
    ungraded = [p for p in positions if p.get('grade') in (0, None, '')]
    
    if not ungraded:
        print("✅ No ungraded positions found")
        return 0
    
    print(f"🎯 Grading {len(ungraded)} ungraded positions...\n")
    
    graded = 0
    for pos in ungraded:
        ticker = pos['ticker']
        try:
            # Run full 6-layer VOX grading
            result = calculate_grade(ticker)
            
            # Update positions table
            update_position(ticker, {
                'grade': result.overall_grade,
                'council': result.council,
                'sector': result.sector or pos.get('sector', 'Technology')
            })
            
            # Save full breakdown to vox_grades
            save_vox_grade({
                'ticker': ticker,
                'name': result.name or ticker,
                'vox_grade': result.overall_grade,
                'previous_grade': pos.get('grade', 0) or 0,
                'action': result.council,
                'current_price': pos.get('live_price', 0),
                'stop_loss': pos.get('live_price', 0) * 0.85 if pos.get('live_price') else 0,
                'entry_point': pos.get('live_price', 0) * 0.95 if pos.get('live_price') else 0,
                'position_value': pos.get('live_value', 0),
                'shares': pos.get('shares', 0),
                'technical_score': result.technical_score,
                'fundamental_score': result.fundamental_score,
                'macro_score': 50,  # Placeholder — Phase 2
                'sector_score': 50,  # Placeholder — Phase 2
                'weather_score': 50,  # Placeholder — Phase 2
                'sentiment_score': result.sentiment_score,
                'catalysts': '; '.join(result.factors.get('technical', {}).get('mean_reversion_signals', [])[:3]),
                'weather_factors': 'Pending macro analysis'
            })
            
            print(f"  ✅ {ticker}: Grade {result.overall_grade} ({result.council}) | Tech:{result.technical_score} Fund:{result.fundamental_score}")
            graded += 1
            
        except Exception as e:
            print(f"  ❌ {ticker}: ERROR - {e}")
    
    print(f"\n✅ Graded {graded}/{len(ungraded)} positions")
    return graded


def grade_single(ticker: str):
    """Grade a single ticker manually."""
    from sync.vox_postgres_sync import get_position_by_ticker
    
    pos = get_position_by_ticker(ticker)
    if not pos:
        print(f"❌ {ticker} not found in positions")
        return
    
    result = calculate_grade(ticker)
    
    update_position(ticker, {
        'grade': result.overall_grade,
        'council': result.council,
        'sector': result.sector or pos.get('sector', 'Technology')
    })
    
    save_vox_grade({
        'ticker': ticker,
        'name': result.name or ticker,
        'vox_grade': result.overall_grade,
        'previous_grade': pos.get('grade', 0) or 0,
        'action': result.council,
        'current_price': pos.get('live_price', 0),
        'stop_loss': pos.get('live_price', 0) * 0.85 if pos.get('live_price') else 0,
        'entry_point': pos.get('live_price', 0) * 0.95 if pos.get('live_price') else 0,
        'position_value': pos.get('live_value', 0),
        'shares': pos.get('shares', 0),
        'technical_score': result.technical_score,
        'fundamental_score': result.fundamental_score,
        'macro_score': 50,
        'sector_score': 50,
        'weather_score': 50,
        'sentiment_score': result.sentiment_score,
        'catalysts': '; '.join(result.factors.get('technical', {}).get('mean_reversion_signals', [])[:3]),
        'weather_factors': 'Pending macro analysis'
    })
    
    print(f"✅ {ticker}: Grade {result.overall_grade} ({result.council})")
    print(f"   Technical: {result.technical_score} | Fundamental: {result.fundamental_score}")
    print(f"   Sector: {result.sector}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Grade single ticker
        grade_single(sys.argv[1])
    else:
        # Grade all ungraded
        auto_grade_all()
