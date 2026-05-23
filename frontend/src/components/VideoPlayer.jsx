import { useRef, useEffect } from 'react'
import { saveProgress, getProgress } from '../api'

export default function VideoPlayer({ movieId, src, runtimeMinutes }) {
  const ref = useRef(null)
  const saveTimer = useRef(null)

  useEffect(() => {
    const video = ref.current
    if (!video) return

    getProgress(movieId).then(res => {
      if (res.data?.position_seconds > 10) {
        video.currentTime = res.data.position_seconds
      }
    }).catch(() => {})

    const handleTimeUpdate = () => {
      clearTimeout(saveTimer.current)
      saveTimer.current = setTimeout(() => {
        const pos = Math.floor(video.currentTime)
        const duration = video.duration || (runtimeMinutes ? runtimeMinutes * 60 : 0)
        const completed = duration > 0 && pos / duration > 0.9
        saveProgress(movieId, pos, completed).catch(() => {})
      }, 5000)
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      clearTimeout(saveTimer.current)
    }
  }, [movieId, runtimeMinutes])

  return (
    <video
      ref={ref}
      src={src}
      controls
      style={{ width: '100%', borderRadius: 'var(--radius)', background: '#000', maxHeight: '70vh' }}
    />
  )
}
