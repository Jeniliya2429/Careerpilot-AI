import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { SkeletonBlock } from '../components/Skeleton.jsx'
import FlightPlan from '../components/FlightPlan.jsx'

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
          <div className="panel" style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20,
            borderColor: isApproved ? 'var(--accent-green)' : 'var(--accent-amber)',
            background: isApproved ? 'rgba(74, 222, 128, 0.06)' : 'rgba(245, 165, 36, 0.06)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 20 }}>{isApproved ? '✓' : '⏸'}</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: 14 }}>
                  {isApproved ? 'Tailored Resume Approved & Unlocked' : 'Human Checkpoint — Review & Approve'}
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
                  {isApproved ? 'Download your tailored PDF below or proceed to Interview Prep.' : 'Review your AI-tailored resume draft. Click Approve to unlock PDF download & interview prep.'}
                </div>
              </div>
            </div>

            {isApproved && (
              <button className="btn btn-primary" onClick={handleDownload} disabled={downloading} style={{ background: 'var(--accent-green)', color: '#06231F' }}>
                {downloading ? <span className="spinner" /> : '📥 Download Tailored Resume PDF'}
              </button>
            )}
          </div>

          {status?.tailoring_reflection_notes && (
            <div className="badge" style={{ marginBottom: 16, borderColor: 'var(--accent-cyan)', color: 'var(--accent-cyan)' }}>
              ✓ Self-reflection check: {status.tailoring_reflection_notes}
            </div>
          )}

          <div className="panel" style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ fontSize: 14 }}>Tailored Resume Content</h3>
              {!isApproved && (
                <button className="btn btn-secondary" onClick={() => setEditing(e => !e)}>
                  {editing ? 'Preview' : 'Edit Draft'}
                </button>
              )}
            </div>

            {editing && !isApproved ? (
              <textarea
                value={content}
                onChange={e => setContent(e.target.value)}
                rows={18}
                style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: 13, lineHeight: 1.6 }}
              />
            ) : (
              <pre style={{
                whiteSpace: 'pre-wrap', fontFamily: 'var(--font-body)', fontSize: 13.5,
                lineHeight: 1.7, color: 'var(--text-primary)', margin: 0,
              }}>{content}</pre>
            )}
          </div>

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
              <button className="btn btn-primary" onClick={handleApprove} disabled={!!submitting} style={{ flex: 1, justifyContent: 'center' }}>
                {submitting === 'approve' ? <span className="spinner" /> : 'Approve & Resume Pipeline →'}
              </button>
              <button className="btn btn-danger" onClick={handleReject} disabled={!!submitting}>
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
