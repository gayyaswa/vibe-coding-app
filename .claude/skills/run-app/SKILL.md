---
description: Launch the Stock Portfolio Risk Analyzer Streamlit app and verify it's running
---

# Run: Stock Portfolio Risk Analyzer

## Launch

```bash
cd /Users/ayyaswamy/projects/vibe-coding-app
streamlit run app.py --server.headless true &
```

## Verify

Wait ~3 seconds, then check the server is up:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
```

Expected: `200`. The app serves at http://localhost:8501

## Notes

- To stop: `pkill -f "streamlit run"` or kill the background job.
- Sample portfolio loads automatically from `data/portfolio_sample.csv` on first load.
