import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

export default function Battlecard() {
  const { runId } = useParams()
  const [card, setCard] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getBattlecard(runId)
      .then(res => { if (mounted) setCard(res.content) })
      .catch(() => toast?.error('Battlecard not ready — approve the tailored resume first.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={5} />

      {loading ? (
        <SkeletonBlock height={420} />
      ) : !card ? (
        <div className="panel">
          <p>No battlecard available. Continue to Elevator Pitch below.</p>
          <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={() => navigate(`/runs/${runId}/elevator-pitch`)}>
            Go to Elevator Pitch →
          </button>
        </div>
      ) : (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="panel" style={{ borderColor: 'var(--accent-cyan)' }}>
            <div className="eyebrow" style={{ marginBottom: 8 }}>ELEVATOR PITCH SUMMARY</div>
            <p style={{ fontSize: 15, color: 'var(--text-primary)', lineHeight: 1.6 }}>{card.elevator_pitch}</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="panel">
              <h3 style={{ fontSize: 13, marginBottom: 10, color: 'var(--accent-green)' }}>Lead with</h3>
              <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(card.top_strengths_to_lead_with || []).map((s, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</li>
                ))}
              </ul>
            </div>
            <div className="panel">
              <h3 style={{ fontSize: 13, marginBottom: 10, color: 'var(--accent-amber)' }}>Address proactively</h3>
              <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
                {(card.gaps_to_address_proactively || []).map((s, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="panel">
            <h3 style={{ fontSize: 13, marginBottom: 10 }}>Key talking points</h3>
            <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {(card.key_talking_points || []).map((s, i) => (
                <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</li>
              ))}
            </ul>
          </div>

          <div className="panel">
            <h3 style={{ fontSize: 13, marginBottom: 10 }}>Questions to ask them</h3>
            <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {(card.questions_to_ask_interviewer || []).map((s, i) => (
                <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s}</li>
              ))}
            </ul>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 8 }}>
            <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/mock-interview`)}>
              ← Back to Mock Interview
            </button>
            <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/elevator-pitch`)}>
              Next: Teleprompter Pitch →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
