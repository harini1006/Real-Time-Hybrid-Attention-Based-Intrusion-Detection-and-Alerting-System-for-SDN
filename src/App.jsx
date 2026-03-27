import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import UploadLogs from './pages/UploadLogs'
import RealTimeMonitoring from './pages/RealTimeMonitoring'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import ModelPerformance from './pages/ModelPerformance'

function App() {
  const [token, setToken] = useState(null)
  const [checking, setChecking] = useState(true)

  // Validate existing token on load
  useEffect(() => {
    const saved = localStorage.getItem('ids_token')
    if (saved) {
      // Verify token is still valid by hitting a protected-ish endpoint
      fetch('http://localhost:8000/api/health')
        .then(res => {
          if (res.ok) setToken(saved)
          else localStorage.removeItem('ids_token')
        })
        .catch(() => localStorage.removeItem('ids_token'))
        .finally(() => setChecking(false))
    } else {
      setChecking(false)
    }
  }, [])

  const handleLogin = (newToken) => {
    localStorage.setItem('ids_token', newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('ids_token')
    setToken(null)
  }

  if (checking) return null

  if (!token) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <Layout onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/upload" element={<UploadLogs token={token} />} />
        <Route path="/realtime" element={<RealTimeMonitoring token={token} />} />
        <Route path="/dashboard" element={<Dashboard token={token} />} />
        <Route path="/alerts" element={<Alerts token={token} />} />
        <Route path="/performance" element={<ModelPerformance token={token} />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
