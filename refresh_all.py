
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf
from storage import log_refresh

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "current_snapshot.csv"

def refresh():
    df = pd.read_csv(SNAPSHOT)
    tickers = [t for t in df["ticker"] if t != "CASH"]
    try:
        px = yf.download(tickers, period="1y", auto_adjust=True, progress=False, group_by="ticker", threads=True)
        rows = []
        for _, r in df.iterrows():
            t = r["ticker"]
            if t == "CASH":
                rows.append(r)
                continue
            try:
                s = px[t]["Close"].dropna() if isinstance(px.columns, pd.MultiIndex) else px["Close"].dropna()
                if len(s) >= 2:
                    r["price"] = float(s.iloc[-1])
                    r["move_1d"] = float((s.iloc[-1]/s.iloc[-2]-1)*100)
                    if len(s) >= 63:
                        r["momentum_3m"] = float((s.iloc[-1]/s.iloc[-63]-1)*100)
                    if len(s) >= 252:
                        r["momentum_12m"] = float((s.iloc[-1]/s.iloc[-252]-1)*100)
                    r["volatility"] = float(s.pct_change().dropna().std()*252**0.5*100)
            except Exception:
                pass
            rows.append(r)
        out = pd.DataFrame(rows)
        out.to_csv(SNAPSHOT, index=False)
        log_refresh("success", f"Updated {len(out)} market groups at {datetime.now(timezone.utc).isoformat()}")
        print("Refresh complete.")
    except Exception as e:
        log_refresh("failed", str(e))
        raise

if __name__ == "__main__":
    refresh()
