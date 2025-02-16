#!/bin/bash

# Default values
STOP_ON_ERROR=false
PORT=8501

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --stop-on-error)
      STOP_ON_ERROR=true
      shift
      ;;
    --port)
      PORT="$2"
      shift
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Running tests..."
if [ "$STOP_ON_ERROR" = true ]; then
  # Run tests with immediate failure on error
  python -m pytest tests/ -v || exit 1
else
  # Run all tests regardless of failures
  python -m pytest tests/ -v
fi

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Starting Streamlit app on port $PORT..."
streamlit run demo/streamlit_app.py --server.port=$PORT \
  --server.address=0.0.0.0 --server.enableCORS=false \
  --server.enableXsrfProtection=false --server.baseUrlPath=''
