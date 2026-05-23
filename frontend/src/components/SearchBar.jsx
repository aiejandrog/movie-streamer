import { useState, useEffect, useRef } from 'react'

export default function SearchBar({ onSearch, placeholder = 'Search movies...' }) {
  const [value, setValue] = useState('')
  const timer = useRef(null)

  useEffect(() => {
    clearTimeout(timer.current)
    timer.current = setTimeout(() => onSearch(value), 350)
    return () => clearTimeout(timer.current)
  }, [value])

  return (
    <input
      type="text"
      value={value}
      onChange={e => setValue(e.target.value)}
      placeholder={placeholder}
      style={{ maxWidth: '400px' }}
    />
  )
}
