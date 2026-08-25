"""
Unit tests for Multi-Agent Collaborative Architecture:
Supervisor, Analyst Agent, Tailor Agent (Actor), Compliance Auditor Agent (Critic),
Interview Coach Agent, and Battlecard Strategist Agent.
"""
from app.ai.agents import analyst, tailor, auditor, coach, strategist, supervisor
from app.ai.agents.analyst import run_analyst_agent
from app.ai.agents.tailor import run_tailor_agent
from app.ai.agents.auditor import run_auditor_agent
from app.ai.agents.coach import run_coach_agent
from app.ai.agents.strategist import run_strategist_agent
from app.ai.agents.supervisor import run_supervisor_agent, route_next_agent


def test_analyst_agent_executes_analysis(monkeypatch):
    class FakeLLM:
        def __init__(self, response_text):
            self.response_text = response_text
        def invoke(self, prompt):
            class Response:
                pass
            r = Response()
            r.content = self.response_text
            return r

    monkeypatch.setattr(analyst, "get_llm", lambda tier="light", temperature=0.1: FakeLLM(
        '{"summary": "Python dev", "skills": ["Python"], "role_title": "Backend Dev", "company": "Tech", "requirements": ["Python", "Docker"], "fit_score": 85, "matching_keywords": ["Python"], "missing_keywords": ["Docker"], "gap_notes": "Good match"}'
    ))

    state = {"resume_text": "Sample resume", "jd_text": "Sample JD", "errors": []}
    res = run_analyst_agent(state)

    assert res["current_agent"] == "ResumeAnalystAgent"
    assert res["fit_score"] == 85.0
    assert len(res["agent_logs"]) >= 1


def test_supervisor_agent_routing():
    # Test router decisions
    s1 = {"current_agent": "ResumeAnalystAgent"}
    r1 = run_supervisor_agent(s1)
    assert r1["next_step"] == "tailor"

    s2 = {"current_agent": "ResumeTailorAgent"}
    r2 = run_supervisor_agent(s2)
    assert r2["next_step"] == "auditor"

    # Auditor flags fabrication -> route back to tailor
    s3 = {
        "current_agent": "ComplianceAuditorAgent",
        "audit_history": [{"has_fabrication": True, "issues": ["Invented Google"]}],
        "tailoring_revision_count": 0,
    }
    r3 = run_supervisor_agent(s3)
    assert r3["next_step"] == "tailor"

    # Auditor passed -> route to human interrupt checkpoint
    s4 = {
        "current_agent": "ComplianceAuditorAgent",
        "audit_history": [{"has_fabrication": False, "issues": []}],
        "tailoring_revision_count": 0,
    }
    r4 = run_supervisor_agent(s4)
    assert r4["next_step"] == "tailor_resume"


def test_actor_critic_loop(monkeypatch):
    class FakeLLM:
        def __init__(self, content):
            self.content = content
        def invoke(self, prompt):
            class R:
                pass
            r = R()
            r.content = self.content
            return r

    monkeypatch.setattr(tailor, "get_llm", lambda *a, **k: FakeLLM("## Summary\nTailored Content"))
    monkeypatch.setattr(auditor, "get_llm", lambda *a, **k: FakeLLM('{"has_fabrication": false, "issues": [], "notes": "Passed"}'))

    state = {
        "resume_text": "Original Resume",
        "jd_requirements": ["Python"],
        "missing_keywords": [],
        "errors": [],
    }

    tailor_res = run_tailor_agent(state)
    assert tailor_res["current_agent"] == "ResumeTailorAgent"
    assert "Tailored Content" in tailor_res["tailored_resume_draft"]

    state.update(tailor_res)
    audit_res = run_auditor_agent(state)
    assert audit_res["current_agent"] == "ComplianceAuditorAgent"
    assert len(audit_res["audit_history"]) == 1
    assert audit_res["audit_history"][0]["has_fabrication"] is False
