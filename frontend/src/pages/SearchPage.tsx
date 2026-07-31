import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchApi } from '../services/api'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState({ semantic: true, fuzzy: false })

  const { data, isFetching, refetch } = useQuery({
    queryKey: ['search', query],
    queryFn: () => searchApi.search({ query, ...filters, page: 1, page_size: 20 }),
    enabled: false,
  })

  return (
    <div>
      <div className="page-header">
        <h1>Search</h1>
        <p>Semantic, full-text, boolean, and fuzzy search across all indexed content</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search cases, articles, locations..."
            style={{
              flex: 1, padding: '0.75rem', borderRadius: 'var(--radius)',
              border: '1px solid var(--border)', background: 'var(--bg-tertiary)',
              color: 'var(--text-primary)', fontSize: '1rem',
            }}
            onKeyDown={(e) => e.key === 'Enter' && refetch()}
          />
          <button className="btn" onClick={() => refetch()} disabled={isFetching}>
            {isFetching ? 'Searching...' : 'Search'}
          </button>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <label><input type="checkbox" checked={filters.semantic} onChange={(e) => setFilters(f => ({ ...f, semantic: e.target.checked }))} /> Semantic</label>
          <label><input type="checkbox" checked={filters.fuzzy} onChange={(e) => setFilters(f => ({ ...f, fuzzy: e.target.checked }))} /> Fuzzy</label>
        </div>
      </div>

      {data && (
        <div>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            {data.total} results ({data.took_ms}ms)
          </p>
          {data.hits.map((hit: { id: string; title: string; summary?: string; score: number; crime_types: string[]; horror_categories: string[] }) => (
            <div key={hit.id} className="card" style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <h3>{hit.title}</h3>
                <span className="badge">Score: {hit.score.toFixed(2)}</span>
              </div>
              {hit.summary && <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>{hit.summary}</p>}
              <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {hit.crime_types?.map((t: string) => <span key={t} className="badge crime">{t}</span>)}
                {hit.horror_categories?.map((t: string) => <span key={t} className="badge horror">{t}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
