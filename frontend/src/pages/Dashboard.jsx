import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

export default function Dashboard() {
  const [resumes, setResumes] = useState([])
  const [jds, setJds] = useState([])
  const [selectedResume, setSelectedResume] = useState('')
  const [selectedJd, setSelectedJd] = useState('')

  const [uploading, setUploading] = useState(false)
  const [jdText, setJdText] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [addingJd, setAddingJd] = useState(false)

  const [launching, setLaunching] = useState(false)
  const [error, setError] = useState('')

  const navigate = useNavigate()

  const refresh = async () => {
    const [r, j] = await Promise.all([api.listResumes(), api.listJDs()])
    setResumes(r)
    setJds(j)
    if (r.length) setSelectedResume(r[0].id)
    if (j.length) setSelectedJd(j[0].id)
  }

  useEffect(() => { refresh() }, [])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      await api.uploadResume(file)
      await refresh()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Try a text-based PDF.')
    } finally {
      setUploading(false)
    }
  }

  const handleAddJd = async (e) => {
    e.preventDefault()
    setAddingJd(true)
    setError('')
    try {
      await api.createJD({ raw_text: jdText, company_name: companyName, role_title: roleTitle })
      setJdText(''); setCompanyName(''); setRoleTitle('')
      await refresh()
    } catch (err) {
      setError('Could not save job description.')
    } finally {
      setAddingJd(false)
    }
  }

  const handleLaunch = async () => {
    if (!selectedResume || !selectedJd) {
      setError('Please select both a resume and a job description to launch.')
      return
    }
    setLaunching(true)
    setError('')
    try {
      const result = await api.runPipeline({ resume_id: selectedResume, jd_id: selectedJd })
      navigate(`/runs/${result.run_id}/gap-analysis`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not start the pipeline run.')
    } finally {
      setLaunching(false)
    }
  }

  const loadSampleJd = () => {
    setCompanyName('TechCorp AI')
    setRoleTitle('Senior Software Engineer')
    setJdText('We are seeking an experienced Senior Software Engineer to build scalable microservices, cloud infrastructure (AWS/Docker), and API integration pipelines. Requires proficiency in Python/Node.js, PostgreSQL, and system design.')
  }

  return (
    <div className="container fade-in" style={{ paddingTop: 36, paddingBottom: 60 }}>
      {/* Hero Animated Banner */}
      <div className="panel pulse-glow" style={{
        marginBottom: 32,
        background: 'linear-gradient(135deg, #0B1220 0%, #16243E 100%)',
        border: '1px solid var(--accent-cyan)',
        position: 'relative',
        overflow: 'hidden',
        padding: 28,
        borderRadius: 16
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div className="eyebrow" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 8, background: 'rgba(52, 211, 201, 0.1)', padding: '4px 10px', borderRadius: 20 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent-cyan)', display: 'inline-block' }} />
              AUTONOMOUS CAREERPILOT AGENT
            </div>
            <h1 style={{ fontSize: 26, color: 'var(--text-primary)', marginBottom: 8, lineHeight: 1.3 }}>
              AI Flight Control & Application Tailoring Studio
            </h1>
            <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', maxWidth: 620, lineHeight: 1.6 }}>
              Upload your resume, paste a target job description, and watch our multi-agent system generate ATS gap analysis, truthful bullet tailoring, voice mock interview rubrics, and a 60-second teleprompter pitch.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ background: 'rgba(18, 27, 46, 0.8)', border: '1px solid var(--line)', padding: '10px 14px', borderRadius: 10, textAlign: 'center' }}>
              <span style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent-green)', display: 'block', fontFamily: 'var(--font-mono)' }}>98.4%</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>ATS Pass Target</span>
            </div>
            <div style={{ background: 'rgba(18, 27, 46, 0.8)', border: '1px solid var(--line)', padding: '10px 14px', borderRadius: 10, textAlign: 'center' }}>
              <span style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent-amber)', display: 'block', fontFamily: 'var(--font-mono)' }}>Real</span>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Human Guardrail</span>
            </div>
          </div>
        </div>
      </div>

      {error && <div className="error-box" style={{ marginBottom: 24 }}>⚠️ {error}</div>}

      {/* 2-Column Selection Studio */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 24, marginBottom: 28 }}>
        
        {/* Step 1: Resume Studio */}
        <div className="panel step-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--accent-cyan)', color: '#06231F', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13 }}>
                1
              </div>
              <h3 style={{ fontSize: 16 }}>Select or Upload Resume</h3>
            </div>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>PDF Format</span>
          </div>

          <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Upload a text-based PDF. The agent extracts your experience and skills cleanly.
          </p>

          <label className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center', marginBottom: 16, borderStyle: 'dashed' }}>
            {uploading ? <span className="spinner" /> : '📁 Upload New PDF Resume'}
            <input type="file" accept="application/pdf" onChange={handleUpload} hidden disabled={uploading} />
          </label>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 180, overflowY: 'auto' }}>
            {resumes.length === 0 ? (
              <span style={{ fontSize: 12.5, color: 'var(--text-muted)', textAlign: 'center', padding: 12 }}>No resumes uploaded yet. Upload your PDF above.</span>
            ) : (
              resumes.map(r => (
                <label key={r.id} style={{
                  display: 'flex', alignItems: 'center', gap: 10, fontSize: 13,
                  padding: '10px 12px', borderRadius: 8, cursor: 'pointer',
                  background: selectedResume === r.id ? 'var(--bg-panel-raised)' : 'var(--bg-deep)',
                  border: `1px solid ${selectedResume === r.id ? 'var(--accent-cyan)' : 'var(--line)'}`,
                  transition: 'all 0.15s ease',
                  minWidth: 0,
                  boxSizing: 'border-box'
                }}>
                  <input type="radio" name="resume" checked={selectedResume === r.id} onChange={() => setSelectedResume(r.id)} style={{ flexShrink: 0 }} />
                  <span style={{ flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.filename}</span>
                  {selectedResume === r.id && <span style={{ color: 'var(--accent-cyan)', fontSize: 11, flexShrink: 0 }}>Selected</span>}
                </label>
              ))
            )}
          </div>
        </div>

        {/* Step 2: Job Description Studio */}
        <div className="panel step-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--accent-cyan)', color: '#06231F', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13 }}>
                2
              </div>
              <h3 style={{ fontSize: 16 }}>Target Job Description</h3>
            </div>
            <button className="btn btn-secondary" onClick={loadSampleJd} style={{ fontSize: 11, padding: '3px 8px' }}>
              Load Sample
            </button>
          </div>

          <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginBottom: 16 }}>
            Paste the job posting details for the exact position you are applying to.
          </p>

          <form onSubmit={handleAddJd} style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 8, width: '100%', boxSizing: 'border-box' }}>
              <input 
                placeholder="Company Name" 
                value={companyName} 
                onChange={e => setCompanyName(e.target.value)} 
                style={{ width: '100%', minWidth: 0, boxSizing: 'border-box' }} 
              />
              <input 
                placeholder="Role Title" 
                value={roleTitle} 
                onChange={e => setRoleTitle(e.target.value)} 
                style={{ width: '100%', minWidth: 0, boxSizing: 'border-box' }} 
              />
            </div>
            <textarea 
              placeholder="Paste job description text here..." 
              rows={3} 
              required 
              value={jdText} 
              onChange={e => setJdText(e.target.value)} 
              style={{ width: '100%', minWidth: 0, boxSizing: 'border-box', resize: 'vertical' }}
            />
            <button className="btn btn-secondary" type="submit" disabled={addingJd} style={{ justifyContent: 'center' }}>
              {addingJd ? <span className="spinner" /> : 'Save Job Description'}
            </button>
          </form>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 120, overflowY: 'auto' }}>
            {jds.length === 0 ? (
              <span style={{ fontSize: 12.5, color: 'var(--text-muted)', textAlign: 'center', padding: 8 }}>No job descriptions saved yet.</span>
            ) : (
              jds.map(j => (
                <label key={j.id} style={{
                  display: 'flex', alignItems: 'center', gap: 10, fontSize: 13,
                  padding: '8px 10px', borderRadius: 8, cursor: 'pointer',
                  background: selectedJd === j.id ? 'var(--bg-panel-raised)' : 'var(--bg-deep)',
                  border: `1px solid ${selectedJd === j.id ? 'var(--accent-cyan)' : 'var(--line)'}`,
                  minWidth: 0,
                  boxSizing: 'border-box'
                }}>
                  <input type="radio" name="jd" checked={selectedJd === j.id} onChange={() => setSelectedJd(j.id)} style={{ flexShrink: 0 }} />
                  <span style={{ flex: 1, minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    <strong>{j.role_title || 'Untitled Role'}</strong> {j.company_name && `— ${j.company_name}`}
                  </span>
                </label>
              ))
            )}
          </div>
        </div>

      </div>

      {/* Large Launch Call-To-Action */}
      <div className="panel pulse-glow" style={{ textAlign: 'center', background: 'var(--bg-panel-raised)', padding: 24, borderRadius: 14 }}>
        <button 
          className="btn btn-primary" 
          onClick={handleLaunch} 
          disabled={launching || !selectedResume || !selectedJd}
          style={{ 
            width: '100%', 
            maxWidth: 500,
            margin: '0 auto', 
            justifyContent: 'center', 
            padding: '16px 24px', 
            fontSize: 16,
            fontWeight: 700,
            borderRadius: 10
          }}
        >
          {launching ? <span className="spinner" /> : '🚀 Launch AI Agent Flight Plan →'}
        </button>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 10 }}>
          Starts Parse ➔ Gap Analysis ➔ Tailored Draft ➔ Human Checkpoint loop.
        </p>
      </div>

      {/* Visual Agent Workflow Architecture */}
      <div style={{ marginTop: 40 }}>
        <span className="eyebrow" style={{ display: 'block', marginBottom: 12, textAlign: 'center' }}>AGENT ARCHITECTURE & PIPELINE STEPS</span>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          <div className="panel" style={{ textAlign: 'center', padding: 16 }}>
            <span style={{ fontSize: 24, display: 'block', marginBottom: 6 }}>📊</span>
            <h4 style={{ fontSize: 14, marginBottom: 4 }}>1. ATS Gap Analysis</h4>
            <p style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>Scans resume vs JD to compute keyword match score and formatting compliance.</p>
          </div>
          <div className="panel" style={{ textAlign: 'center', padding: 16, border: '1px solid var(--accent-amber)' }}>
            <span style={{ fontSize: 24, display: 'block', marginBottom: 6 }}>⏸️</span>
            <h4 style={{ fontSize: 14, marginBottom: 4, color: 'var(--accent-amber)' }}>2. Human Approval</h4>
            <p style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>Review and edit AI-tailored resume draft before unlocking PDF export.</p>
          </div>
          <div className="panel" style={{ textAlign: 'center', padding: 16 }}>
            <span style={{ fontSize: 24, display: 'block', marginBottom: 6 }}>🎙️</span>
            <h4 style={{ fontSize: 14, marginBottom: 4 }}>3. Voice Mock Interview</h4>
            <p style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>Practice questions with voice transcription, filler word counter, and STAR rubric scoring.</p>
          </div>
          <div className="panel" style={{ textAlign: 'center', padding: 16 }}>
            <span style={{ fontSize: 24, display: 'block', marginBottom: 6 }}>📜</span>
            <h4 style={{ fontSize: 14, marginBottom: 4 }}>4. Role-Tailored Pitch</h4>
            <p style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>Practice your custom 60-second elevator pitch with on-screen teleprompter.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
