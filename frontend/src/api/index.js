import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getMovies = (params) => api.get('/movies', { params })
export const getMovie = (id) => api.get(`/movies/${id}`)
export const deleteMovie = (id) => api.delete(`/movies/${id}`)
export const getContinuing = () => api.get('/movies/continuing')

export const searchTMDB = (q) => api.get('/ingest/tmdb/search', { params: { q } })
export const importFromTMDB = (tmdbId) => api.post(`/ingest/tmdb/${tmdbId}`)
export const uploadVideoFile = (movieId, file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/ingest/file/${movieId}`, form)
}
export const addManual = (title, year, youtubeUrl) =>
  api.post('/ingest/manual', null, { params: { title, year, youtube_embed_url: youtubeUrl } })

export const getWatchlist = () => api.get('/watchlist')
export const addToWatchlist = (movieId) => api.post(`/watchlist/${movieId}`)
export const removeFromWatchlist = (movieId) => api.delete(`/watchlist/${movieId}`)

export const getProgress = (movieId) => api.get(`/progress/${movieId}`)
export const saveProgress = (movieId, positionSeconds, completed = false) =>
  api.post(`/progress/${movieId}`, { position_seconds: positionSeconds, completed })

export const getStreamUrl = (movieId) => `/api/stream/${movieId}`
