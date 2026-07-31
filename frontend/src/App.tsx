import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import SearchPage from './pages/SearchPage'
import CasesPage from './pages/CasesPage'
import SourcesPage from './pages/SourcesPage'
import AnalyticsPage from './pages/AnalyticsPage'
import MapPage from './pages/MapPage'
import PlaceholderPage from './pages/PlaceholderPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="cases" element={<CasesPage />} />
          <Route path="sources" element={<SourcesPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="map" element={<MapPage />} />
          <Route path="graph" element={<PlaceholderPage title="Relationship Graph" description="Interactive entity relationship visualization" />} />
          <Route path="duplicates" element={<PlaceholderPage title="Duplicate Finder" description="Review and merge duplicate articles" />} />
          <Route path="timelines" element={<PlaceholderPage title="Timelines" description="Interactive case timeline explorer" />} />
          <Route path="export" element={<PlaceholderPage title="Export Tools" description="Export research data as JSON, CSV, or PDF" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
