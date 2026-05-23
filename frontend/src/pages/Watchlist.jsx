import { useState, useEffect } from 'react'
import { getWatchlist } from '../api'
import MovieCard from '../components/MovieCard'

export default function Watchlist() {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getWatchlist()
      .then(r => setMovies(r.data))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div style={{ padding: '32px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '28px' }}>Watchlist</h1>
      {loading && <div style={{ color: 'var(--muted)' }}>Loading...</div>}
      {!loading && movies.length === 0 && (
        <div style={{ color: 'var(--muted)', textAlign: 'center', padding: '60px' }}>
          No movies saved yet. Browse and add movies to your watchlist.
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '16px' }}>
        {movies.map(m => <MovieCard key={m.id} movie={m} />)}
      </div>
    </div>
  )
}
