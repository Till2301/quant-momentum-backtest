import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt
import os

# =========================
# Konfiguration
# =========================
TICKERS = ["SPY", "EFA", "IEF", "BIL", "QQQ", "DIA"]
START = dt.datetime(2010, 1, 1)
END = dt.datetime.now()
LOOKBACK_LIST = [3, 6, 12]  # Momentum Lookbacks in Monaten
TOP_N = 3
REBALANCE_FREQ = "M"
RISK_FREE_ANNUAL = 0.015

# Ordner für Plots erstellen
os.makedirs("plots", exist_ok=True)

# =========================
# Daten laden (Stooq)
# =========================
def get_stooq_data(symbol):
    try:
        df = web.DataReader(symbol + ".US", "stooq", START, END)
        df = df.sort_index()
        return df["Close"]
    except Exception as e:
        print(f"Fehler bei {symbol}: {e}")
        return None

prices = pd.DataFrame({t: get_stooq_data(t) for t in TICKERS})
prices = prices.dropna(how="all").sort_index()
prices_m = prices.resample("M").last()
rets_m = prices_m.pct_change().dropna()

# =========================
# Kennzahlen
# =========================
def annualize_return(r, periods=12):
    return (1 + r).prod() ** (1 / (len(r)/periods)) - 1

def annualize_vol(r, periods=12):
    return r.std() * np.sqrt(periods)

def sharpe_ratio(r, rf=RISK_FREE_ANNUAL, periods=12):
    excess = r - rf/periods
    return annualize_return(excess, periods)/annualize_vol(excess, periods)

# =========================
# Momentum Backtests
# =========================
results = {}

for lookback in LOOKBACK_LIST:
    mom = prices_m.pct_change(lookback).shift(1)
    weights = pd.DataFrame(0.0, index=prices_m.index, columns=prices_m.columns)
    for date in prices_m.index:
        if date not in mom.index:
            continue
        top_assets = mom.loc[date].nlargest(TOP_N).index
        weights.loc[date, top_assets] = 1.0 / len(top_assets)
    port_rets = (weights.shift(1) * rets_m).sum(axis=1)
    results[f"{lookback}M"] = port_rets

bench_rets = rets_m["SPY"]

# =========================
# Kennzahlen & Summary
# =========================
summary = []
for name, r in results.items():
    summary.append({
        "Strategy": f"Momentum {name}",
        "CAGR": annualize_return(r),
        "Vol": annualize_vol(r),
        "Sharpe": sharpe_ratio(r)
    })

summary.append({
    "Strategy": "Buy-and-Hold SPY",
    "CAGR": annualize_return(bench_rets),
    "Vol": annualize_vol(bench_rets),
    "Sharpe": sharpe_ratio(bench_rets)
})

df_summary = pd.DataFrame(summary)
print("\n=== Strategie-Vergleich ===")
print(df_summary)

# =========================
# Equity Curves plotten & speichern
# =========================
plt.figure(figsize=(12,6))
for name, r in results.items():
    (1 + r).cumprod().plot(label=f"Momentum {name}")
(1 + bench_rets).cumprod().plot(label="Buy-and-Hold SPY", linewidth=2, color="black")
plt.title("Equity Curves: Momentum Strategien vs. Buy-and-Hold")
plt.ylabel("Portfolio Value")
plt.xlabel("Datum")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/equity_curves.png")
plt.close()

# Einzelplots pro Strategie
for name, r in results.items():
    plt.figure(figsize=(10,4))
    (1 + r).cumprod().plot(title=f"Equity Curve: Momentum {name}")
    plt.ylabel("Portfolio Value")
    plt.xlabel("Datum")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"plots/equity_{name}.png")
    plt.close()

# =========================
# Ergebnisse exportieren
# =========================
df_summary.to_csv("momentum_summary.csv", index=False)
for name, r in results.items():
    r.cumsum().to_csv(f"equity_{name}.csv")
print("\n✅ CSVs und Plots wurden gespeichert. Ordner 'plots' enthält alle Grafiken.")
