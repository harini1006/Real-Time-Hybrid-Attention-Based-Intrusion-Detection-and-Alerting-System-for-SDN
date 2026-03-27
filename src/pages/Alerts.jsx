import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000/api'

export default function Alerts({ token }) {
  const [alerts, setAlerts] = useState([])
  const [filter, setFilter] = useState('')
  const [page, setPage] = useState(1)
  const perPage = 15

  const fetchAlerts = async () => {
    try {
      const url = filter ? `${API}/alerts?limit=500&attack_type=${filter}` : `${API}/alerts?limit=500`
      const res = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } })
      setAlerts(res.data.alerts || [])
    } catch {}
  }

  useEffect(() => {
    fetchAlerts()
    const i = setInterval(fetchAlerts, 5000)
    return () => clearInterval(i)
  }, [filter])

  const types = [...new Set(alerts.map((a) => a.attack_type))]
  const totalPages = Math.ceil(alerts.length / perPage)
  const paginated = alerts.slice((page - 1) * perPage, page * perPage)

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Security Alerts</h1>
        <p className="page-subtitle">Detected threats and security events</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon red">🔔</div>
          <div className="stat-info">
            <div className="stat-value">{alerts.length}</div>
            <div className="stat-label">Total Alerts</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon purple">🏷️</div>
          <div className="stat-info">
            <div className="stat-value">{types.length}</div>
            <div className="stat-label">Attack Types</div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="filter-bar">
          <select
            className="filter-select"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value)
              setPage(1)
            }}
          >
            <option value="">All Attack Types</option>
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <button className="btn btn-outline" onClick={fetchAlerts}>🔄 Refresh</button>
        </div>

        {alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '40px', marginBottom: '12px', opacity: 0.5 }}>🔔</div>
            <p>No alerts recorded yet</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Attack Type</th>
                    <th>Confidence</th>
                    <th>Source</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((a, i) => (
                    <tr key={i}>
                      <td style={{ whiteSpace: 'nowrap' }}>{new Date(a.timestamp).toLocaleString()}</td>
                      <td style={{ fontWeight: 600 }}>{a.attack_type}</td>
                      <td>{Number(a.confidence).toFixed(1)}%</td>
                      <td style={{ color: 'var(--text-muted)' }}>{a.flow_info?.source || '—'}</td>
                      <td>
                        <span className={`badge ${a.confidence > 90 ? 'danger' : a.confidence > 70 ? 'warning' : 'info'}`}>
                          {a.confidence > 90 ? '🔴 Critical' : a.confidence > 70 ? '🟡 High' : '🔵 Medium'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {totalPages > 1 && (
              <div className="pagination">
                <button className="page-btn" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
                  ←
                </button>
                <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                  Page {page} / {totalPages}
                </span>
                <button
                  className="page-btn"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
