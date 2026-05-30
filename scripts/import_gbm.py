#!/usr/bin/env python3
"""
GBM Portfolio Import Script

Usage:
    python scripts/import_gbm.py [MXN_RATE]

Example:
    python scripts/import_gbm.py           # Uses default rate (17.8)
    python scripts/import_gbm.py 18.2      # Override MXN/USD rate

Prerequisites:
    1. Export GBM portfolio as JSON
    2. Save to: ~/.hermes/scripts/gbm_main_portfolio.json
    3. (Optional) Save GBM USA to: ~/.hermes/scripts/gbm_usa_portfolio.json
"""

import sys
sys.path.insert(0, 'src')

from sync.gbm_importer import run_gbm_sync

if __name__ == '__main__':
    rate = float(sys.argv[1]) if len(sys.argv) > 1 else None
    if rate:
        run_gbm_sync(rate)
    else:
        run_gbm_sync()
