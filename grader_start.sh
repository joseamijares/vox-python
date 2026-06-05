#!/bin/bash
# Grader service start script
# Runs the daily sync + grading pipeline

cd /app

export PYTHONPATH=src:$PYTHONPATH

echo "🚀 VOX Grader Service Starting..."
echo "⏰ Running daily sync + grade pipeline..."

# Run the full pipeline
python3 scripts/auto_grade_positions.py

echo "✅ Grading complete. Service will restart on next schedule."
