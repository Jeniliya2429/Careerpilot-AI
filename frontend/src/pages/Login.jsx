import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '../api/client.js'
import { useAuth } from '../api/AuthContext.jsx'

export default function Login() {
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
      const res = await api.login({ email, password })
      login(res.access_token, res.user)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Sign in failed. Check your details and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420, paddingTop: 80 }}>
      <div className="eyebrow" style={{ marginBottom: 8 }}>WELCOME BACK</div>
      <h1 style={{ fontSize: 30, marginBottom: 24 }}>Sign in to your flight deck</h1>

      <form onSubmit={submit} className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {error && <div className="error-box">{error}</div>}
        <label style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Email
          <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                 placeholder="you@example.com" style={{ width: '100%', marginTop: 6 }} />
        </label>
        <label style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Password
          <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
                 placeholder="••••••••" style={{ width: '100%', marginTop: 6 }} />
        </label>
        <button className="btn btn-primary" type="submit" disabled={loading} style={{ marginTop: 8, justifyContent: 'center' }}>
          {loading ? <span className="spinner" /> : 'Sign in'}
        </button>
      </form>

      <p style={{ marginTop: 16, fontSize: 13 }}>
        New here? <Link to="/register" style={{ color: 'var(--accent-cyan)' }}>Create an account</Link>
      </p>
    </div>
  )
}
