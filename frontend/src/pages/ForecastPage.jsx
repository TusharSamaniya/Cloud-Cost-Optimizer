import { TrendingDown, TrendingUp, DollarSign } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ForecastChart from '../components/ForecastChart';

export default function ForecastPage() {
  // Generate mock trajectory data bridging past data into future predictions
  const forecastData = Array.from({ length: 30 }).map((_, i) => {
    const baseCost = 1500 + (i * 25);
    return {
      date: i === 15 ? 'Today' : `Day ${i + 1}`,
      predicted_cost: baseCost,
      confidence_bounds: i >= 15 ? [baseCost - 150, baseCost + 200] : [baseCost, baseCost]
    };
  });

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Spend Forecast</h1>
        <p className="text-text-muted mt-1">AI-driven cost projections with 95% confidence intervals.</p>
      </div>

      <div className="bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
        <ForecastChart data={forecastData} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        <MetricCard label="Predicted Next 30 Days" value="$48,250" change="3.1" changeDirection="up" icon={DollarSign} />
        <MetricCard label="Projected Savings Available" value="$5,120" change="14.0" changeDirection="down" icon={TrendingDown} />
        <MetricCard label="Cost Trend Trajectory" value="Rising" change="2.5" changeDirection="up" icon={TrendingUp} />
      </div>
    </div>
  );
}