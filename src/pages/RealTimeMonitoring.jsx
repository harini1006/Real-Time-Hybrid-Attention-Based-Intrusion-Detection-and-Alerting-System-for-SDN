import { useState, useRef, useEffect } from 'react'

const WS_URL = 'ws://localhost:8000/api/ws/realtime'

export default function RealTimeMonitoring({ token }) {
  const [file, setFile] = useState(null)
  const [monitoring, setMonitoring] = useState(false)
  const [feed, setFeed] = useState([])
  const [stats, setStats] = useState({ total: 0, attacks: 0, benign: 0 })
  const wsRef = useRef(null)
  const fileRef = useRef()

  const startMonitoring = async () => {
    if (!file) return
    const text = await file.text()
    setFeed([]); setStats({ total: 0, attacks: 0, benign: 0 }); setMonitoring(true)

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => ws.send(JSON.stringify({ type: 'start', csv_data: text }))
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.type === 'complete' || data.type === 'stopped') { setMonitoring(false); return }
      if (data.error) { setMonitoring(false); return }
      setFeed(prev => [data, ...prev].slice(0, 200))
      setStats(prev => ({
        total: prev.total + 1,
        attacks: prev.attacks + (data.is_attack ? 1 : 0),
        benign: prev.benign + (data.is_attack ? 0 : 1),
      }))
    }
    ws.onclose = () => setMonitoring(false)
  }

  const stopMonitoring = () => {
    if (wsRef.current) { wsRef.current.send(JSON.stringify({ type: 'stop' })); wsRef.current.close() }
    setMonitoring(false)
  }

  useEffect(() => () => { if (wsRef.current) wsRef.current.close() }, [])

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Real-Time Monitor</h1>
        <p className="page-subtitle">Stream network traffic for live threat detection</p>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="monitoring-controls">
          <input type="file" ref={fileRef} accept=".csv" onChange={e => setFile(e.target.files?.[0])} style={{ display: 'none' }} />
          <button className="btn btn-outline" onClick={() => fileRef.current?.click()}>
            {file ? `📄 ${file.name}` : '📁 Select CSV'}
          </button>
          {!monitoring ? (
            <button className="btn btn-green" onClick={startMonitoring} disabled={!file}>▶ Start Monitoring</button>
          ) : (
            <button className="btn btn-red" onClick={stopMonitoring}>⏹ Stop</button>
          )}
          {monitoring && <span className="badge info pulse">● LIVE</span>}
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card"><div className="stat-icon blue">📊</div><div className="stat-info"><div className="stat-value">{stats.total}</div><div className="stat-label">Processed</div></div></div>
        <div className="stat-card"><div className="stat-icon red">🚨</div><div className="stat-info"><div className="stat-value">{stats.attacks}</div><div className="stat-label">Threats</div></div></div>
        <div className="stat-card"><div className="stat-icon green">✅</div><div className="stat-info"><div className="stat-value">{stats.benign}</div><div className="stat-label">Safe</div></div></div>
        <div className="stat-card"><div className="stat-icon yellow">📈</div><div className="stat-info"><div className="stat-value">{stats.total > 0 ? (stats.attacks / stats.total * 100).toFixed(1) : '0'}%</div><div className="stat-label">Threat Rate</div></div></div>
      </div>

      <div className="card">
        <div className="card-title">Live Feed</div>
        {feed.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px', opacity: 0.5 }}>📡</div>
            <p>Start monitoring to see live results</p>
          </div>
        ) : (
          <div className="live-feed">
            {feed.map((item, i) => (
              <div key={i} className={`feed-item ${item.is_attack ? 'attack' : ''}`}>
                <div>
                  <span style={{ fontWeight: 600 }}>{item.is_attack ? `🚨 ${item.attack_type}` : '✅ Benign'}</span>
                  <span style={{ color: 'var(--text-muted)', marginLeft: '12px', fontSize: '12px' }}>Row #{item.row_index}</span>
                </div>
                <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{Number(item.confidence).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
