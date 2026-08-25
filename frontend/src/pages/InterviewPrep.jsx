import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonCard } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

function QuestionCard({ q, index }) {
  const [open, setOpen] = useState(index === 0)
  return (
    <div className="panel panel-interactive" style={{ cursor: 'pointer' }} onClick={() => setOpen(o => !o)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
        <h3 style={{ fontSize: 14.5, lineHeight: 1.5 }}>{q.question}</h3>
        <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>{open ? '−' : '+'}</span>
      </div>
      {q.why_asked && <p style={{ fontSize: 12.5, marginTop: 6 }}>{q.why_asked}</p>}

      {open && q.star_guidance && (
        <div className="fade-in" style={{ marginTop: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {['situation', 'task', 'action', 'result'].map(key => (
            q.star_guidance[key] && (
              <div key={key} style={{ background: 'var(--bg-panel-raised)', borderRadius: 8, padding: 10 }}>
                <div className="eyebrow" style={{ fontSize: 10.5, marginBottom: 4 }}>{key}</div>
                <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>{q.star_guidance[key]}</div>
              </div>
            )
          ))}
        </div>
      )}
    </div>
  )
}

export default function InterviewPrep() {
  const { runId } = useParams()
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getPipelineStatus(runId)
      .then(s => { if (mounted) setStatus(s) })
      .catch(() => toast?.error('Could not load interview prep.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  const prep = status?.interview_prep

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={3} />

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <SkeletonCard /><SkeletonCard /><SkeletonCard />
        </div>
      ) : !prep ? (
        <div className="panel">
          <p>Interview prep isn't ready yet — approve the tailored resume first.</p>
          <button className="btn btn-secondary" style={{ marginTop: 12 }}
                  onClick={() => navigate(`/runs/${runId}/tailored-resume`)}>Back to approval</button>
        </div>
      ) : (
        <div className="fade-in">
          {prep.focus_areas?.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
              {prep.focus_areas.map(f => <span key={f} className="chip">{f}</span>)}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
            {(prep.questions || []).map((q, i) => <QuestionCard key={i} q={q} index={i} />)}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 16 }}>
            <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/tailored-resume`)}>
              ← Back to Tailored Resume
            </button>
            <div style={{ display: 'flex', gap: 12 }}>
              <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/mock-interview`)}>
                Next: Mock Interview →
              </button>
              <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/battlecard`)}>
                View Battlecard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
