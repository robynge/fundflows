# ETF Fund Flows Analysis

A Streamlit dashboard comparing ARK Funds performance against Top 100 ETFs.

## Features

- **ARK vs Top 100 Inflows**: Compare ARK funds against top 100 ETF inflows
- **ARK vs Top 100 Outflows**: Compare ARK funds against top 100 ETF outflows
- **Interactive Controls**: Toggle between cumulative/daily flows and absolute/percentage values
- **Download Data**: Export datasets as CSV files

## Live Demo

[View on Streamlit Cloud](https://your-app-url.streamlit.app)

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Source

Data from `ETF_Fund_Flows_5016_Complete.xlsx` containing:
- ARK Funds daily flows (ARKK, ARKF, ARKB, ARKX, ARKG, ARKQ)
- Top 100 ETF inflows
- Top 100 ETF outflows
