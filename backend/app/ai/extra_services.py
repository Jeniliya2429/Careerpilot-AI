"""
Services for Salary Negotiation, 30-60-90 Day Action Plan, and Elevator Pitch generation.
Uses structured output parsing or fallbacks so endpoints run cleanly even without OpenAI keys (fallback mock generator).
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.llm_client import get_llm
from app.config import settings


def generate_salary_negotiation(resume_text: str, jd_text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        return {
            "salary_range": "$135,000 - $165,000 USD (Base) + 15% Bonus + Equity",
            "equity_benchmark": "0.05% - 0.15% Stock Options (4-year vest, 1-year cliff)",
            "top_leverage_points": [
                "Direct experience scaling production architecture matching JD requirements",
                "Proven leadership track record reducing deployment downtime by 40%",
                "Specialized expertise in cloud optimization saving $50k+ annually"
            ],
            "email_template_initial": "Thank you so much for extending this offer! I am extremely excited about the vision at the company. Based on my specialized background in cloud architecture and market data for this role, I would like to explore if there is flexibility to bring the base salary to $155,000.",
            "email_template_counter": "I appreciate your response and enthusiasm for having me join the team. Given the high impact expected in the first 90 days, if we can meet at $150,000 with a $10,000 signing bonus, I am prepared to sign the offer immediately.",
            "email_template_competing": "I am currently reviewing an offer with a competing firm at $160,000. However, your team and mission are my absolute top choice. Is there any leeway to adjust the total compensation package to make this an easy decision?"
        }

    llm = get_llm(tier="heavy", temperature=0.4)
    prompt = f"""
Analyze the candidate's resume and job description to construct an elite salary negotiation plan.
Return ONLY a JSON object with these keys:
- "salary_range": string estimate
- "equity_benchmark": string estimate
- "top_leverage_points": array of 3 bullet points
- "email_template_initial": string email template
- "email_template_counter": string email template
- "email_template_competing": string email template

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:2000]}
"""
    try:
        res = llm.invoke([SystemMessage(content="You are an executive compensation negotiator. Return strictly valid JSON."), HumanMessage(content=prompt)])
        content = res.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception:
        return generate_salary_negotiation("", "")


def generate_action_plan(resume_text: str, jd_text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        return {
            "day_30_goals": [
                "Audit current codebase, infrastructure setup, and deployment pipelines.",
                "Conduct 1-on-1 interviews with key team stakeholders to identify bottleneck friction points.",
                "Deliver initial quick-win documentation update or bug fix within the first 2 weeks."
            ],
            "day_60_goals": [
                "Lead execution on the core feature priority outlined in the Q3 product roadmap.",
                "Establish automated test suite coverage improvements for key API endpoints.",
                "Optimize performance bottlenecks identified during initial audit phase."
            ],
            "day_90_goals": [
                "Propose long-term architectural scaling improvements to leadership.",
                "Mentor junior team members and standardise code review guidelines.",
                "Present a 30-day post-launch metrics review for new feature deployments."
            ],
            "key_success_metrics": [
                "Deployment velocity increased by 25%",
                "Zero P1 incidents during launch phase",
                "100% stakeholder satisfaction rating across sprint cycles"
            ]
        }

    llm = get_llm(tier="light", temperature=0.3)
    prompt = f"""
Create a 30-60-90 Day Onboarding Action Plan for this role based on the JD and candidate resume.
Return ONLY a JSON object with these keys:
- "day_30_goals": array of 3 strings
- "day_60_goals": array of 3 strings
- "day_90_goals": array of 3 strings
- "key_success_metrics": array of 3 strings

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:2000]}
"""
    try:
        res = llm.invoke([SystemMessage(content="You are an executive career strategist. Return strictly valid JSON."), HumanMessage(content=prompt)])
        content = res.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception:
        return generate_action_plan("", "")


def generate_elevator_pitch(resume_text: str, jd_text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        return {
            "custom_pitch": "I'm a dedicated professional with a strong background in software engineering, cloud architecture, and high-performance system design. Over my career, I've specialized in turning complex requirements into scalable, reliable solutions—driving measurable efficiency gains and optimizing core platform operations. Looking at the target role and vision at your organization, I am eager to leverage my technical expertise and collaborative leadership to drive immediate impact for your team from Day 1."
        }

    llm = get_llm(tier="heavy", temperature=0.5)
    prompt = f"""
Construct a single, highly compelling 60-second Elevator Pitch answering "Tell me about yourself".
Tailor it SPECIFICALLY to the candidate's actual resume background and the target role/company requirements in the job description.

Return ONLY a JSON object with this key:
- "custom_pitch": string (a polished, professional 4-5 sentence elevator pitch)

CANDIDATE RESUME:
{resume_text[:2000]}

TARGET JOB DESCRIPTION:
{jd_text[:2000]}
"""
    try:
        res = llm.invoke([SystemMessage(content="You are an executive pitch coach. Return strictly valid JSON."), HumanMessage(content=prompt)])
        content = res.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception:
        return generate_elevator_pitch("", "")

