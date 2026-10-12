"""Automated Tests for Day 29 & 30 Technical Presentation Slides, 10 Interview Q&As, Checklist & Vector PDF Downloads."""

from fastapi.testclient import TestClient


def test_prep_slides_deck_endpoint(client: TestClient):
    """Verify 12-slide presentation deck endpoint returns all 12 slides and speaker notes."""
    res = client.get("/api/v1/prep/slides")
    assert res.status_code == 200
    body = res.json()
    assert body["total_slides"] == 12
    assert len(body["slides"]) == 12
    assert "speaker_notes" in body["slides"][0]


def test_prep_10_interview_qa_endpoint(client: TestClient):
    """Verify all 10 technical interview questions and deep architectural answers are returned."""
    res = client.get("/api/v1/prep/interview-qa")
    assert res.status_code == 200
    body = res.json()
    assert body["total_questions"] == 10
    assert len(body["items"]) == 10


def test_prep_checklist_and_video_storyboard_endpoint(client: TestClient):
    """Verify mentor demo practice checklist and 5-scene video storyboard."""
    res = client.get("/api/v1/prep/checklist-and-video")
    assert res.status_code == 200
    body = res.json()
    assert len(body["checklist"]) >= 7
    assert len(body["video_storyboard"]) == 5
    dl = client.get("/api/v1/prep/download/INTERVIEW_QA.pdf")
    assert dl.status_code == 200
    assert dl.headers["content-type"] == "application/pdf"
