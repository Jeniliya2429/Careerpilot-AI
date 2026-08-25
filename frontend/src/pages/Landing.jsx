import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../api/AuthContext.jsx'

export default function Landing() {
  const { user } = useAuth()

  return (
    <div className="container" style={{ paddingTop: 100, paddingBottom: 60 }}>
      <div className="eyebrow" style={{ marginBottom: 16 }}>AI CO-PILOT FOR YOUR NEXT ROLE</div>
      <h1 style={{ fontSize: 48, lineHeight: 1.1, maxWidth: 640, marginBottom: 20 }}>
        Preflight check for your <span style={{ color: 'var(--accent-cyan)' }}>next interview</span>.
      </h1>
      <p style={{ fontSize: 17, maxWidth: 540, marginBottom: 32 }}>
        Upload your resume and a job description. A LangGraph agent pipeline
        analyzes the gap, tailors your resume truthfully, and builds you a
        pre-interview battlecard — with a human checkpoint before anything ships.
      </p>
      <Link to={user ? '/dashboard' : '/register'} className="btn btn-primary">
        {user ? 'Go to dashboard' : 'Start your flight plan'} →
      </Link>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 72 }}>
        {[
          { title: 'Gap Analysis', desc: 'Fit score + missing keywords, compared honestly against the JD.' },
          { title: 'Tailored Resume', desc: 'Rewritten for the role — no fabricated experience, ever.' },
          { title: 'Battlecard', desc: 'Elevator pitch, talking points, and questions to ask — one page.' },
        ].map(f => (
          <div key={f.title} className="panel">
            <h3 style={{ fontSize: 15, marginBottom: 8, color: 'var(--accent-cyan)' }}>{f.title}</h3>
            <p style={{ fontSize: 13 }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
