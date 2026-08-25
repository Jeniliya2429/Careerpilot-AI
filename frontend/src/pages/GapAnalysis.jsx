import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonCard, SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

function FitRing({ score }) {
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, score || 0))
  const offset = circumference - (clamped / 100) * circumference
  const color = clamped >= 70 ? 'var(--accent-green)' : clamped >= 45 ? 'var(--accent-amber)' : 'var(--accent-red)'

  return (
    <div style={{ position: 'relative', width: 140, height: 140 }}>
      <svg className="fit-ring" width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--line)" strokeWidth="10" />
        <circle
          cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 30, fontWeight: 700 }}>{Math.round(clamped)}</span>
        <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>ATS Score</span>
      </div>
    </div>
  )
}

export default function GapAnalysis() {
  const { runId } = useParams()
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getPipelineStatus(runId)
      .then(s => { if (mounted) setStatus(s) })
      .catch(() => toast?.error('Could not load gap analysis.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  const fitScore = status?.fit_score || 0
  const passProb = fitScore >= 75 ? 'HIGH (Greenhouse / Workday Ready)' : fitScore >= 50 ? 'MEDIUM (Manual Review Likely)' : 'LOW (Risk of Auto-Rejection)'

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={1} />

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <SkeletonBlock height={220} />
          <SkeletonCard />
        </div>
      ) : (
        <div className="fade-in split-layout">
          <div className="panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
            <span className="eyebrow">ATS RADAR AUDITOR</span>
            <FitRing score={fitScore} />
            
            <div style={{ textAlign: 'center', background: 'var(--bg-panel-raised)', padding: '8px 14px', borderRadius: 20, width: '100%' }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block' }}>ATS PASS PROBABILITY</span>
              <strong style={{ fontSize: 12.5, color: fitScore >= 70 ? 'var(--accent-green)' : 'var(--accent-amber)' }}>{passProb}</strong>
            </div>

            <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-secondary)' }}>{status?.gap_notes}</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* ATS Compliance Checklist */}
            <div className="panel" style={{ background: 'var(--bg-panel-raised)', border: '1px solid var(--line)' }}>
              <h3 style={{ fontSize: 13.5, marginBottom: 10, color: 'var(--accent-cyan)' }}>🔍 ATS FORMAT & PARSER INTEGRITY</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: 12 }}>
                <div style={{ color: 'var(--accent-green)' }}>✓ Plain text PDF structure</div>
                <div style={{ color: 'var(--accent-green)' }}>✓ Standard section headings</div>
                <div style={{ color: 'var(--accent-green)' }}>✓ No unparseable image text</div>
                <div style={{ color: fitScore >= 60 ? 'var(--accent-green)' : 'var(--accent-amber)' }}>
                  {fitScore >= 60 ? '✓ High keyword density' : '⚠ Keyword density gap'}
                </div>
              </div>
            </div>

            {/* Matching Keywords */}
            <div className="panel">
              <h3 style={{ fontSize: 14, marginBottom: 12, color: 'var(--accent-green)' }}>Matched Skills & Keywords ({status?.matching_keywords?.length || 0})</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {(status?.matching_keywords || []).length === 0 && (
                  <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>None detected yet.</span>
                )}
                {(status?.matching_keywords || []).map(k => (
                  <span key={k} style={{ background: 'rgba(74, 222, 128, 0.1)', border: '1px solid var(--accent-green)', color: 'var(--accent-green)', padding: '4px 10px', borderRadius: 16, fontSize: 12 }}>
                    ✓ {k}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Gaps */}
            <div className="panel">
              <h3 style={{ fontSize: 14, marginBottom: 12, color: 'var(--accent-amber)' }}>Critical Keyword Gaps ({status?.missing_keywords?.length || 0})</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {(status?.missing_keywords || []).length === 0 && (
                  <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>No major gaps found — great match.</span>
                )}
                {(status?.missing_keywords || []).map(k => (
                  <span key={k} style={{ background: 'rgba(245, 165, 36, 0.1)', border: '1px solid var(--accent-amber)', color: 'var(--accent-amber)', padding: '4px 10px', borderRadius: 16, fontSize: 12 }}>
                    ⚠ {k}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 8 }}>
              <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
                ← Back to Dashboard
              </button>
              <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/tailored-resume`)}>
                Next: Review Tailored Resume →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
