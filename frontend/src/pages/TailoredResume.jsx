import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

function FormattedResumeView({ content }) {
  if (!content) return <span style={{ color: 'var(--text-muted)' }}>No resume content available.</span>

  const lines = content.split('\n')
  const elements = []
  let nameRendered = false

  lines.forEach((rawLine, i) => {
    const line = rawLine.trim()
    if (!line) return

    // # Candidate Name Header
    if (line.startsWith('# ') && !nameRendered) {
      nameRendered = true
      elements.push(
        <div key={i} style={{ marginBottom: 4 }}>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--accent-cyan)', letterSpacing: '0.02em', textTransform: 'uppercase' }}>
            {line.replace('# ', '')}
          </h1>
        </div>
      )
    }
    // Contact line (right under name)
    else if (nameRendered && elements.length === 1 && !line.startsWith('#')) {
      elements.push(
        <div key={i} style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginBottom: 12, paddingBottom: 10, borderBottom: '1px solid var(--accent-cyan)' }}>
          {line}
        </div>
      )
    }
    // ## Section Heading
    else if (line.startsWith('## ')) {
      elements.push(
        <div key={i} style={{ marginTop: 18, marginBottom: 8 }}>
          <h2 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 4, height: 14, background: 'var(--accent-cyan)', borderRadius: 2, display: 'inline-block' }} />
            {line.replace('## ', '')}
          </h2>
          <div style={{ height: 1, background: 'var(--line)', marginTop: 4, marginBottom: 8 }} />
        </div>
      )
    }
    // ### Job / Project Subheading
    else if (line.startsWith('### ')) {
      elements.push(
        <div key={i} style={{ marginTop: 10, marginBottom: 4, fontWeight: 600, fontSize: 13, color: 'var(--accent-amber)' }}>
          {line.replace('### ', '')}
        </div>
      )
    }
    // Bullet points (- or * or •)
    else if (line.startsWith('- ') || line.startsWith('* ') || line.startsWith('• ')) {
      const cleanBullet = line.replace(/^[-*•]\s+/, '')
      const parts = cleanBullet.split(/(\*\*.*?\*\*)/g)
      elements.push(
        <div key={i} style={{ display: 'flex', gap: 8, fontSize: 13, lineHeight: 1.6, color: 'var(--text-secondary)', marginBottom: 4, paddingLeft: 8 }}>
          <span style={{ color: 'var(--accent-cyan)', flexShrink: 0 }}>•</span>
          <div>
            {parts.map((p, pi) => {
              if (p.startsWith('**') && p.endsWith('**')) {
                return <strong key={pi} style={{ color: 'var(--text-primary)' }}>{p.slice(2, -2)}</strong>
              }
              return p
            })}
          </div>
        </div>
      )
    }
    // Regular paragraph
    else {
      const parts = line.split(/(\*\*.*?\*\*)/g)
      elements.push(
        <p key={i} style={{ fontSize: 13, lineHeight: 1.6, color: 'var(--text-secondary)', marginBottom: 6 }}>
          {parts.map((p, pi) => {
            if (p.startsWith('**') && p.endsWith('**')) {
              return <strong key={pi} style={{ color: 'var(--text-primary)' }}>{p.slice(2, -2)}</strong>
            }
            return p
          })}
        </p>
      )
    }
  })

  return <div style={{ display: 'flex', flexDirection: 'column' }}>{elements}</div>
}

