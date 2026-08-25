import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../api/AuthContext.jsx'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.register({ name, email, password })
      login(res.access_token, res.user)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try a different email.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420, paddingTop: 80 }}>
      <div className="eyebrow" style={{ marginBottom: 8 }}>GET STARTED</div>
      <h1 style={{ fontSize: 30, marginBottom: 24 }}>Create your account</h1>

      <form onSubmit={submit} className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {error && <div className="error-box">{error}</div>}
        <label style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Name
          <input required value={name} onChange={e => setName(e.target.value)}
                 placeholder="Jane Doe" style={{ width: '100%', marginTop: 6 }} />
        </label>
        <label style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Email
          <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                 placeholder="you@example.com" style={{ width: '100%', marginTop: 6 }} />
        </label>
        <label style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Password
          <input type="password" required minLength={6} value={password} onChange={e => setPassword(e.target.value)}
                 placeholder="At least 6 characters" style={{ width: '100%', marginTop: 6 }} />
        </label>
        <button className="btn btn-primary" type="submit" disabled={loading} style={{ marginTop: 8, justifyContent: 'center' }}>
          {loading ? <span className="spinner" /> : 'Create account'}
        </button>
      </form>

      <p style={{ marginTop: 16, fontSize: 13 }}>
        Already have an account? <Link to="/login" style={{ color: 'var(--accent-cyan)' }}>Sign in</Link>
      </p>
    </div>
  )
}
