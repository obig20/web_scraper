import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

export const dashboardApi = {
  stats: () => api.get('/dashboard/stats').then(r => r.data),
  trending: () => api.get('/dashboard/trending').then(r => r.data),
  discoveries: () => api.get('/dashboard/discoveries').then(r => r.data),
  crawlerStatus: () => api.get('/dashboard/crawler-status').then(r => r.data),
}

export const searchApi = {
  search: (query: Record<string, unknown>) => api.post('/search', query).then(r => r.data),
}

export const articlesApi = {
  list: (page = 1) => api.get('/articles', { params: { page } }).then(r => r.data),
  get: (id: string) => api.get(`/articles/${id}`).then(r => r.data),
}

export const casesApi = {
  list: (page = 1) => api.get('/cases', { params: { page } }).then(r => r.data),
}

export const sourcesApi = {
  list: () => api.get('/sources').then(r => r.data),
  crawl: (id: string) => api.post(`/sources/${id}/crawl`).then(r => r.data),
}
