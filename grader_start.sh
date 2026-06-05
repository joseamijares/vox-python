#!/bin/bash
# VOX Grader Service — Integrated 6-Layer Pipeline
# Runs: Broker sync → Layer analysis → Integrated grading

cd /app
export PYTHONPATH=src:$PYTHONPATH

echo "🚀 VOX Integrated Grader Starting..."
echo "⏰ $(date)"
echo ""

# Step 1: Sync brokers (eToro API + manual JSON)
echo "📡 Step 1: Broker Sync..."
python3 src/brokers/etoro_sync.py 2>&1 || echo "  ⚠️ eToro sync had issues"
python3 src/brokers/gbm_sync.py 2>&1 || echo "  ⚠️ GBM sync had issues"
python3 src/brokers/binance_sync.py 2>&1 || echo "  ⚠️ Binance sync had issues"

# Step 2: Run integrated 6-layer grading
echo ""
echo "🧠 Step 2: Integrated 6-Layer Grading..."
python3 src/layers/integrated_grader.py

echo ""
echo "✅ Pipeline complete. Sleeping until next run..."
# Keep container alive for Railway health checks
sleep 3600
