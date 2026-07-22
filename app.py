from pathlib import Path
from datetime import datetime
import os
import subprocess
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import load_settings
from auth import require_login
from engine import (
    enrich_market,
    regime_engine,
    specialist_committee,
    portfolio_analysis,
    build_decision,
    stress_scenarios,
)
from storage import save_decision, decision_history, refresh_history
from report_builder import build_pdf

ROOT = Path(__file__).resolve().parent
load_settings()

st.set_page_config(
    page_title=os.getenv("APP_TITLE", "Global Capital Rotation CIO V2"),
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
require_login()

st.markdown(
    """
<style>
:root {
  --ink:#111827; --navy:#10263f; --blue:#315b86; --gold:#b89245;
  --slate:#64748b; --line:#e5eaf0; --panel:#f7f9fc; --good:#16794b;
  --warn:#a16207; --bad:#b42318;
}
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.block-container {max-width:1320px; padding-top:1rem; padding-bottom:5rem;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0f2238 0%,#152f4d 100%);}
[data-testid="stSidebar"] * {color:white;}
[data-testid="stSidebar"] .stRadio label {padding:.42rem .55rem;border-radius:10px;}
[data-testid="stSidebar"] .stRadio label:hover {background:rgba(255,255,255,.08);}
.hero {background:linear-gradient(135deg,#10263f 0%,#315b86 70%,#567da6 100%);color:white;border-radius:22px;padding:22px 22px 20px;margin-bottom:14px;box-shadow:0 12px 28px rgba(16,38,63,.15);}
.hero-kicker {font-size:.78rem;text-transform:uppercase;letter-spacing:.13em;opacity:.78;font-weight:700;}
.hero-title {font-size:2rem;font-weight:760;line-height:1.12;margin:.35rem 0 .5rem;}
.hero-copy {font-size:1rem;line-height:1.55;opacity:.94;max-width:920px;}
.card {background:white;border:1px solid var(--line);border-radius:18px;padding:17px;box-shadow:0 4px 14px rgba(15,34,56,.045);height:100%;}
.card-label {font-size:.72rem;text-transform:uppercase;letter-spacing:.09em;color:var(--slate);font-weight:750;}
.card-value {font-size:1.45rem;line-height:1.15;font-weight:760;color:var(--navy);margin-top:.35rem;}
.card-note {font-size:.82rem;color:var(--slate);margin-top:.45rem;line-height:1.35;}
.action-up {border-top:5px solid #168a55;} .action-flat {border-top:5px solid #315b86;} .action-down {border-top:5px solid #b45309;}
.chip {display:inline-block;padding:.28rem .62rem;border-radius:999px;background:#eef3f8;color:#315b86;font-size:.76rem;font-weight:700;margin-right:.35rem;}
.section-title {font-size:1.12rem;font-weight:760;color:var(--navy);margin:1.2rem 0 .55rem;}
.signal-row {display:flex;justify-content:space-between;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid var(--line);}
.signal-row:last-child {border-bottom:0;}
.score-good {color:var(--good);font-weight:750;} .score-warn {color:var(--warn);font-weight:750;} .score-bad {color:var(--bad);font-weight:750;}
.notice {background:#f1f5f9;border-left:4px solid #315b86;border-radius:12px;padding:12px 14px;color:#334155;font-size:.86rem;}
[data-testid="stMetric"] {background:white;border:1px solid var(--line);border-radius:16px;padding:13px;box-shadow:0 4px 12px rgba(15,34,56,.035);}
.stButton>button, .stDownloadButton>button {border-radius:12px;min-height:44px;font-weight:700;}
div[data-testid="stExpander"] {border:1px solid var(--line);border-radius:14px;overflow:hidden;}
@media (max-width: 760px) {
  .block-container {padding-left:.8rem;padding-right:.8rem;padding-top:.55rem;}
  .hero {padding:18px;border-radius:18px;}
  .hero-title {font-size:1.65rem;}
  .hero-copy {font-size:.91rem;}
  .card-value {font-size:1.2rem;}
  [data-testid="stMetricValue"] {font-size:1.3rem;}
}
</style>
""",
    unsafe_allow_html=True,
)

@st.cache_data(ttl=900)
def load_market():
    return enrich_market(pd.read_csv(ROOT / "current_snapshot.csv"))


def load_holdings():
    path = ROOT / "portfolio_holdings.csv"
    if not path.exists():
        path = ROOT / "portfolio_holdings_template.csv"
    return pd.read_csv(path)


def pct_class(value):
    return "score-good" if value >= 68 else "score-warn" if value >= 48 else "score-bad"


market = load_market()
regime = regime_engine(market)
specialists = specialist_committee(market, regime)
holdings = load_holdings()
portfolio, portfolio_summary = portfolio_analysis(holdings, market)
decision = build_decision(market, regime, specialists, portfolio_summary)
scenarios = stress_scenarios(portfolio)

if "v2_decision_saved" not in st.session_state:
    try:
        save_decision(decision)
    except Exception:
        pass
    st.session_state.v2_decision_saved = True

with st.sidebar:
    st.markdown("## ◈ Capital CIO")
    st.caption("Enhanced Streamlit V2")
    page = st.radio(
        "Navigation",
        [
            "Command Center",
            "My Portfolio",
            "Capital Rotation",
            "Risk & Regime",
            "CIO Committee",
            "Reports",
            "System Health",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("CURRENT POSTURE")
    st.markdown(f"**{regime['posture']}**")
    st.caption(f"Confidence {regime['confidence']:.0f}%")
    st.caption(datetime.now().strftime("Updated %b %d • %I:%M %p"))

if page == "Command Center":
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-kicker">Chief Investment Officer Command Center</div>
  <div class="hero-title">{regime['regime']}</div>
  <div class="hero-copy">{decision['brief']}</div>
  <div style="margin-top:14px"><span class="chip">Posture: {regime['posture']}</span><span class="chip">Confidence: {regime['confidence']:.0f}%</span><span class="chip">Risk: {regime['risk_score']:.0f}/100</span></div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Regime score", f"{regime['composite']:.0f}/100")
    c2.metric("Committee agreement", f"{decision['specialist_agreement']:.0f}%")
    c3.metric("Portfolio value", f"${portfolio_summary['total']:,.0f}")
    c4.metric("Diversification", f"{portfolio_summary['diversification']:.0f}/100")

    st.markdown('<div class="section-title">CIO action map</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown(f'<div class="card action-up"><div class="card-label">Increase consideration</div><div class="card-value">{decision["increase"]}</div><div class="card-note">Strongest current risk-adjusted leadership.</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="card action-flat"><div class="card-label">Maintain</div><div class="card-value">{decision["maintain"]}</div><div class="card-note">Core exposure remains compatible with the current regime.</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="card action-down"><div class="card-label">Reduce consideration</div><div class="card-value">{decision["reduce"]}</div><div class="card-note">Weakest current risk-adjusted profile; review concentration.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Leadership board</div>', unsafe_allow_html=True)
    top = market.sort_values("risk_adjusted_score", ascending=False).head(7)
    fig = px.bar(
        top.sort_values("risk_adjusted_score"),
        x="risk_adjusted_score",
        y="group",
        orientation="h",
        text="risk_adjusted_score",
        labels={"risk_adjusted_score": "CIO score", "group": ""},
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_layout(height=370, margin=dict(l=0, r=30, t=5, b=0), xaxis_range=[0, 105], showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">What needs attention</div>', unsafe_allow_html=True)
    watch = market.sort_values("risk_adjusted_score").head(3)
    for _, row in watch.iterrows():
        st.markdown(f"**{row['group']}** — {row['cio_view']} · score {row['risk_adjusted_score']:.0f} · trend {row['trend']}")

elif page == "My Portfolio":
    st.markdown("## My Portfolio")
    st.caption("Edit holdings, examine concentration, and compare current weights with the CIO model.")

    editor = st.data_editor(
        holdings,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "market_value": st.column_config.NumberColumn("Market value", format="$%.2f"),
            "cost_basis": st.column_config.NumberColumn("Cost basis", format="$%.2f"),
            "max_weight": st.column_config.NumberColumn("Max weight", format="%.2f"),
        },
    )
    if st.button("Save portfolio", type="primary", use_container_width=True):
        editor.to_csv(ROOT / "portfolio_holdings.csv", index=False)
        st.cache_data.clear()
        st.success("Portfolio saved.")
        st.rerun()

    analyzed, summary = portfolio_analysis(editor, market)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio value", f"${summary['total']:,.0f}")
    c2.metric("Unrealized gain/loss", f"${summary['gain_loss']:,.0f}")
    c3.metric("Concentration", f"{summary['concentration']:.1f}")
    c4.metric("Largest holding", summary["largest_holding"])

    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Allocation")
        fig = px.pie(analyzed, values="market_value", names="ticker", hole=.58)
        fig.update_layout(height=390, margin=dict(l=0, r=0, t=0, b=0), legend_orientation="h")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### Risk contribution")
        risk_view = analyzed.sort_values("risk_contribution", ascending=False)
        fig = px.bar(risk_view, x="ticker", y="risk_contribution", labels={"risk_contribution": "Risk contribution", "ticker": ""})
        fig.update_layout(height=390, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Model-alignment considerations")
    display = analyzed[["ticker", "weight", "target_weight", "dollar_adjustment", "suggested_action", "cio_view", "risk_adjusted_score"]]
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "weight": st.column_config.ProgressColumn("Current", format="%.1%%", min_value=0, max_value=1),
            "target_weight": st.column_config.ProgressColumn("Model target", format="%.1%%", min_value=0, max_value=1),
            "dollar_adjustment": st.column_config.NumberColumn("Estimated adjustment", format="$%.0f"),
            "risk_adjusted_score": st.column_config.NumberColumn("CIO score", format="%.0f"),
        },
    )
    st.markdown('<div class="notice">Model targets are research considerations, not instructions to buy or sell.</div>', unsafe_allow_html=True)

elif page == "Capital Rotation":
    st.markdown("## Capital Rotation")
    st.caption("Ranked leadership across asset classes, sectors, and industries.")
    universe = st.segmented_control("Universe", ["All", "Asset Class", "Sector", "Industry"], default="All")
    view = market if universe == "All" else market[market["level"] == universe]

    for _, row in view.sort_values("rank").iterrows():
        with st.expander(f"#{int(row['rank'])}  {row['group']}  •  {row['cio_view']}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CIO score", f"{row['risk_adjusted_score']:.0f}")
            c2.metric("3M momentum", f"{row['momentum_3m']:.1f}%")
            c3.metric("Breadth", f"{row['breadth']:.0f}")
            c4.metric("Flow", f"{row['flow']:.0f}")
            st.write(f"**Trend:** {row['trend']}  ·  **Volatility:** {row['volatility']:.1f}%  ·  **Level:** {row['level']}")
            gauge = go.Figure(go.Indicator(mode="gauge+number", value=float(row["risk_adjusted_score"]), gauge={"axis": {"range": [0, 100]}}))
            gauge.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=0))
            st.plotly_chart(gauge, use_container_width=True)

    with st.expander("Advanced ranking table"):
        st.dataframe(view, use_container_width=True, hide_index=True)

elif page == "Risk & Regime":
    st.markdown("## Risk & Regime")
    st.markdown(
        f'<div class="hero"><div class="hero-kicker">Current environment</div><div class="hero-title">{regime["regime"]}</div><div class="hero-copy">Portfolio posture: {regime["posture"]}. Model confidence is {regime["confidence"]:.0f}%.</div></div>',
        unsafe_allow_html=True,
    )

    components = pd.DataFrame({"Component": list(regime["components"].keys()), "Score": list(regime["components"].values())})
    fig = px.bar(components, x="Score", y="Component", orientation="h", range_x=[0, 100], text="Score")
    fig.update_layout(height=340, margin=dict(l=0, r=15, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Portfolio stress laboratory")
    st.dataframe(
        scenarios,
        use_container_width=True,
        hide_index=True,
        column_config={
            "estimated_return": st.column_config.NumberColumn("Estimated return", format="%.1%%"),
            "estimated_dollar_impact": st.column_config.NumberColumn("Estimated impact", format="$%.0f"),
        },
    )
    st.markdown('<div class="notice">Stress results are simplified estimates used to reveal sensitivity. They are not forecasts.</div>', unsafe_allow_html=True)

elif page == "CIO Committee":
    st.markdown("## CIO Committee")
    st.caption("Numerical specialists vote independently; narrative explains their combined conclusion.")
    for _, row in specialists.iterrows():
        cls = pct_class(float(row["score"]))
        st.markdown(
            f'<div class="card"><div class="signal-row"><div><div class="card-label">{row["specialist"]} specialist</div><div class="card-value">{row["view"]}</div></div><div class="{cls}">{row["score"]:.0f}/100</div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("### Committee conclusion")
    st.info(decision["brief"])
    st.metric("Specialist agreement", f"{decision['specialist_agreement']:.0f}%")

elif page == "Reports":
    st.markdown("## CIO Reports")
    (ROOT / "reports").mkdir(exist_ok=True)
    pdf_path = ROOT / "reports" / "latest_cio_report.pdf"
    build_pdf(pdf_path, decision, regime, portfolio_summary)
    with open(pdf_path, "rb") as file:
        st.download_button(
            "Download current CIO report",
            file,
            file_name="Global_Capital_Rotation_CIO_V2_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    st.markdown(
        f'<div class="card"><div class="card-label">Executive summary</div><div class="card-value">{decision["brief"]}</div><div class="card-note">Regime: {regime["regime"]} · Posture: {regime["posture"]} · Confidence: {regime["confidence"]:.0f}%</div></div>',
        unsafe_allow_html=True,
    )

    try:
        history = decision_history()
        if len(history):
            st.markdown("### Decision history")
            st.dataframe(history[["created_at", "regime", "posture", "confidence", "risk_score", "brief"]], use_container_width=True, hide_index=True)
    except Exception as exc:
        st.caption(f"Decision history is not yet available: {exc}")

elif page == "System Health":
    st.markdown("## System Health")
    checks = pd.DataFrame(
        [
            ["V2 application", "Ready", "Polished command-center interface loaded"],
            ["FRED key", "Ready" if os.getenv("FRED_API_KEY") else "Missing", "Stored in Streamlit Secrets"],
            ["Market snapshot", "Ready" if (ROOT / "current_snapshot.csv").exists() else "Missing", "Primary market input"],
            ["Portfolio", "Ready" if (ROOT / "portfolio_holdings.csv").exists() else "Template", "Editable holdings input"],
            ["Authentication", "Enabled" if os.getenv("APP_PASSWORD") else "Open", "Controlled by APP_PASSWORD"],
            ["PDF reports", "Ready", "ReportLab renderer"],
        ],
        columns=["Component", "Status", "Details"],
    )
    st.dataframe(checks, use_container_width=True, hide_index=True)

    if st.button("Refresh live market data", type="primary", use_container_width=True):
        with st.spinner("Refreshing market data…"):
            result = subprocess.run([sys.executable, str(ROOT / "refresh_all.py")], capture_output=True, text=True)
        if result.returncode == 0:
            st.cache_data.clear()
            st.success("Market refresh completed.")
        else:
            st.error(result.stderr[-1800:] or "Refresh failed without an error message.")

    try:
        logs = refresh_history()
        if len(logs):
            st.markdown("### Refresh history")
            st.dataframe(logs, use_container_width=True, hide_index=True)
    except Exception:
        pass

st.divider()
st.caption("Research and decision support only. The platform does not place trades, guarantee outcomes, or replace personalized financial advice.")
