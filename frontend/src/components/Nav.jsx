import { Link, useLocation } from 'react-router-dom'

const styles = {
  nav: {
    display: 'flex', alignItems: 'center', gap: '32px',
    padding: '0 32px', height: '60px',
    background: '#111', borderBottom: '1px solid var(--border)',
    position: 'sticky', top: 0, zIndex: 100,
  },
  logo: { fontWeight: 800, fontSize: '20px', color: 'var(--accent)', letterSpacing: '-0.5px' },
  link: { fontSize: '14px', color: 'var(--muted)', fontWeight: 500, transition: 'color 0.15s' },
  active: { color: 'var(--text)' },
}

export default function Nav() {
  const { pathname } = useLocation()
  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.logo}>MovieVault</Link>
      <Link to="/" style={{ ...styles.link, ...(pathname === '/' ? styles.active : {}) }}>Browse</Link>
      <Link to="/watchlist" style={{ ...styles.link, ...(pathname === '/watchlist' ? styles.active : {}) }}>Watchlist</Link>
    </nav>
  )
}
