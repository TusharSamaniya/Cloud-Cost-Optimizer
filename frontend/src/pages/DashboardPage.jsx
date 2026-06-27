import { useQuery } from '@tanstack/react-query';
import { DollarSign, AlertTriangle, TrendingDown, Server } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import CostTrendChart from '../components/CostTrendChart';
import LoadingSkeleton from '../components/LoadingSkeleton';
import Button from '../components/ui/Button';
import { getDashboardSummary, getRecommendations } from '../api/resources';

// Fallback data so the chart doesn't crash if the database is brand new
const dummyChartData = Array.from({ length: 30 }).map((_, i) => ({
  date: `Day ${i + 1}`,
  trajectory: 1000 + (i * 50) + Math.random() * 200,
  optimised: 1000 + (i * 10) + Math.random() * 50,
}));

export default function DashboardPage() {
  const { data: summary, isLoading: loadingSummary } = useQuery({ queryKey: ['dashboardSummary'], queryFn: getDashboardSummary });
  const { data: recs, isLoading: loadingRecs } = useQuery({ queryKey: ['recommendations'], queryFn: getRecommendations });

  if (loadingSummary || loadingRecs) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => <LoadingSkeleton key={i} className="h-32" />)}
        </div>
        <LoadingSkeleton className="h-96" />
      </div>
    );
  }

  const data = summary || { total_spend: 0, wasted_spend: 0, savings_percent: 0, resources_scanned: 0 };
  const topRecs = Array.isArray(recs) ? recs.slice(0, 3) : [];

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard label="Total Spend" value={`$${data.total_spend.toLocaleString()}`} change="5.2" changeDirection="up" icon={DollarSign} />
        <MetricCard label="Wasted Spend" value={`$${data.wasted_spend.toLocaleString()}`} change="12.4" changeDirection="down" icon={AlertTriangle} />
        <MetricCard label="Potential Savings" value={`${data.savings_percent}%`} change="2.1" changeDirection="up" icon={TrendingDown} />
        <MetricCard label="Resources Scanned" value={data.resources_scanned} icon={Server} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-text-primary mb-6">30-Day Cost Projection</h2>
          <CostTrendChart data={summary?.chart_data || dummyChartData} />
        </div>

        <div className="bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-text-primary mb-6">Top Recommendations</h2>
          <div className="space-y-4">
            {topRecs.length > 0 ? topRecs.map((rec, i) => (
              <div key={i} className="p-4 bg-bg-primary border border-border rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-text-primary truncate pr-4">{rec.resource_name || 'Instance'}</h4>
                  <span className="text-accent font-semibold flex-shrink-0">${rec.estimated_savings}/mo</span>
                </div>
                <p className="text-sm text-text-muted mb-4">{rec.recommendation_type || 'Optimize resource to reduce cost.'}</p>
                <Button className="w-full text-sm py-1.5">Apply</Button>
              </div>
            )) : (
              <p className="text-sm text-text-muted text-center py-4">Run an ML scan to generate recommendations.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}