import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getRecommendations, updateRecommendation } from '../api/resources';
import RecommendationCard from '../components/RecommendationCard';
import FilterBar from '../components/FilterBar';
import LoadingSkeleton from '../components/LoadingSkeleton';
import toast from 'react-hot-toast';

export default function RecommendationsPage() {
  const [filter, setFilter] = useState('All');
  const queryClient = useQueryClient();

  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations,
  });

  // Optimistic Update Mutation
  const mutation = useMutation({
    mutationFn: ({ id, status }) => updateRecommendation(id, status),

    onMutate: async ({ id, status }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['recommendations'] });

      // Snapshot the previous value
      const previousRecs = queryClient.getQueryData(['recommendations']);

      // Optimistically update the cache
      queryClient.setQueryData(['recommendations'], (old) =>
        old?.map((rec) =>
          rec.id === id ? { ...rec, status } : rec
        )
      );

      return { previousRecs };
    },

    onError: (err, newRec, context) => {
      // Rollback on failure
      queryClient.setQueryData(
        ['recommendations'],
        context?.previousRecs
      );
      toast.error('Failed to update recommendation.');
    },

    onSettled: () => {
      // Refresh dashboard summary
      queryClient.invalidateQueries({
        queryKey: ['dashboardSummary'],
      });
    },
  });

  const handleAction = (id, status) => {
    mutation.mutate({ id, status });

    if (status === 'applied') {
      toast.success('Recommendation applied successfully!');
    }
  };

  const filteredRecs = useMemo(() => {
    if (!recommendations) return [];

    return recommendations.filter(
      (rec) => filter === 'All' || rec.priority === filter
    );
  }, [recommendations, filter]);

  // Calculate total pending savings
  const totalPendingSavings = (recommendations || [])
    .filter((r) => r.status === 'pending')
    .reduce(
      (sum, r) => sum + (r.saving_amount || 0),
      0
    );

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">
            Optimization Recommendations
          </h1>
          <p className="text-text-muted mt-1">
            Review and apply AI-generated strategies to reduce your cloud spend.
          </p>
        </div>

        <div className="bg-accent/10 border border-accent/20 px-6 py-3 rounded-xl text-right">
          <p className="text-sm text-accent font-medium uppercase tracking-wider">
            Potential Savings
          </p>
          <p className="text-3xl font-bold text-accent transition-all duration-700 ease-in-out">
            ${totalPendingSavings.toLocaleString()}/mo
          </p>
        </div>
      </div>

      <FilterBar
        options={['All', 'High', 'Medium', 'Low']}
        activeFilter={filter}
        onFilterChange={setFilter}
      />

      <div className="space-y-4 mt-6">
        {isLoading ? (
          [...Array(5)].map((_, i) => (
            <LoadingSkeleton
              key={i}
              className="h-32 w-full"
            />
          ))
        ) : filteredRecs.length > 0 ? (
          filteredRecs.map((rec) => (
            <RecommendationCard
              key={rec.id}
              {...rec}
              savingAmount={rec.saving_amount}
              onAction={handleAction}
            />
          ))
        ) : (
          <div className="text-center py-12 bg-bg-secondary rounded-xl border border-border">
            <p className="text-text-muted">
              No recommendations found for this filter.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}