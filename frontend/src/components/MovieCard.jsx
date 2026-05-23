import { Link } from 'react-router-dom'

const styles = {
  card: {
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    background: 'var(--surface)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
  },
  poster: { width: '100%', aspectRatio: '2/3', objectFit: 'cover', background: 'var(--surface2)' },
  placeholder: {
    width: '100%', aspectRatio: '2/3', background: 'var(--surface2)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '40px',
  },
  info: { padding: '10px 12px' },
  title: { fontWeight: 600, fontSize: '13px', lineHeight: 1.3, marginBottom: '4px' },
  meta: { fontSize: '12px', color: 'var(--muted)' },
}

export default function MovieCard({ movie }) {
  return (
    <Link to={`/movie/${movie.id}`}>
      <div
        style={styles.card}
        onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.03)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.5)' }}
        onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = 'none' }}
      >
        {movie.poster_url
          ? <img src={movie.poster_url} alt={movie.title} style={styles.poster} loading="lazy" />
          : <div style={styles.placeholder}>🎬</div>
        }
        <div style={styles.info}>
          <div style={styles.title}>{movie.title}</div>
          <div style={styles.meta}>{movie.year} {movie.genres?.slice(0, 2).join(' · ')}</div>
        </div>
      </div>
    </Link>
  )
}
