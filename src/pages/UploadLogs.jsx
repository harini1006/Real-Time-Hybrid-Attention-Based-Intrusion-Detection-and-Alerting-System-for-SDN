import { useState, useRef } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000/api'

export default function UploadLogs({ token }) {
  const [file, setFile] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()
  const perPage = 20

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError('')
    setResults(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post(`${API}/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      })
      setResults(res.data)
      setPage(1)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0])
  }

  const preds = results?.predictions || []
  const totalPages = Math.ceil(preds.length / perPage)
  const paginated = preds.slice((page - 1) * perPage, page * perPage)

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Upload Logs</h1>
        <p className="page-subtitle">Upload CSV network log files for batch analysis</p>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <div
          className={`upload-zone ${dragOver ? 'dragover' : ''}`}
          onDragOver={(e) => {
            e.preventDefault()
            setDragOver(true)
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
        >
          <input
            type="file"
            ref={fileRef}
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ display: 'none' }}
          />
          <div className="upload-icon">📁</div>
          <div className="upload-text">
            {file ? `📄 ${file.name}` : 'Drop CSV file here or click to browse'}
          </div>
          <div className="upload-hint">
            {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : 'Supports CSV network log files'}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
          <button className="btn btn-blue" onClick={handleUpload} disabled={!file || loading}>
            {loading ? '⏳ Analyzing...' : '🔍 Analyze'}
          </button>
          {results && (
            <a
              href={`${API}/predictions/download`}
              className="btn btn-outline"
              style={{ textDecoration: 'none' }}
            >
              📥 Download CSV
            </a>
          )}
        </div>
      </div>

      {error && <div className="auth-error">{error}</div>}

      {results && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon blue">📄</div>
              <div className="stat-info">
                <div className="stat-value">{results.total_rows?.toLocaleString()}</div>
                <div className="stat-label">Total Rows</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon green">✅</div>
              <div className="stat-info">
                <div className="stat-value">{results.benign_count?.toLocaleString()}</div>
                <div className="stat-label">Benign</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon red">🚨</div>
              <div className="stat-info">
                <div className="stat-value">{results.attacks_found?.toLocaleString()}</div>
                <div className="stat-label">Attacks Found</div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-title">Analysis Results</div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Prediction</th>
                    <th>Type</th>
                    <th>Confidence</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((p, i) => (
                    <tr key={i}>
                      <td>{p.id}</td>
                      <td>{p.predicted_label}</td>
                      <td style={{ fontWeight: 500 }}>{p.attack_type || '-'}</td>
                      <td>{Number(p.confidence).toFixed(1)}%</td>
                      <td>
                        <span className={`badge ${p.is_attack ? 'danger' : 'success'}`}>
                          {p.is_attack ? '⚠ Threat' : '✅ Safe'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="page-btn"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
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
          </div>
        </>
      )}
    </div>
  )
}
