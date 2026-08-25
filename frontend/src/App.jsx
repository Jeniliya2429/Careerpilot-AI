import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './api/AuthContext.jsx'
import { ToastProvider } from './components/Toast.jsx'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'

import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import GapAnalysis from './pages/GapAnalysis.jsx'
import TailoredResume from './pages/TailoredResume.jsx'
import InterviewPrep from './pages/InterviewPrep.jsx'
import MockInterview from './pages/MockInterview.jsx'
import Battlecard from './pages/Battlecard.jsx'
import ActionPlan from './pages/ActionPlan.jsx'
import SalaryNegotiation from './pages/SalaryNegotiation.jsx'
import ElevatorPitch from './pages/ElevatorPitch.jsx'

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <div className="app-shell">
            <Navbar />
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/runs/:runId/gap-analysis" element={<ProtectedRoute><GapAnalysis /></ProtectedRoute>} />
              <Route path="/runs/:runId/tailored-resume" element={<ProtectedRoute><TailoredResume /></ProtectedRoute>} />
              <Route path="/runs/:runId/interview-prep" element={<ProtectedRoute><InterviewPrep /></ProtectedRoute>} />
              <Route path="/runs/:runId/mock-interview" element={<ProtectedRoute><MockInterview /></ProtectedRoute>} />
              <Route path="/runs/:runId/battlecard" element={<ProtectedRoute><Battlecard /></ProtectedRoute>} />
              <Route path="/runs/:runId/action-plan" element={<ProtectedRoute><ActionPlan /></ProtectedRoute>} />
              <Route path="/runs/:runId/salary-negotiation" element={<ProtectedRoute><SalaryNegotiation /></ProtectedRoute>} />
              <Route path="/runs/:runId/elevator-pitch" element={<ProtectedRoute><ElevatorPitch /></ProtectedRoute>} />
            </Routes>
          </div>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  )
}
