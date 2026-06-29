import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getAnomalies } from '../api/resources';
import AnomalyItem from '../components/AnomalyItem';
import FilterBar from '../components/FilterBar';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { CheckCircle } from 'lucide-react';

export default function AnomaliesPage() {
  const [filter, setFilter] = useState('All');

  const { data: anomalies, isLoading } = useQuery({
    queryKey: ['anomalies'],
    queryFn: getAnomalies,
  });

  const filteredAnomalies = (anomalies || []).filter(
    (a) => filter === 'All' || a.severity === filter
  );

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Cost Anomalies
        </h1>
        <p className="text-text-muted mt-1">
          Timeline of unusual spending spikes detected by the ML engine.
        </p>
      </div>

      <FilterBar
        options={['All', 'High', 'Medium', 'Low']}
        activeFilter={filter}
        onFilterChange={setFilter}
      />

      <div className="mt-8 ml-2">
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <LoadingSkeleton
                key={i}
                className="h-40 w-full"
              />
            ))}
          </div>
        ) : filteredAnomalies.length > 0 ? (
          filteredAnomalies.map((anomaly, index) => (
            <AnomalyItem
              key={anomaly.id || index}
              resourceName={anomaly.resource_name}
              date={anomaly.date_detected}
              expected={anomaly.expected_cost}
              actual={anomaly.actual_cost}
              spikePercent={anomaly.spike_percentage}
              severity={anomaly.severity}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="bg-green-500/10 p-4 rounded-full mb-4">
              <CheckCircle
                size={48}
                className="text-green-500"
              />
            </div>

            <h3 className="text-lg font-semibold text-text-primary mb-1">
              All Clear!
            </h3>

            <p className="text-text-muted">
              No unusual spending detected in your resources.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}