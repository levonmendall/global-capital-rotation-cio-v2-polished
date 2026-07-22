
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def build_pdf(path: Path, decision: dict, regime: dict, portfolio_summary: dict):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 60
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Global Capital Rotation CIO — V2 Report")
    y -= 28
    c.setFont("Helvetica", 10)
    c.drawString(50, y, datetime.now().strftime("%B %d, %Y %I:%M %p"))
    y -= 35

    sections = [
        ("Executive Summary", decision["brief"]),
        ("Market Regime", f"{regime['regime']} | Posture: {regime['posture']} | Confidence: {regime['confidence']}%"),
        ("Portfolio", f"Value: ${portfolio_summary['total']:,.0f} | Diversification: {portfolio_summary['diversification']}/100 | Largest holding: {portfolio_summary['largest_holding']}"),
        ("CIO Considerations", f"Increase consideration: {decision['increase']}. Maintain: {decision['maintain']}. Reduce consideration: {decision['reduce']}."),
        ("Important Notice", "This report is decision support, not personalized financial advice or an instruction to trade. Scenario results are estimates, not forecasts.")
    ]
    for title, body in sections:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        y -= 18
        c.setFont("Helvetica", 10)
        words = body.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if c.stringWidth(test, "Helvetica", 10) > width - 100:
                c.drawString(50, y, line)
                y -= 14
                line = word
            else:
                line = test
        if line:
            c.drawString(50, y, line)
            y -= 22
    c.save()
    return path
