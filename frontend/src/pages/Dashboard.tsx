import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../services/api'
import StatCard from '../components/dashboard/StatCard'
import TrendingChart from '../components/charts/TrendingChart'
import DiscoveryFeed from '../components/dashboard/DiscoveryFeed'
import CrawlerStatus from '../components/dashboard/CrawlerStatus'

export default function Dashboard() {
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: dashboardApi.stats })
  const { data: trending } = useQuery({ queryKey: ['trending'], queryFn: dashboardApi.trending })
  const { data: discoveries } = useQuery({ queryKey: ['discoveries'], queryFn: dashboardApi.discoveries })
  const { data: crawlers } = useQuery({ queryKey: ['crawler-status'], queryFn: dashboardApi.crawlerStatus, refetchInterval: 30000 })

  return (
    <div>
      <div className="page-header">
        <h1>Research Dashboard</h1>
        <p>Monitor crawlers, discoveries, and trending topics across all sources</p>
      </div>

      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard label="Total Articles" value={stats?.total_articles ?? '—'} />
        <StatCard label="Cases" value={stats?.total_cases ?? '—'} />
        <StatCard label="New This Week" value={stats?.new_this_week ?? '—'} />
        <StatCard label="Processing Queue" value={stats?.pending_processing ?? '—'} />
      </div>

      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Trending Topics</h3>
          <TrendingChart data={trending ?? []} />
        </div>
        <CrawlerStatus crawlers={crawlers ?? []} />
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>New Discoveries</h3>
        <DiscoveryFeed items={discoveries ?? []} />
      </div>
    </div>
  )
}
