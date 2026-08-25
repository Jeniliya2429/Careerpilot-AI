import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../api/AuthContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header style={{
      borderBottom: '1px solid var(--line)',
      background: 'rgba(11, 18, 32, 0.85)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 10,
    }}>
      <div className="container" style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64,
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 7,
            background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-amber))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 14, fontWeight: 700, color: '#06231F',
          }}>◆</div>
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 17 }}>
            CareerPilot <span style={{ color: 'var(--accent-cyan)' }}>AI</span>
          </span>
        </Link>

        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{user.email}</span>
            <button className="btn btn-secondary" onClick={() => { logout(); navigate('/login') }}>
              Sign out
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn btn-primary">Sign in</Link>
        )}
      </div>
    </header>
  )
}
