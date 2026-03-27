import { useState, useEffect } from 'react'
import { Pie, Bar } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import axios from 'axios'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)
const API = 'http://localhost:8000/api'

export default function Dashboard({ token }) {
  const [stats, setStats] = useState(null)
  const [alerts, setAlerts] = useState([])

  const fetchData = async () => {
    try {
      const [s, a] = await Promise.all([
        axios.get(`${API}/dashboard/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/alerts?limit=5`, { headers: { Authorization: `Bearer ${token}` } }),
      ])
      setStats(s.data)
      setAlerts(a.data.alerts || [])
    } catch {}
  }

  useEffect(() => { fetchData(); const i = setInterval(fetchData, 5000); return () => clearInterval(i) }, [])

  const pieData = stats?.attack_distribution ? {
    labels: Object.keys(stats.attack_distribution),
    datasets: [{ data: Object.values(stats.attack_distribution), backgroundColor: ['#3b82f6','#ef4444','#f59e0b','#10b981','#8b5cf6','#06b6d4','#f97316','#e11d48','#7c3aed','#14b8a6'], borderWidth: 0 }]
  } : null

  const barData = stats?.attack_distribution ? {
    labels: Object.keys(stats.attack_distribution),
    datasets: [{ label: 'Detections', data: Object.values(stats.attack_distribution), backgroundColor: '#3b82f6', borderRadius: 6 }]
  } : null

  const chartOptions = { responsive: true, plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } }, scales: { x: { ticks: { color: '#64748b' }, grid: { color: '#1e2d4a' } }, y: { ticks: { color: '#64748b' }, grid: { color: '#1e2d4a' } } } }

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Network security overview and threat analysis</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue">📊</div>
          <div className="stat-info"><div className="stat-value">{stats?.total_traffic?.toLocaleString() || '0'}</div><div className="stat-label">Total Traffic</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon red">⚠️</div>
          <div className="stat-info"><div className="stat-value">{stats?.total_attacks?.toLocaleString() || '0'}</div><div className="stat-label">Attacks Detected</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green">✅</div>
          <div className="stat-info"><div className="stat-value">{stats?.total_benign?.toLocaleString() || '0'}</div><div className="stat-label">Benign Traffic</div></div>
        </div>
        <div className="stat-card">
          <div className="stat-icon yellow">📈</div>
          <div className="stat-info"><div className="stat-value">{stats?.attack_ratio || '0'}%</div><div className="stat-label">Attack Rate</div></div>
        </div>
      </div>

      <div className="charts-grid">
        {pieData && (
          <div className="chart-card">
            <div className="card-title">Threat Distribution</div>
            <Pie data={pieData} options={{ responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 12, font: { size: 11 } } } } }} />
          </div>
        )}
        {barData && (
          <div className="chart-card">
            <div className="card-title">Attack Types Overview</div>
            <Bar data={barData} options={chartOptions} />
          </div>
        )}
      </div>

      {!pieData && !barData && (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <div style={{ fontSize: '40px', marginBottom: '12px', opacity: 0.5 }}>📡</div>
          <p style={{ color: 'var(--text-muted)' }}>No data yet. Upload logs or start monitoring to see analytics.</p>
        </div>
      )}

      {alerts.length > 0 && (
        <div className="card" style={{ marginTop: '20px' }}>
          <div className="card-title">Recent Alerts</div>
          <div className="table-container">
            <table>
              <thead><tr><th>Time</th><th>Attack Type</th><th>Confidence</th><th>Status</th></tr></thead>
              <tbody>
                {alerts.map((a, i) => (
                  <tr key={i}>
                    <td>{new Date(a.timestamp).toLocaleTimeString()}</td>
                    <td style={{ fontWeight: 600 }}>{a.attack_type}</td>
                    <td>{Number(a.confidence).toFixed(1)}%</td>
                    <td><span className="badge danger">⚠ Threat</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
