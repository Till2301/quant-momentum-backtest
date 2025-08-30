# Quant-Finance Momentum Backtest

## Beschreibung
Dieses Projekt vergleicht Momentum-Strategien (Top-N Assets, Lookbacks 3, 6, 12 Monate) mit Buy-and-Hold (SPY) anhand historischer Kursdaten von Stooq.

## Funktionen
- Datenbeschaffung von Stooq
- Berechnung von Momentum-Scores
- Portfolio-Konstruktion & Backtest
- Kennzahlen: CAGR, Volatilität, Sharpe Ratio
- Equity Curves Visualisierung
- Export der Ergebnisse als CSV

## Installation
```bash
git clone <repo-url>
cd quant-momentum-backtest
pip install -r requirements.txt
python momentum_backtest.py
