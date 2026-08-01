#!/usr/bin/env bash
# ==============================================================================
# Western Hellenistic Horoscope RAG Execution Script
# ==============================================================================
# Usage:
#   ./run_western_rag.sh [Name] [Year] [Month] [Day] [Hour] [Minute] [City] [CountryCode]
# Default parameters:
#   User 1983 11 10 4 20 Georgsmarienhütte DE
# ==============================================================================

NAME="${1:-User}"
YEAR="${2:-1983}"
MONTH="${3:-11}"
DAY="${4:-10}"
HOUR="${5:-4}"
MINUTE="${6:-20}"
CITY="${7:-Georgsmarienhütte}"
COUNTRY="${8:-DE}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_BIN="${SCRIPT_DIR}/venv/bin/python"

if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "======================================================================"
echo "  Astra Western Hellenistic Astrology Engine & Classical RAG DB"
echo "======================================================================"
echo " Calculating Chart for: $NAME"
echo " Date & Time: $YEAR-$MONTH-$DAY $HOUR:$MINUTE"
echo " Location: $CITY, $COUNTRY"
echo "----------------------------------------------------------------------"

# 1. Generate Western Chart JSON
"$PYTHON_BIN" -c "
from western.generate_chart import generate_ai_json
generate_ai_json(
    name='$NAME',
    year=$YEAR,
    month=$MONTH,
    day=$DAY,
    hour=$HOUR,
    minute=$MINUTE,
    city='$CITY',
    country_code='$COUNTRY',
    output_filename='western/chart_context.json',
    silent=False
)
"

# 2. Run RAG Interpreter to query vector database
echo ""
echo "----------------------------------------------------------------------"
echo " Querying Local Vector DB (Chroma) for Classical Ground Truth..."
echo "----------------------------------------------------------------------"
"$PYTHON_BIN" rag/rag_interpreter.py

echo ""
echo "======================================================================"
echo " Execution Complete! Chart data saved to western/chart_context.json"
echo "======================================================================"
