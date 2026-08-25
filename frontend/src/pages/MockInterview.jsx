import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

const FILLER_WORDS = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'honestly', 'so', 'right', 'i mean']

function ScoreBar({ label, value }) {
  const pct = (value / 10) * 100
  const color = value >= 7 ? 'var(--accent-green)' : value >= 4 ? 'var(--accent-amber)' : 'var(--accent-red)'
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, marginBottom: 4 }}>
        <span style={{ textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{label}</span>
        <span style={{ fontFamily: 'var(--font-mono)' }}>{value}/10</span>
      </div>
      <div style={{ height: 6, background: 'var(--bg-panel-raised)', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, transition: 'width 0.5s ease' }} />
      </div>
    </div>
  )
}

export default function MockInterview() {
  const { runId } = useParams()
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [qIndex, setQIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [history, setHistory] = useState([]) // { question, answer, feedback }
  
  // Voice & Speech State
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [fillerCounts, setFillerCounts] = useState({})
  const [wpm, setWpm] = useState(0)
  const recognitionRef = useRef(null)
  const timerRef = useRef(null)

  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getPipelineStatus(runId)
      .then(s => { if (mounted) setStatus(s) })
      .catch(() => toast?.error('Could not load mock interview questions.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  // Speech Recognition Setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'

      recognition.onresult = (event) => {
        let transcript = ''
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript + ' '
        }
        setAnswer(transcript.trim())
      }

      recognition.onerror = (err) => {
        console.error('Speech recognition error:', err)
        setIsRecording(false)
      }

      recognition.onend = () => {
        setIsRecording(false)
      }

      recognitionRef.current = recognition
    }
  }, [])

  // Calculate Speech Analytics (Filler Words & WPM)
  useEffect(() => {
    if (!answer) {
      setFillerCounts({})
      setWpm(0)
      return
    }

    const words = answer.toLowerCase().split(/\s+/)
    const counts = {}
    let totalFillers = 0

    words.forEach(w => {
      const clean = w.replace(/[^a-z]/g, '')
      if (FILLER_WORDS.includes(clean)) {
        counts[clean] = (counts[clean] || 0) + 1
        totalFillers++
      }
    })

    setFillerCounts(counts)

    if (recordingTime > 0) {
      const minutes = recordingTime / 60
      setWpm(Math.round(words.length / minutes))
    }
  }, [answer, recordingTime])

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      toast?.error('Speech recognition is not supported in this browser. You can still type your answer!')
      return
    }

    if (isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
      clearInterval(timerRef.current)
    } else {
      setRecordingTime(0)
      recognitionRef.current.start()
      setIsRecording(true)
      timerRef.current = setInterval(() => {
        setRecordingTime(t => t + 1)
      }, 1000)
    }
  }

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1.0
      window.speechSynthesis.speak(utterance)
    }
  }

  const questions = status?.interview_prep?.questions || []
  const current = questions[qIndex]
  const answered = history.find(h => h.question === current?.question)

  const handleSubmit = async () => {
    if (!answer.trim()) return
    if (isRecording) toggleRecording()

    setSubmitting(true)
    try {
      const res = await api.submitMockAnswer(runId, { question: current.question, answer })
      setHistory(prev => [...prev, { question: current.question, answer, feedback: res.feedback }])
    } catch (err) {
      toast?.error('Could not score that answer — try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleNext = () => {
    window.speechSynthesis?.cancel()
    setAnswer('')
    setRecordingTime(0)
    setQIndex(i => Math.min(i + 1, questions.length - 1))
  }

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        <FlightPlan current={4} />
        <SkeletonBlock height={360} />
      </div>
    )
  }

  if (!questions.length) {
    return (
      <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
        <FlightPlan current={4} />
        <div className="panel">
          <p>No questions ready yet — finish interview prep first.</p>
          <button className="btn btn-secondary" style={{ marginTop: 12 }}
                  onClick={() => navigate(`/runs/${runId}/interview-prep`)}>Back to prep</button>
        </div>
      </div>
    )
  }

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={4} />

      <div className="fade-in">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <span className="eyebrow">MOCK INTERVIEW • QUESTION {qIndex + 1} OF {questions.length}</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-secondary" onClick={() => speakText(current.question)} title="Listen to question">
              🔊 Listen
            </button>
            {answered && (
              <button className="btn btn-secondary" onClick={handleNext} disabled={qIndex >= questions.length - 1}>
                Next question →
              </button>
            )}
          </div>
        </div>

        <div className="panel" style={{ marginBottom: 16, background: 'var(--bg-panel-raised)' }}>
          <h2 style={{ fontSize: 17, lineHeight: 1.5, color: 'var(--text-primary)' }}>{current.question}</h2>
        </div>

        {!answered ? (
          <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button 
                className={`btn ${isRecording ? 'btn-danger' : 'btn-secondary'}`}
                onClick={toggleRecording}
                type="button"
                style={{ borderRadius: 20 }}
              >
                {isRecording ? `🛑 Stop Recording (${recordingTime}s)` : '🎙️ Start Speaking'}
              </button>

              {recordingTime > 0 && (
                <div style={{ display: 'flex', gap: 12, fontSize: 12, fontFamily: 'var(--font-mono)' }}>
                  <span style={{ color: 'var(--accent-cyan)' }}>Speed: {wpm || 0} WPM</span>
                  <span style={{ color: Object.keys(fillerCounts).length > 0 ? 'var(--accent-amber)' : 'var(--accent-green)' }}>
                    Fillers: {Object.values(fillerCounts).reduce((a,b)=>a+b, 0)}
                  </span>
                </div>
              )}
            </div>

            <textarea
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              rows={6}
              placeholder="Click 'Start Speaking' or type your response here..."
              style={{ width: '100%', fontSize: 14, lineHeight: 1.6 }}
            />

            {/* Speech Analytics Box */}
            {Object.keys(fillerCounts).length > 0 && (
              <div style={{ background: 'rgba(245, 165, 36, 0.08)', border: '1px dashed var(--accent-amber)', borderRadius: 8, padding: 10, fontSize: 12 }}>
                ⚠️ <strong>Speech Analytics:</strong> Filler words detected: {' '}
                {Object.entries(fillerCounts).map(([w, c]) => (
                  <span key={w} style={{ background: 'rgba(245, 165, 36, 0.2)', padding: '2px 6px', borderRadius: 4, marginRight: 6 }}>
                    "{w}": {c}
                  </span>
                ))}
              </div>
            )}

            <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting || !answer.trim()}
                    style={{ marginTop: 4, justifyContent: 'center' }}>
              {submitting ? <span className="spinner" /> : 'Submit answer for AI feedback'}
            </button>
          </div>
        ) : (
          <div className="fade-in panel" style={{ borderColor: 'var(--accent-cyan)' }}>
            <p style={{ fontSize: 13, marginBottom: 4, color: 'var(--text-muted)' }}>Your Spoken / Typed Answer</p>
            <p style={{ fontSize: 13.5, marginBottom: 18, color: 'var(--text-primary)', background: 'var(--bg-panel-raised)', padding: 12, borderRadius: 8 }}>
              {answered.answer}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 20 }}>
              <div>
                <h4 style={{ fontSize: 13, marginBottom: 12, color: 'var(--accent-cyan)' }}>RUBRIC BREAKDOWN</h4>
                {Object.entries(answered.feedback.scores || {}).map(([k, v]) => (
                  <ScoreBar key={k} label={k.replace('_', ' ')} value={v} />
                ))}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--accent-green)' }}>{answered.feedback.overall_verdict}</p>
                  <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => speakText(answered.feedback.overall_verdict)}>
                    🔊 Read Verdict
                  </button>
                </div>
                {answered.feedback.strengths?.length > 0 && (
                  <div>
                    <span style={{ fontSize: 11.5, color: 'var(--accent-green)' }}>STRENGTHS</span>
                    <ul style={{ margin: '4px 0 0', paddingLeft: 16 }}>
                      {answered.feedback.strengths.map((s, i) => <li key={i} style={{ fontSize: 12.5 }}>{s}</li>)}
                    </ul>
                  </div>
                )}
                {answered.feedback.improvements?.length > 0 && (
                  <div>
                    <span style={{ fontSize: 11.5, color: 'var(--accent-amber)' }}>AREAS TO IMPROVE</span>
                    <ul style={{ margin: '4px 0 0', paddingLeft: 16 }}>
                      {answered.feedback.improvements.map((s, i) => <li key={i} style={{ fontSize: 12.5 }}>{s}</li>)}
                    </ul>
                  </div>
                )}
                {answered.feedback.suggested_rephrase && (
                  <div style={{ background: 'var(--bg-panel-raised)', borderLeft: '3px solid var(--accent-cyan)', padding: 10, fontSize: 12.5, borderRadius: 4 }}>
                    💡 <strong>Suggested Rephrase:</strong> {answered.feedback.suggested_rephrase}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginTop: 24 }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/interview-prep`)}>
            ← Back to Interview Prep
          </button>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/battlecard`)} style={{ borderColor: 'var(--accent-amber)', color: 'var(--accent-amber)' }}>
              Skip to Battlecard ⏭️
            </button>
            <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/elevator-pitch`)} style={{ borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)' }}>
              Skip to Pitch 🎙️
            </button>
            <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/battlecard`)}>
              Next: View Battlecard →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
