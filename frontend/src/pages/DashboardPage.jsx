import { useQuery } from '@tanstack/react-query';
import { DollarSign, AlertTriangle, TrendingDown, Server } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import CostTrendChart from '../components/CostTrendChart';
import LoadingSkeleton from '../components/LoadingSkeleton';
import Button from '../components/ui/Button';
import { getDashboardSummary, getRecommendations } from '../api/resources';

const dummyChartData = Array.from({ length: 30 }).map((_, i) => ({
  date: `Day ${i + 1}`,
  trajectory: 1000 + (i * 50) + Math.random() * 200,
  optimised: 1000 + (i * 10) + Math.random() * 50,
}));

export default function DashboardPage() {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: getDashboardSummary,
  });
  const { data: recs, isLoading: loadingRecs } = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations,
  });

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

  // BUG FIXED: the backend now returns total_spend / wasted_spend /
  // savings_percent / resources_scanned directly (see dashboard.py fix),
  // so these now actually populate instead of always falling back to 0.
  const data = {
    total_spend: summary?.total_spend || 0,
    wasted_spend: summary?.wasted_spend || 0,
    savings_percent: summary?.savings_percent || 0,
    resources_scanned: summary?.resources_scanned || 0,
  };

  const topRecs = Array.isArray(recs) ? recs.slice(0, 3) : [];

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard label="Total Spend" value={`$${data.total_spend.toLocaleString()}`} change="5.2" changeDirection="up" icon={DollarSign} />
        <MetricCard label="Wasted Spend" value={`$${data.wasted_spend.toLocaleString()}`} change="12.4" changeDirection="down" icon={AlertTriangle} />
        <MetricCard label="Potential Savings" value={`${data.savings_percent}%`} change="2.1" changeDirection="up" icon={TrendingDown} />
        <MetricCard label="Resources Scanned" value={data.resources_scanned} icon={Server} />
      </div>

      {data.resources_scanned === 0 && (
        <div className="bg-bg-secondary border border-border rounded-xl p-8 text-center">
          <p className="text-text-primary font-medium mb-2">No data yet</p>
          <p className="text-text-muted text-sm">
            Go to Settings and turn on Demo Mode, or connect your AWS account, then click "Run Scan" above.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-text-primary mb-6">30-Day Cost Projection</h2>
          <CostTrendChart data={summary?.chart_data || dummyChartData} />
        </div>

        <div className="bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
          <h2 className="text-lg font-semibold text-text-primary mb-6">Top Recommendations</h2>
          <div className="space-y-4">
            {topRecs.length > 0 ? topRecs.map((rec) => (
              <div key={rec.id} className="p-4 bg-bg-primary border border-border rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-text-primary truncate pr-4">{rec.title || 'Resource'}</h4>
                  {/* BUG FIXED: was reading rec.estimated_savings, which never
                      existed on the Recommendation model. Correct field is
                      rec.saving_amount (matches the SQLAlchemy model exactly). */}
                  <span className="text-accent font-semibold flex-shrink-0">${(rec.saving_amount || 0).toFixed(0)}/mo</span>
                </div>
                <p className="text-sm text-text-muted mb-4">{rec.description || 'Optimize resource to reduce cost.'}</p>
                <Button className="w-full text-sm py-1.5">Apply</Button>
              </div>
            )) : (
              <p className="text-sm text-text-muted text-center py-4">Run a scan to generate recommendations.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
