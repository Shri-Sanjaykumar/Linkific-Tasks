"""Day 30 Automated Tests for Portfolio, Panel Briefing, 90-Day Roadmap & Deliverable Downloads."""

from fastapi.testclient import TestClient


def test_portfolio_overview_endpoint(client: TestClient):
    """Verify candidate metadata, 6-phase 30-day matrix, and flagship projects."""
    res = client.get("/api/v1/portfolio/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["candidate"]["name"] == "Shri Sanjaykumar V"
    assert "9.12" in data["candidate"]["cgpa"]
    assert len(data["progression_matrix"]) == 6
    assert len(data["projects"]) >= 5


def test_panel_briefing_tracks_endpoint(client: TestClient):
    """Verify tailored presentation tracks for Mentors, Team Members, and Technical Panel."""
    res = client.get("/api/v1/portfolio/panel-briefing")
    assert res.status_code == 200
    tracks = res.json()["tracks"]
    assert "mentors" in tracks
    assert "team_members" in tracks
    assert "technical_panel" in tracks
    assert len(tracks["technical_panel"]["key_points"]) >= 4


def test_90_day_learning_roadmap_endpoint(client: TestClient):
    """Verify the 90-day personal learning roadmap structure and KPIs."""
    res = client.get("/api/v1/portfolio/roadmap")
    assert res.status_code == 200
    body = res.json()
    assert body["duration_days"] == 90
    assert len(body["phases"]) == 3


def test_deliverables_catalog_endpoint(client: TestClient):
    """Verify all Day 30 PDF and Markdown deliverables are present and non-empty."""
    res = client.get("/api/v1/portfolio/deliverables")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] >= 10
    filenames = {item["filename"] for item in body["deliverables"]}
    assert "SHRI_SANJAYKUMAR_V_UPDATED_RESUME_LINKIFIC.pdf" in filenames
    assert "INTERNSHIP_REFLECTION_REPORT.pdf" in filenames
    assert "INTERNSHIP_REFLECTION_REPORT.md" in filenames
    assert "UPDATED_LINKEDIN_PROFILE.md" in filenames
    assert "PERSONAL_LEARNING_ROADMAP_90_DAYS.md" in filenames


def test_download_updated_resume_pdf_and_reflection_md(client: TestClient):
    """Verify direct HTTP download of the Updated Resume PDF and Reflection Report Markdown."""
    res_pdf = client.get("/api/v1/portfolio/download/SHRI_SANJAYKUMAR_V_UPDATED_RESUME_LINKIFIC.pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 5000

    res_md = client.get("/api/v1/portfolio/download/INTERNSHIP_REFLECTION_REPORT.md")
    assert res_md.status_code == 200
    assert "Shri Sanjaykumar V" in res_md.text
