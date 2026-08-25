import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'

const STEPS = [
  { label: 'Upload', route: '/dashboard' },
  { label: 'Gap Analysis', route: '/gap-analysis' },
  { label: 'Tailor', route: '/tailored-resume' },
  { label: 'Prep', route: '/interview-prep' },
  { label: 'Mock Interview', route: '/mock-interview' },
  { label: 'Battlecard', route: '/battlecard' },
  { label: 'Pitch', route: '/elevator-pitch' }
]

export default function FlightPlan({ current }) {
  const navigate = useNavigate()
  const { runId } = useParams()

  const handleStepClick = (stepIndex, route) => {
    if (stepIndex === 0) {
      navigate('/dashboard')
    } else if (runId) {
      navigate(`/runs/${runId}${route}`)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 28, overflowX: 'auto', paddingBottom: 4 }}>
      {STEPS.map((step, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'pending'
        const isClickable = i === 0 || !!runId

        return (
          <React.Fragment key={step.label}>
            <div 
              onClick={() => handleStepClick(i, step.route)}
              style={{
                display: 'flex', 
                alignItems: 'center', 
                gap: 8, 
                cursor: isClickable ? 'pointer' : 'default',
                opacity: state === 'pending' ? 0.75 : 1
              }}
              title={isClickable ? `Go to ${step.label}` : 'Start an application first'}
            >
              <div style={{
                width: 24, height: 24, borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 11, fontFamily: 'var(--font-mono)', fontWeight: 600,
                background: state === 'pending' ? 'transparent' : state === 'active' ? 'var(--accent-cyan)' : 'var(--bg-panel-raised)',
                color: state === 'active' ? '#06231F' : state === 'done' ? 'var(--accent-cyan)' : 'var(--text-muted)',
                border: `1px solid ${state === 'pending' ? 'var(--line)' : 'var(--accent-cyan)'}`,
                flexShrink: 0
              }}>
                {state === 'done' ? '✓' : i + 1}
              </div>
              <span style={{
                fontSize: 13,
                whiteSpace: 'nowrap',
                color: state === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)',
                fontWeight: state === 'active' ? 600 : 400,
              }}>{step.label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{ width: 20, height: 1, background: 'var(--line)', flexShrink: 0 }} />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}