export default function TailoredResume() {
  const { runId } = useParams()
  const [status, setStatus] = useState(null)
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [submitting, setSubmitting] = useState(null) // 'approve' | 'reject' | null
  const [downloading, setDownloading] = useState(false)
  const navigate = useNavigate()
  const toast = useToast()

  useEffect(() => {
    let mounted = true
    api.getPipelineStatus(runId)
      .then(s => {
        if (!mounted) return
        setStatus(s)
        setContent(s.tailored_resume_draft || '')
      })
      .catch(() => toast?.error('Could not load the tailored resume.'))
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [runId])

  const isApproved = status?.status === 'completed'

  const handleApprove = async () => {
    setSubmitting('approve')
    try {
      await api.approveTailoring(runId, { approved: true, edited_content: content })
      toast?.success('Approved! Your tailored resume PDF is ready for download.')
      setStatus(prev => ({ ...prev, status: 'completed' }))
    } catch (err) {
      toast?.error('Could not approve — try again.')
    } finally {
      setSubmitting(null)
    }
  }

  const handleReject = async () => {
    setSubmitting('reject')
    try {
      await api.approveTailoring(runId, { approved: false })
      toast?.info('Rejected. The pipeline stopped here.')
      setStatus(prev => ({ ...prev, status: 'rejected' }))
    } catch (err) {
      toast?.error('Could not reject — try again.')
    } finally {
      setSubmitting(null)
    }
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const res = await api.downloadTailoredResume(runId)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'tailored_resume.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast?.success('Resume PDF downloaded successfully!')
    } catch (err) {
      toast?.error('Could not download resume PDF — try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <FlightPlan current={2} />

      {loading ? (
        <SkeletonBlock height={400} />
      ) : (
        <div className="fade-in">
          {/* Header Action Card */}
          <div className="panel" style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20,
            borderColor: isApproved ? 'var(--accent-green)' : 'var(--accent-amber)',
            background: isApproved ? 'rgba(74, 222, 128, 0.06)' : 'rgba(245, 165, 36, 0.06)',
            flexWrap: 'wrap', gap: 14
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 22 }}>{isApproved ? '✓' : '⏸'}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: isApproved ? 'var(--accent-green)' : 'var(--accent-amber)' }}>
                  {isApproved ? 'Tailored Resume Approved & PDF Unlocked' : 'Human Checkpoint — Review & Approve Draft'}
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
                  {isApproved ? 'Download your tailored PDF below or proceed to Interview Prep.' : 'Review your executive AI-tailored resume draft. Click Approve to unlock high-res PDF download.'}
                </div>
              </div>
            </div>

            {isApproved && (
              <button className="btn btn-primary" onClick={handleDownload} disabled={downloading} style={{ background: 'var(--accent-green)', color: '#06231F', fontWeight: 700 }}>
                {downloading ? <span className="spinner" /> : '📥 Download Tailored Resume PDF'}
              </button>
            )}
          </div>

          {status?.tailoring_reflection_notes && (
            <div className="badge" style={{ marginBottom: 16, borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)', padding: '6px 12px' }}>
              🛡️ Anti-Fabrication Fact Check: {status.tailoring_reflection_notes}
            </div>
          )}

          {/* Resume Studio Document Box */}
          <div className="panel" style={{ marginBottom: 20, background: 'var(--bg-panel-raised)', border: '1px solid var(--line)', padding: 28, borderRadius: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, borderBottom: '1px solid var(--line)', paddingBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 16 }}>📄</span>
                <h3 style={{ fontSize: 15, fontWeight: 700 }}>Tailored Executive Resume</h3>
              </div>
              {!isApproved && (
                <button className="btn btn-secondary" onClick={() => setEditing(e => !e)} style={{ fontSize: 12, padding: '6px 12px' }}>
                  {editing ? '👁️ Switch to Visual Preview' : '✏️ Edit Resume Text'}
                </button>
              )}
            </div>

            {editing && !isApproved ? (
              <textarea
                value={content}
                onChange={e => setContent(e.target.value)}
                rows={20}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: 13, lineHeight: 1.6, background: 'var(--bg-deep)' }}
              />
            ) : (
              <div style={{ padding: '8px 4px' }}>
                <FormattedResumeView content={content} />
              </div>
            )}
          </div>

          {/* Bottom Action Controls */}
          {isApproved ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-panel)', padding: 16, borderRadius: 12, border: '1px solid var(--accent-green)' }}>
              <div>
                <span style={{ fontSize: 13, color: 'var(--accent-green)', fontWeight: 600 }}>✓ Tailored Resume Approved</span>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>Your PDF export is ready with executive formatting.</p>
              </div>
              <button className="btn btn-primary" onClick={handleDownload} disabled={downloading} style={{ background: 'var(--accent-green)', color: '#06231F' }}>
                {downloading ? <span className="spinner" /> : '📥 Download Resume PDF'}
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 12 }}>
              <button className="btn btn-primary" onClick={handleApprove} disabled={!!submitting} style={{ flex: 1, justifyContent: 'center', padding: '14px', fontSize: 15, fontWeight: 700 }}>
                {submitting === 'approve' ? <span className="spinner" /> : '✓ Approve & Resume Pipeline →'}
              </button>
              <button className="btn btn-danger" onClick={handleReject} disabled={!!submitting} style={{ padding: '14px 20px' }}>
                {submitting === 'reject' ? <span className="spinner" /> : 'Reject'}
              </button>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 24 }}>
            <button className="btn btn-secondary" onClick={() => navigate(`/runs/${runId}/gap-analysis`)}>
              ← Back to Gap Analysis
            </button>
            <button className="btn btn-primary" onClick={() => navigate(`/runs/${runId}/interview-prep`)}>
              Next: Interview Prep →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
