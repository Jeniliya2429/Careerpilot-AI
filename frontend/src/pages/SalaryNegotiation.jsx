import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

export default function SalaryNegotiation() {
  const { runId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [copiedKey, setCopiedKey] = useState(null)
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getSalaryNegotiation(runId)
      .then(res => { if (mounted) setData(res.data) })
      .catch(() => toast?.error('Could not load salary negotiation data.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(key)
    toast?.success('Email template copied to clipboard!')
    setTimeout(() => setCopiedKey(null), 2500)
  }

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        <FlightPlan current={7} />
        <SkeletonBlock height={380} />
      </div>
    )
  }

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={7} />

      <div className="fade-in">
        <div style={{ marginBottom: 20 }}>
          <span className="eyebrow">COMPENSATION STRATEGY</span>
          <h1 style={{ fontSize: 26, marginTop: 4 }}>Salary & Offer Negotiation Battle Plan</h1>
        </div>

        {/* Benchmarks Header */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20, marginBottom: 24 }}>
          <div className="panel" style={{ borderLeft: '4px solid var(--accent-green)' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>ESTIMATED BASE SALARY RANGE</span>
            <h2 style={{ fontSize: 20, color: 'var(--accent-green)', marginTop: 4 }}>{data?.salary_range}</h2>
          </div>

          <div className="panel" style={{ borderLeft: '4px solid var(--accent-cyan)' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>EQUITY / STOCK BENCHMARK</span>
            <h2 style={{ fontSize: 20, color: 'var(--accent-cyan)', marginTop: 4 }}>{data?.equity_benchmark}</h2>
          </div>
        </div>

        {/* Leverage Points */}
        <div className="panel" style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 15, marginBottom: 12, color: 'var(--accent-amber)' }}>⚡ Your Top Compensation Leverage Points</h3>
          <ul style={{ paddingLeft: 18, margin: 0, display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13.5 }}>
            {data?.top_leverage_points?.map((lp, i) => (
              <li key={i} style={{ lineHeight: 1.5 }}>{lp}</li>
            ))}
          </ul>
        </div>

        {/* Copyable Negotiation Scripts */}
        <h3 style={{ fontSize: 16, marginBottom: 14 }}>📋 Ready-to-Use Negotiation Email Scripts</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 24 }}>
          {/* Initial Response */}
          <div className="panel" style={{ background: 'var(--bg-panel-raised)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>1. Initial Offer Counter-Request</span>
              <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 12 }}
                      onClick={() => copyToClipboard(data?.email_template_initial, 'initial')}>
                {copiedKey === 'initial' ? '✓ Copied!' : '📋 Copy Script'}
              </button>
            </div>
            <p style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
              {data?.email_template_initial}
            </p>
          </div>

          {/* Final Push Counter */}
          <div className="panel" style={{ background: 'var(--bg-panel-raised)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>2. Final Compromise / Sign-On Bonus Push</span>
              <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 12 }}
                      onClick={() => copyToClipboard(data?.email_template_counter, 'counter')}>
                {copiedKey === 'counter' ? '✓ Copied!' : '📋 Copy Script'}
              </button>
            </div>
            <p style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
              {data?.email_template_counter}
            </p>
          </div>

          {/* Competing Offer */}
          <div className="panel" style={{ background: 'var(--bg-panel-raised)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>3. Competing Offer Leverage Email</span>
              <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 12 }}
                      onClick={() => copyToClipboard(data?.email_template_competing, 'competing')}>
                {copiedKey === 'competing' ? '✓ Copied!' : '📋 Copy Script'}
              </button>
            </div>
            <p style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
              {data?.email_template_competing}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/elevator-pitch`)}>
            Next Step: 60-Second Teleprompter Pitch Studio →
          </button>
        </div>
      </div>
    </div>
  )
}
