import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000/api'

export default function ModelPerformance({ token }) {
  const [metrics, setMetrics] = useState(null)

  useEffect(() => {
    axios.get(`${API}/metrics`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setMetrics(res.data))
      .catch(() => {})
  }, [])

  if (!metrics) return (
    <div className="animate-in">
      <div className="page-header"><h1 className="page-title">Model Performance</h1></div>
      <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
        <div style={{ fontSize: '40px', marginBottom: '12px', opacity: 0.5 }}>⏳</div>
        <p style={{ color: 'var(--text-muted)' }}>Loading metrics...</p>
      </div>
    </div>
  )

  const metricCards = [
    { label: 'Accuracy', value: metrics.accuracy, icon: '🎯', color: 'blue' },
    { label: 'Precision', value: metrics.precision, icon: '📐', color: 'purple' },
    { label: 'Recall', value: metrics.recall, icon: '📡', color: 'cyan' },
    { label: 'F1-Score', value: metrics.f1_score, icon: '⚖️', color: 'green' },
  ]

  const cm = metrics.confusion_matrix || []
  const classNames = metrics.class_names || []

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Model Performance</h1>
        <p className="page-subtitle">Hybrid Attention-Based Neural Network — evaluation metrics</p>
      </div>

      <div className="stats-grid">
        {metricCards.map(m => (
          <div className="stat-card" key={m.label}>
            <div className={`stat-icon ${m.color}`}>{m.icon}</div>
            <div className="stat-info">
              <div className="stat-value">{(m.value * 100).toFixed(2)}%</div>
              <div className="stat-label">{m.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <div className="stat-card"><div className="stat-icon yellow">⏱️</div><div className="stat-info"><div className="stat-value">{metrics.training_time_seconds?.toFixed(0)}s</div><div className="stat-label">Training Time</div></div></div>
        <div className="stat-card"><div className="stat-icon blue">📊</div><div className="stat-info"><div className="stat-value">{metrics.total_samples?.toLocaleString()}</div><div className="stat-label">Total Samples</div></div></div>
        <div className="stat-card"><div className="stat-icon green">🏷️</div><div className="stat-info"><div className="stat-value">{classNames.length}</div><div className="stat-label">Classes</div></div></div>
      </div>

      {cm.length > 0 && (
        <div className="card" style={{ marginTop: '4px' }}>
          <div className="card-title">Confusion Matrix</div>
          <div className="table-container">
            <table style={{ fontSize: '11px' }}>
              <thead>
                <tr>
                  <th style={{ minWidth: '120px' }}>Actual ↓ / Pred →</th>
                  {classNames.map((c, i) => <th key={i} style={{ textAlign: 'center', padding: '8px 4px', fontSize: '9px' }}>{c.length > 12 ? c.slice(0, 12) + '…' : c}</th>)}
                </tr>
              </thead>
              <tbody>
                {cm.map((row, i) => {
                  const rowMax = Math.max(...row)
                  return (
                    <tr key={i}>
                      <td style={{ fontWeight: 600, fontSize: '10px' }}>{classNames[i]?.length > 15 ? classNames[i].slice(0, 15) + '…' : classNames[i]}</td>
                      {row.map((val, j) => {
                        const intensity = rowMax > 0 ? val / rowMax : 0
                        const bg = i === j
                          ? `rgba(16, 185, 129, ${0.1 + intensity * 0.5})`
                          : val > 0 ? `rgba(239, 68, 68, ${0.1 + intensity * 0.4})` : 'transparent'
                        return <td key={j} style={{ textAlign: 'center', background: bg, padding: '6px 4px', fontWeight: i === j ? 700 : 400 }}>{val}</td>
                      })}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {classNames.length > 0 && (
        <div className="card" style={{ marginTop: '20px' }}>
          <div className="card-title">Detected Classes</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {classNames.map((c, i) => (
              <span key={i} className={`badge ${c === 'BENIGN' ? 'success' : 'danger'}`}>{c}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
