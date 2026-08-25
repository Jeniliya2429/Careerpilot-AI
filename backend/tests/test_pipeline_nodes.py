"""
Tests every node's logic in isolation by monkeypatching the `_call_llm_*`
helper each node uses, so no real OpenAI API call is ever made.
"""
from app.ai import nodes
from app.ai import mock_interview


def test_parse_resume_node_maps_llm_output_to_state(monkeypatch):
    monkeypatch.setattr(
        nodes, "_call_llm_parse_resume",
        lambda resume_text: {"summary": "Backend engineer with 5 years experience.",
                              "skills": ["Python", "FastAPI", "PostgreSQL"]},
    )
    result = nodes.parse_resume_node({"resume_text": "some resume text", "errors": []})
    assert result["resume_summary"] == "Backend engineer with 5 years experience."
    assert result["resume_skills"] == ["Python", "FastAPI", "PostgreSQL"]


def test_parse_resume_node_handles_llm_failure_gracefully(monkeypatch):
    def _boom(resume_text):
        raise RuntimeError("simulated LLM outage")
    monkeypatch.setattr(nodes, "_call_llm_parse_resume", _boom)

    result = nodes.parse_resume_node({"resume_text": "x", "errors": []})
    assert result["status"] == "failed"
    assert "parse_resume_node" in result["errors"][0]


def test_parse_jd_node_maps_llm_output(monkeypatch):
    monkeypatch.setattr(
        nodes, "_call_llm_parse_jd",
        lambda jd_text: {"role_title": "Backend Engineer", "company": "Acme Corp",
                          "requirements": ["Python", "Docker", "Kubernetes"]},
    )
    result = nodes.parse_jd_node({"jd_text": "some jd", "errors": []})
    assert result["jd_role_title"] == "Backend Engineer"
    assert result["jd_requirements"] == ["Python", "Docker", "Kubernetes"]


def test_gap_analysis_node_computes_fit(monkeypatch):
    monkeypatch.setattr(
        nodes, "_call_llm_gap_analysis",
        lambda resume_skills, jd_requirements: {
            "fit_score": 72, "matching_keywords": ["Python"],
            "missing_keywords": ["Kubernetes"], "gap_notes": "Strong on Python, weak on infra.",
        },
    )
    result = nodes.gap_analysis_node({
        "resume_skills": ["Python", "FastAPI"], "jd_requirements": ["Python", "Kubernetes"], "errors": [],
    })
    assert result["fit_score"] == 72.0
    assert result["missing_keywords"] == ["Kubernetes"]


def test_tailor_resume_node_accepts_clean_first_draft(monkeypatch):
    """If self-reflection finds no fabrication, it should NOT retry."""
    calls = {"draft": 0, "reflect": 0}

    def _draft(resume_text, jd_requirements, missing_keywords, extra_notes=""):
        calls["draft"] += 1
        return "## Summary\nHonest tailored resume text."

    def _reflect(original_resume, tailored_resume):
        calls["reflect"] += 1
        return {"has_fabrication": False, "issues": [], "notes": "Clean, no fabrication detected."}

    monkeypatch.setattr(nodes, "_call_llm_draft_tailored_resume", _draft)
    monkeypatch.setattr(nodes, "_call_llm_reflect", _reflect)

    result = nodes.tailor_resume_node({
        "resume_text": "original resume", "jd_requirements": ["Python"],
        "missing_keywords": [], "errors": [],
    })

    assert calls["draft"] == 1
    assert calls["reflect"] == 1
    assert result["tailoring_revision_count"] == 0
    assert "Honest" in result["tailored_resume_draft"]


