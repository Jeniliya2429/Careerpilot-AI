import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

export default function ElevatorPitch() {
  const { runId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Teleprompter state
  const [isScrolling, setIsScrolling] = useState(false)
  const [scrollSpeed, setScrollSpeed] = useState(2)
  const [timer, setTimer] = useState(60)
  const [timeRemaining, setTimeRemaining] = useState(60)
  const teleprompterRef = useRef(null)
  const timerIntervalRef = useRef(null)
  const scrollIntervalRef = useRef(null)

  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getElevatorPitch(runId)
      .then(res => { if (mounted) setData(res.data) })
      .catch(() => toast?.error('Could not load elevator pitch script.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  const pitchText = data?.custom_pitch || data?.storyteller_pitch || 'I am eager to leverage my technical background and strategic expertise to drive high impact for your team.'

  const toggleTeleprompter = () => {
    if (isScrolling) {
      stopTeleprompter()
    } else {
      startTeleprompter()
    }
  }

  const startTeleprompter = () => {
    setIsScrolling(true)
    setTimeRemaining(timer)
    
    if (teleprompterRef.current) {
      teleprompterRef.current.scrollTop = 0
    }

    timerIntervalRef.current = setInterval(() => {
      setTimeRemaining(t => {
        if (t <= 1) {
          stopTeleprompter()
          return 0
        }
        return t - 1
      })
    }, 1000)

    scrollIntervalRef.current = setInterval(() => {
      if (teleprompterRef.current) {
        teleprompterRef.current.scrollTop += scrollSpeed
      }
    }, 50)
  }

  const stopTeleprompter = () => {
    setIsScrolling(false)
    clearInterval(timerIntervalRef.current)
    clearInterval(scrollIntervalRef.current)
  }

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
        <div style={{ marginBottom: 20 }}>
          <span className="eyebrow">TAILORED PITCH STUDIO</span>
          <h1 style={{ fontSize: 26, marginTop: 4 }}>Role-Tailored Elevator Pitch Teleprompter</h1>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginTop: 4 }}>
            Synthesized specifically from your resume background and your target role requirements.
          </p>
        </div>

        {/* Teleprompter Controls Bar */}
        <div className="panel" style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-panel-raised)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button className={`btn ${isScrolling ? 'btn-danger' : 'btn-primary'}`} onClick={toggleTeleprompter}>
              {isScrolling ? '🛑 Stop Teleprompter' : '▶️ Start Teleprompter'}
            </button>
            <span style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: timeRemaining < 10 ? 'var(--accent-red)' : 'var(--accent-cyan)' }}>
              ⏱️ 00:{timeRemaining < 10 ? `0${timeRemaining}` : timeRemaining}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 13 }}>
            <label style={{ color: 'var(--text-muted)' }}>
              Target Time:{' '}
              <select value={timer} onChange={e => { setTimer(Number(e.target.value)); setTimeRemaining(Number(e.target.value)); }}
                      style={{ padding: '4px 8px', borderRadius: 4, background: 'var(--bg-panel)', color: 'var(--text-primary)', border: '1px solid var(--line)' }}>
                <option value={30}>30s Speed</option>
                <option value={60}>60s Standard</option>
                <option value={90}>90s Deep</option>
              </select>
            </label>
            <label style={{ color: 'var(--text-muted)' }}>
              Scroll Speed:{' '}
              <input type="range" min="1" max="5" value={scrollSpeed} onChange={e => setScrollSpeed(Number(e.target.value))} />
            </label>
          </div>
        </div>

        {/* Teleprompter Screen */}
        <div 
          ref={teleprompterRef}
          className="panel"
          style={{ 
            height: 280, 
            overflowY: 'auto', 
            scrollBehavior: 'smooth',
            background: '#070D18',
            border: isScrolling ? '2px solid var(--accent-cyan)' : '1px solid var(--line)',
            padding: 30,
            marginBottom: 24,
            boxShadow: isScrolling ? '0 0 20px rgba(52, 211, 201, 0.2)' : 'none'
          }}
        >
          <div style={{ height: 40 }} />
          <p style={{ fontSize: 21, lineHeight: 1.8, color: '#FFFFFF', fontWeight: 500, textAlign: 'center', maxWidth: 720, margin: '0 auto' }}>
            {pitchText}
          </p>
          <div style={{ height: 180 }} />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/battlecard`)}>
            ← Back to Battlecard
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
            Finish Flight Plan 🎉
          </button>
        </div>
      </div>
    </div>
  )
}
