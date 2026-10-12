"""Day 30 Final Practical Runner — Present Project to Mentors, Team Members & Technical Panel.

Executes:
1. Candidate & 30-Day Portfolio Overview (Shri Sanjaykumar V — VIT Vellore CGPA 9.12)
2. Multi-Stakeholder Briefing Verification (Mentors, Team Members, Technical Panel)
3. Live Dynamic 3-Way Reconciliation + 7-D Isolation Forest + Perturbation XAI Demonstration
4. Verification of Day 30 Career Deliverables (Updated Resume PDF/MD, Reflection Report PDF/MD, LinkedIn Guide, 90-Day Roadmap)
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi.testclient import TestClient
from app.main import app
from app.routers.audit import AUDIT_LEDGER


def main():
    client = TestClient(app)
    AUDIT_LEDGER.clear()

    print("\n" + "=" * 124)
    print("   LINKIFIC DAY 30 FINAL PRACTICAL — CAPSTONE PRESENTATION TO MENTORS, TEAM MEMBERS & TECHNICAL PANEL")
    print("   Candidate: Shri Sanjaykumar V (M.Tech Integrated SWE @ VIT Vellore | CGPA: 9.12/10.0)")
    print("   LinkedIn : https://www.linkedin.com/in/shri-sanjaykumar-v-588bab28a/")
    print("   GitHub   : https://github.com/Shri-Sanjaykumar/Linkific-Tasks")
    print("=" * 124)

    # 1. Portfolio Overview
    ov = client.get("/api/v1/portfolio/overview").json()
    print("\n[1] 30-DAY INTERNSHIP PROGRESSION MATRIX & PORTFOLIO OVERVIEW:")
    for phase in ov["progression_matrix"]:
        print(f"  * {phase['phase']:<20} | {phase['title']:<44} -> {phase['outcome']}")

    # 2. Panel Briefing Tracks
    pb = client.get("/api/v1/portfolio/panel-briefing").json()["tracks"]
    print("\n[2] MULTI-STAKEHOLDER PRESENTATION TRACKS (MENTORS / TEAM MEMBERS / TECHNICAL PANEL):")
    for key, track in pb.items():
        print(f"  -> [{track['audience'].upper()}] ({track['duration']}) | Focus: {track['focus']}")
        print(f"     Key Highlight: {track['key_points'][0]}")

    # 3. Live Dynamic Capstone Execution (5 Benchmark Scenarios + Custom Dynamic Audit)
    print("\n[3] LIVE CAPSTONE EXECUTION — FinDoc-AuditEngine v3.0 (1 USD = 86.50 INR):")
    batch = client.post("/api/v1/audit/demo-batch").json()
    for d in batch:
        print(
            f"  * {d['invoice_id']} | {d['vendor_name']:<28} | "
            f"${d['total_amount_usd']:>9,.2f} (INR {d['total_amount_inr']:>12,.2f}) | "
            f"Risk: {d['risk_score']:>4.1f} ({d['risk_level']:<8}) | Tier: {d['approval_tier']}"
        )

    # 4. Deliverables & 90-Day Roadmap Verification
    dl = client.get("/api/v1/portfolio/deliverables").json()
    print(f"\n[4] VERIFIED DAY 30 DELIVERABLES ({dl['count']} DOCUMENTS READY FOR SUBMISSION):")
    for item in dl["deliverables"]:
        print(f"  * [{item['format']:<8}] {item['filename']:<48} ({item['size_kb']:>6.1f} KB) -> {item['title']}")

    rm = client.get("/api/v1/portfolio/roadmap").json()
    print(f"\n[5] 90-DAY PERSONAL LEARNING ROADMAP SUMMARY ({rm['duration_days']} DAYS):")
    for p in rm["phases"]:
        print(f"  * {p['month']}: {p['theme']} | KPI: {p['kpi']}")

    print("\n" + "=" * 124)
    print("   DAY 30 FINAL PRACTICAL & PORTFOLIO VERIFICATION COMPLETE — READY FOR PANEL PRESENTATION")
    print("=" * 124 + "\n")


if __name__ == "__main__":
    main()