def test_tailor_resume_node_retries_when_fabrication_detected(monkeypatch):
    """
    Core guardrail test: if self-reflection flags fabrication, the node
    must redraft (up to MAX_TAILOR_REVISIONS) rather than silently
    accepting a fabricated resume.
    """
    calls = {"draft": 0, "reflect": 0}

    def _draft(resume_text, jd_requirements, missing_keywords, extra_notes=""):
        calls["draft"] += 1
        if calls["draft"] == 1:
            return "## Experience\nSenior Kubernetes Architect at Google (fabricated!)"
        return "## Experience\nHonest rewritten resume, no fabrication."

    def _reflect(original_resume, tailored_resume):
        calls["reflect"] += 1
        if calls["reflect"] == 1:
            return {"has_fabrication": True, "issues": ["Invented employer: Google"], "notes": "Fabrication found."}
        return {"has_fabrication": False, "issues": [], "notes": "Clean on retry."}

    monkeypatch.setattr(nodes, "_call_llm_draft_tailored_resume", _draft)
    monkeypatch.setattr(nodes, "_call_llm_reflect", _reflect)

    result = nodes.tailor_resume_node({
        "resume_text": "original resume, no Google experience", "jd_requirements": ["Kubernetes"],
        "missing_keywords": ["Kubernetes"], "errors": [],
    })

    assert calls["draft"] == 2  # redrafted exactly once
    assert result["tailoring_revision_count"] == 1
    assert "Honest rewritten" in result["tailored_resume_draft"]
    assert "Google" not in result["tailored_resume_draft"]


def test_tailor_resume_node_stops_after_max_revisions(monkeypatch):
    """Even if fabrication is never resolved, the node must not loop forever."""
    calls = {"draft": 0, "reflect": 0}

    def _draft(resume_text, jd_requirements, missing_keywords, extra_notes=""):
        calls["draft"] += 1
        return f"draft #{calls['draft']}"

    def _reflect(original_resume, tailored_resume):
        calls["reflect"] += 1
        return {"has_fabrication": True, "issues": ["still fabricating"], "notes": "still bad"}

    monkeypatch.setattr(nodes, "_call_llm_draft_tailored_resume", _draft)
    monkeypatch.setattr(nodes, "_call_llm_reflect", _reflect)

    result = nodes.tailor_resume_node({
        "resume_text": "original", "jd_requirements": [], "missing_keywords": [], "errors": [],
    })

    assert calls["draft"] == 1 + nodes.MAX_TAILOR_REVISIONS
    assert result["tailoring_revision_count"] == nodes.MAX_TAILOR_REVISIONS


def test_retrieve_questions_node_uses_chroma_collection(monkeypatch):
    class FakeCollection:
        def query(self, query_texts, n_results):
            return {
                "documents": [["Tell me about a time you led a project."]],
                "metadatas": [[{"category": "behavioral", "role_tag": "general"}]],
            }

    monkeypatch.setattr(nodes, "get_question_collection", lambda: FakeCollection())

    result = nodes.retrieve_questions_node({
        "jd_role_title": "Backend Engineer", "jd_requirements": ["Python"], "errors": [],
    })
    assert len(result["retrieved_questions"]) == 1
    assert result["retrieved_questions"][0]["category"] == "behavioral"


def test_generate_battlecard_node_returns_completed_status(monkeypatch):
    monkeypatch.setattr(
        nodes, "_call_llm_generate_battlecard",
        lambda *args, **kwargs: {
            "elevator_pitch": "I'm a backend engineer who ships reliable systems.",
            "top_strengths_to_lead_with": ["Python"],
            "gaps_to_address_proactively": ["Kubernetes"],
            "questions_to_ask_interviewer": ["What does success look like in 90 days?"],
            "key_talking_points": ["Scaled API to 1M requests/day"],
        },
    )
    result = nodes.generate_battlecard_node({
        "resume_summary": "x", "jd_role_title": "y", "jd_company": "z",
        "fit_score": 80, "matching_keywords": [], "missing_keywords": [], "errors": [],
    })
    assert result["status"] == "completed"
    assert "elevator_pitch" in result["battlecard"]


def test_score_mock_answer_returns_rubric_scores(monkeypatch):
    class FakeResponse:
        content = (
            '{"scores": {"structure": 7, "specificity": 6, "jd_alignment": 8}, '
            '"overall_verdict": "Solid answer with room to tighten the result.", '
            '"strengths": ["Clear situation setup"], '
            '"improvements": ["Quantify the outcome"], '
            '"suggested_rephrase": "Start with the impact, then explain how you got there."}'
        )

    class FakeLLM:
        def invoke(self, prompt):
            return FakeResponse()

    monkeypatch.setattr(mock_interview, "get_llm", lambda tier="light", temperature=0.3: FakeLLM())

    result = mock_interview.score_mock_answer(
        question="Tell me about a time you led a project.",
        answer="I led a migration project...",
        jd_requirements=["Python", "Leadership"],
    )
    assert result["scores"]["structure"] == 7
    assert "overall_verdict" in result
