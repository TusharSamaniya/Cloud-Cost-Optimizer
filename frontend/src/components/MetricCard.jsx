import { ArrowDownRight, ArrowUpRight } from 'lucide-react';

export default function MetricCard({ label, value, change, changeDirection, icon: Icon }) {
  // If costs go down, that's good (green). If costs go up, that's bad (red).
  const isGood = changeDirection === 'down' || label.includes('Savings');
  const colorClass = isGood ? 'text-green-500' : 'text-red-500';

  return (
    <div className="bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-text-muted font-medium">{label}</p>
          <h3 className="text-2xl font-bold text-text-primary mt-2">{value}</h3>
        </div>
        {Icon && (
          <div className="p-3 bg-bg-primary rounded-lg text-accent">
            <Icon size={24} />
          </div>
        )}
      </div>
      
      {change && (
        <div className={`flex items-center mt-4 text-sm font-medium ${colorClass}`}>
          {changeDirection === 'up' ? <ArrowUpRight size={16} className="mr-1" /> : <ArrowDownRight size={16} className="mr-1" />}
          <span>{change}% from last month</span>
        </div>
      )}
    </div>
  );
}