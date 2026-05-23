import { useState } from 'react'
import { searchTMDB, importFromTMDB, addManual } from '../api'

const overlay = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200,
}
const modal = {
  background: 'var(--surface)', borderRadius: 'var(--radius)', padding: '28px',
  width: '500px', maxWidth: '95vw', maxHeight: '80vh', overflowY: 'auto',
}

export default function AddMovieModal({ onClose, onAdded }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [manualTitle, setManualTitle] = useState('')
  const [tab, setTab] = useState('tmdb')

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await searchTMDB(query)
      setResults(res.data)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleImport = async (tmdbId) => {
    try {
      await importFromTMDB(tmdbId)
      onAdded()
      onClose()
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to import')
    }
  }

  const handleManual = async () => {
    if (!manualTitle.trim()) return
    await addManual(manualTitle)
    onAdded()
    onClose()
  }

  return (
    <div style={overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={modal}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700 }}>Add Movie</h2>
          <button onClick={onClose} style={{ fontSize: '20px', color: 'var(--muted)' }}>×</button>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button className={`btn btn-sm ${tab === 'tmdb' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab('tmdb')}>TMDB Search</button>
          <button className={`btn btn-sm ${tab === 'manual' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab('manual')}>Manual</button>
        </div>

        {tab === 'tmdb' && (
          <>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
              <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search TMDB..." onKeyDown={e => e.key === 'Enter' && search()} />
              <button className="btn btn-primary btn-sm" onClick={search} disabled={loading}>
                {loading ? '...' : 'Search'}
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {results.map(r => (
                <div key={r.tmdb_id} style={{ display: 'flex', gap: '12px', alignItems: 'center', padding: '10px', background: 'var(--surface2)', borderRadius: 'var(--radius)' }}>
                  {r.poster_url && <img src={r.poster_url} alt="" style={{ width: '40px', height: '60px', objectFit: 'cover', borderRadius: '4px' }} />}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '14px' }}>{r.title}</div>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{r.year}</div>
                  </div>
                  <button className="btn btn-primary btn-sm" onClick={() => handleImport(r.tmdb_id)}>Add</button>
                </div>
              ))}
            </div>
          </>
        )}

        {tab === 'manual' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <input value={manualTitle} onChange={e => setManualTitle(e.target.value)} placeholder="Movie title" />
            <button className="btn btn-primary" onClick={handleManual} disabled={!manualTitle.trim()}>Add Movie</button>
          </div>
        )}
      </div>
    </div>
  )
}
