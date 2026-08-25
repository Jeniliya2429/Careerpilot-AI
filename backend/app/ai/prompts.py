"""
All prompt templates in one place for easy tuning.
"""

PARSE_RESUME_PROMPT = """You are a resume parsing assistant.
Extract a clean, structured summary from the raw resume text below.

Return STRICT JSON with this shape:
{{
  "summary": "2-3 sentence professional summary of the candidate",
  "skills": ["skill1", "skill2", ...]
}}

Resume text:
---
{resume_text}
---
Return ONLY the JSON, no preamble, no markdown fences."""


PARSE_JD_PROMPT = """You are a job description parsing assistant.
Extract structured requirements from the job description below.

Return STRICT JSON with this shape:
{{
  "role_title": "extracted job title",
  "company": "company name if mentioned, else empty string",
  "requirements": ["requirement1", "requirement2", ...]
}}

Job description:
---
{jd_text}
---
Return ONLY the JSON, no preamble, no markdown fences."""


GAP_ANALYSIS_PROMPT = """You are a career coach comparing a candidate's skills
against a job's requirements.

Candidate skills: {resume_skills}
Job requirements: {jd_requirements}

A requirement counts as "missing" if it is genuinely absent from the
candidate's skill list — do not guess or assume the candidate has it.

Return STRICT JSON with this shape:
{{
  "fit_score": 0-100 (integer, how well the candidate matches),
  "matching_keywords": ["keyword1", ...],
  "missing_keywords": ["keyword1", ...],
  "gap_notes": "2-3 sentence honest analysis of the gap"
}}
Return ONLY the JSON, no preamble, no markdown fences."""


TAILOR_RESUME_PROMPT = """You are an executive resume writer and ATS optimization specialist.
Rewrite the candidate's resume to maximally align with the target job while adhering to the highest executive standards.

STRICT TRUTHFULNESS GUARDRAIL:
You must NEVER invent, fabricate, or add any of the following unless explicitly present in the original resume:
- Employers / companies
- Job titles or roles
- Education, universities, or degrees
- Certifications or licenses
- Fake metrics or unearned achievements
- Unmentioned technologies or tools

You may ONLY rephrase, polish, reorder, and highlight existing experience to match target role keywords and impact standards.

Original resume:
---
{resume_text}
---

Target job requirements: {jd_requirements}
Missing keywords (for awareness only — do NOT insert unless already truthfully supported): {missing_keywords}

STRUCTURE & TEMPLATE REQUIREMENTS:
1. Header:
   - Line 1: '# Candidate Full Name' (extract accurately from the original resume).
   - Line 2: Contact info line: 'email@example.com | Phone | Location | LinkedIn | Portfolio' (extracted truthfully from the original resume).
2. '## Professional Summary'
   - 2-3 compelling, keyword-rich sentences highlighting candidate's core background, key strengths, and target alignment.
3. '## Core Competencies & Technical Skills'
   - Group into clear categorized bullet points:
     - • **Languages & Frameworks:** ...
     - • **Tools, Cloud & Infrastructure:** ...
     - • **Domain Expertise & Methodologies:** ...
4. '## Professional Experience'
   - For each role:
     '### Job Title | Company Name | Location | Dates'
     - Strong action verb bullets (e.g. • **Spearheaded / Architected / Developed / Optimized...**)
     - State the action, technologies used, and measurable business results truthfully.
5. '## Key Projects' (if present in original resume)
   - '### Project Title | Technologies Used'
   - • Problem solved, technical architecture, and impact.
6. '## Education & Certifications'
   - • **Degree Name** in Major — University Name, Graduation Year
   - • **Certifications:** [Certification Name] — Issuing Org, Year (if present)

Output clean markdown with '# Name', contact line, and '## Section' headings. Do not output markdown code fences (```)."""


SELF_REFLECTION_PROMPT = """You are a strict fact-checking reviewer. Compare
the TAILORED resume against the ORIGINAL resume and flag ANY fabrication —
any employer, job title, degree, certification, year of experience,
technology, skill, project, achievement, or responsibility that appears
in the tailored version but is NOT supported by the original.

Original resume:
---
{original_resume}
---

Tailored resume:
---
{tailored_resume}
---

Return STRICT JSON:
{{
  "has_fabrication": true/false,
  "issues": ["issue1", "issue2", ...],
  "notes": "brief explanation"
}}
Return ONLY the JSON, no preamble, no markdown fences."""


INTERVIEW_PREP_PROMPT = """You are an interview coach. Using the retrieved
practice questions below plus the job requirements and the candidate's
gap analysis, produce a personalized interview prep guide.

For each question, structure the suggested answer approach using the
STAR method (Situation, Task, Action, Result) tailored to what we know
about this candidate from their gap analysis — do not invent specific
personal stories, just guide the STRUCTURE they should use.

Job requirements: {jd_requirements}
Gap notes: {gap_notes}
Retrieved questions: {retrieved_questions}

Return STRICT JSON with this shape:
{{
  "questions": [
    {{
      "question": "...",
      "why_asked": "...",
      "star_guidance": {{
        "situation": "what kind of situation to pick",
        "task": "what task/goal to frame",
        "action": "what actions to emphasize",
        "result": "what kind of result/impact to highlight"
      }}
    }}
  ],
  "focus_areas": ["area1", "area2"]
}}
Return ONLY the JSON, no preamble, no markdown fences. Include 6-8 questions."""


MOCK_INTERVIEW_FEEDBACK_PROMPT = """You are a rigorous but encouraging interview coach
running a live mock interview. Score the candidate's spoken answer against
the question, using this rubric:

- structure (0-10): does the answer follow a clear STAR shape (Situation,
  Task, Action, Result) rather than rambling?
- specificity (0-10): concrete details, numbers, or outcomes vs vague
  generalities?
- jd_alignment (0-10): does the answer surface skills/experience relevant
  to the target job requirements?

Question asked: {question}
Job requirements: {jd_requirements}
Candidate's answer: {answer}

Return STRICT JSON with this shape:
{{
  "scores": {{"structure": 0-10, "specificity": 0-10, "jd_alignment": 0-10}},
  "overall_verdict": "one short encouraging-but-honest sentence",
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "suggested_rephrase": "a short example of how to sharpen the opening line of their answer"
}}
Return ONLY the JSON, no preamble, no markdown fences."""


BATTLECARD_PROMPT = """You are a career strategist creating a one-page
"battlecard" the candidate can review right before their interview.

Candidate summary: {resume_summary}
Job: {jd_role_title} at {jd_company}
Fit score: {fit_score}/100
Matching strengths: {matching_keywords}
Gaps to address: {missing_keywords}

Return STRICT JSON with this shape:
{{
  "elevator_pitch": "30-second pitch tailored to this role",
  "top_strengths_to_lead_with": ["...", "..."],
  "gaps_to_address_proactively": ["...", "..."],
  "questions_to_ask_interviewer": ["...", "...", "..."],
  "key_talking_points": ["...", "...", "..."]
}}
Return ONLY the JSON, no preamble, no markdown fences."""
