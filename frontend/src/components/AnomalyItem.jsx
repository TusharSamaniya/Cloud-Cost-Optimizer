import { TrendingUp } from 'lucide-react';

export default function AnomalyItem({ resourceName, date, expected, actual, spikePercent, severity }) {
  const colors = { high: 'bg-red-500', medium: 'bg-amber-500', low: 'bg-blue-500' };
  
  return (
    <div className="relative pl-8 py-4 group">
      {/* Timeline vertical line & dot */}
      <div className="absolute left-0 top-0 bottom-0 w-px bg-border group-last:bg-transparent" />
      <div className={`absolute left-[-4px] top-6 w-2.5 h-2.5 rounded-full ${colors[severity?.toLowerCase()] || 'bg-gray-500'} ring-4 ring-bg-primary`} />
      
      <div className="bg-bg-secondary border border-border p-5 rounded-xl shadow-sm">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h4 className="font-semibold text-text-primary">{resourceName}</h4>
            <span className="text-xs text-text-muted">{new Date(date).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1 text-red-500 bg-red-500/10 px-2 py-1 rounded font-medium text-sm">
            <TrendingUp size={14} />
            {spikePercent}% Spike
          </div>
        </div>
        
        <div className="flex gap-4 mt-4 text-sm">
          <div>
            <p className="text-text-muted text-xs">Expected Cost</p>
            <p className="font-medium text-text-primary">${expected}</p>
          </div>
          <div>
            <p className="text-text-muted text-xs">Actual Cost</p>
            <p className="font-medium text-red-500">${actual}</p>
          </div>
        </div>
      </div>
    </div>
  );
}