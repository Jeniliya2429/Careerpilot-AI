import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

export default function ActionPlan() {
  const { runId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getActionPlan(runId)
      .then(res => { if (mounted) setData(res.data) })
      .catch(() => toast?.error('Could not load 30-60-90 day action plan.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        <FlightPlan current={6} />
        <SkeletonBlock height={380} />
      </div>
    )
  }

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={6} />

      <div className="fade-in">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <span className="eyebrow">EXECUTIVE STRATEGY</span>
            <h1 style={{ fontSize: 26, marginTop: 4 }}>30-60-90 Day Onboarding Action Plan</h1>
          </div>
          <button className="btn btn-secondary" onClick={() => window.print()}>
            🖨️ Print / Export PDF
          </button>
        </div>

        <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 24 }}>
          Present this strategic roadmap in final-round executive interviews to demonstrate immediate readiness and Day-1 clarity.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20, marginBottom: 24 }}>
          {/* Day 30 */}
          <div className="panel" style={{ borderTop: '4px solid var(--accent-cyan)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <h3 style={{ fontSize: 16, color: 'var(--accent-cyan)' }}>DAYS 1 – 30</h3>
              <span className="badge" style={{ borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)' }}>LEARN & AUDIT</span>
            </div>
            <ul style={{ paddingLeft: 18, margin: 0, display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
              {data?.day_30_goals?.map((g, i) => (
                <li key={i} style={{ lineHeight: 1.5 }}>{g}</li>
              ))}
            </ul>
          </div>

          {/* Day 60 */}
          <div className="panel" style={{ borderTop: '4px solid var(--accent-amber)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <h3 style={{ fontSize: 16, color: 'var(--accent-amber)' }}>DAYS 31 – 60</h3>
              <span className="badge" style={{ borderColor: 'var(--accent-amber)', color: 'var(--accent-amber)' }}>BUILD & EXECUTE</span>
            </div>
            <ul style={{ paddingLeft: 18, margin: 0, display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
              {data?.day_60_goals?.map((g, i) => (
                <li key={i} style={{ lineHeight: 1.5 }}>{g}</li>
              ))}
            </ul>
          </div>

          {/* Day 90 */}
          <div className="panel" style={{ borderTop: '4px solid var(--accent-green)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <h3 style={{ fontSize: 16, color: 'var(--accent-green)' }}>DAYS 61 – 90</h3>
              <span className="badge" style={{ borderColor: 'var(--accent-green)', color: 'var(--accent-green)' }}>LEAD & SCALE</span>
            </div>
            <ul style={{ paddingLeft: 18, margin: 0, display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
              {data?.day_90_goals?.map((g, i) => (
                <li key={i} style={{ lineHeight: 1.5 }}>{g}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Success Metrics */}
        <div className="panel" style={{ background: 'var(--bg-panel-raised)', marginBottom: 24 }}>
          <h3 style={{ fontSize: 15, marginBottom: 12, color: 'var(--text-primary)' }}>🎯 Key Success Metrics & KPIs</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
            {data?.key_success_metrics?.map((m, i) => (
              <div key={i} style={{ background: 'var(--bg-panel)', padding: 12, borderRadius: 8, border: '1px solid var(--line)', fontSize: 13, display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ color: 'var(--accent-green)', fontWeight: 700 }}>✓</span>
                <span>{m}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/salary-negotiation`)}>
            Next Step: Salary Negotiation Strategy →
          </button>
        </div>
      </div>
    </div>
  )
}
