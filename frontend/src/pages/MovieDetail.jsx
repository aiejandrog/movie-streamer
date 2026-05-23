import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMovie, getWatchlist, addToWatchlist, removeFromWatchlist, deleteMovie, getStreamUrl, uploadVideoFile } from '../api'
import VideoPlayer from '../components/VideoPlayer'

export default function MovieDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [movie, setMovie] = useState(null)
  const [inWatchlist, setInWatchlist] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileInput = useRef(null)

  useEffect(() => {
    getMovie(id).then(r => setMovie(r.data)).catch(() => navigate('/'))
    getWatchlist().then(r => setInWatchlist(r.data.some(m => m.id === id))).catch(() => {})
  }, [id])

  const toggleWatchlist = async () => {
    if (inWatchlist) {
      await removeFromWatchlist(id)
      setInWatchlist(false)
    } else {
      await addToWatchlist(id)
      setInWatchlist(true)
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Delete "${movie.title}"?`)) return
    await deleteMovie(id)
    navigate('/')
  }

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const res = await uploadVideoFile(id, file)
      setMovie(res.data)
    } catch (err) {
      alert('Upload failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setUploading(false)
    }
  }

  if (!movie) return <div style={{ padding: '60px', textAlign: 'center', color: 'var(--muted)' }}>Loading...</div>

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '32px' }}>
      <button onClick={() => navigate(-1)} style={{ color: 'var(--muted)', marginBottom: '24px', fontSize: '14px' }}>← Back</button>

      <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '32px', marginBottom: '32px' }}>
        {movie.poster_url
          ? <img src={movie.poster_url} alt={movie.title} style={{ width: '100%', borderRadius: 'var(--radius)' }} />
          : <div style={{ background: 'var(--surface2)', borderRadius: 'var(--radius)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '48px', height: '300px' }}>🎬</div>
        }
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px' }}>{movie.title}</h1>
          <div style={{ color: 'var(--muted)', fontSize: '14px', marginBottom: '12px' }}>
            {[movie.year, movie.runtime_minutes ? `${movie.runtime_minutes} min` : null, ...(movie.genres || [])].filter(Boolean).join(' · ')}
          </div>
          {movie.overview && <p style={{ fontSize: '15px', lineHeight: 1.6, color: '#ccc', marginBottom: '24px' }}>{movie.overview}</p>}

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {movie.file_path && (
              <button className="btn btn-primary" onClick={() => setPlaying(true)}>▶ Play</button>
            )}
            {movie.youtube_embed_url && !movie.file_path && (
              <button className="btn btn-primary" onClick={() => setPlaying(true)}>▶ Watch</button>
            )}
            <button className="btn btn-ghost" onClick={toggleWatchlist}>
              {inWatchlist ? '✓ In Watchlist' : '+ Watchlist'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={() => fileInput.current?.click()} disabled={uploading}>
              {uploading ? 'Uploading...' : '⬆ Upload File'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={handleDelete} style={{ color: '#e55' }}>🗑 Delete</button>
            <input ref={fileInput} type="file" accept="video/*" style={{ display: 'none' }} onChange={handleUpload} />
          </div>
        </div>
      </div>

      {playing && movie.file_path && (
        <VideoPlayer movieId={id} src={getStreamUrl(id)} runtimeMinutes={movie.runtime_minutes} />
      )}

      {playing && movie.youtube_embed_url && !movie.file_path && (
        <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, borderRadius: 'var(--radius)', overflow: 'hidden' }}>
          <iframe
            src={movie.youtube_embed_url}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 0 }}
            allowFullScreen
            title={movie.title}
          />
        </div>
      )}
    </div>
  )
}
