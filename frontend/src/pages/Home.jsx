import { useState, useEffect } from 'react'
import { getMovies, getContinuing } from '../api'
import MovieCard from '../components/MovieCard'
import SearchBar from '../components/SearchBar'
import AddMovieModal from '../components/AddMovieModal'

const grid = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
  gap: '16px',
}

export default function Home() {
  const [movies, setMovies] = useState([])
  const [continuing, setContinuing] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [genre, setGenre] = useState('')

  const load = async (q = '', g = genre) => {
    setLoading(true)
    try {
      const [movRes, contRes] = await Promise.all([
        getMovies({ q: q || undefined, genre: g || undefined }),
        getContinuing(),
      ])
      setMovies(movRes.data)
      setContinuing(contRes.data)
    } catch {
      setMovies([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const genres = [...new Set(movies.flatMap(m => m.genres || []))].sort()

  return (
    <div style={{ padding: '32px', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px', flexWrap: 'wrap' }}>
        <SearchBar onSearch={q => load(q)} />
        <select
          value={genre}
          onChange={e => { setGenre(e.target.value); load('', e.target.value) }}
          style={{ width: 'auto' }}
        >
          <option value="">All Genres</option>
          {genres.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>+ Add Movie</button>
      </div>

      {continuing.length > 0 && (
        <section style={{ marginBottom: '36px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px', color: 'var(--muted)' }}>CONTINUE WATCHING</h2>
          <div style={grid}>
            {continuing.map(m => <MovieCard key={m.id} movie={m} />)}
          </div>
        </section>
      )}

      <section>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px', color: 'var(--muted)' }}>
          {movies.length === 0 && !loading ? 'NO MOVIES YET' : `ALL MOVIES (${movies.length})`}
        </h2>
        {loading
          ? <div style={{ color: 'var(--muted)', textAlign: 'center', padding: '60px' }}>Loading...</div>
          : <div style={grid}>{movies.map(m => <MovieCard key={m.id} movie={m} />)}</div>
        }
      </section>

      {showModal && (
        <AddMovieModal
          onClose={() => setShowModal(false)}
          onAdded={() => load()}
        />
      )}
    </div>
  )
}
