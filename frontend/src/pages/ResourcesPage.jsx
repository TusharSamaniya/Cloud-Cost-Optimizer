import { useQuery } from '@tanstack/react-query';
import { getResources } from '../api/resources';
import ResourceTable from '../components/ResourceTable';
import LoadingSkeleton from '../components/LoadingSkeleton';

export default function ResourcesPage() {
  const { data: resources, isLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: getResources,
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Cloud Resources</h1>
        <p className="text-text-muted mt-1">Manage, filter, and monitor all your scanned AWS resources.</p>
      </div>

      {isLoading ? (
        <LoadingSkeleton className="h-[500px] w-full" />
      ) : (
        <ResourceTable resources={Array.isArray(resources) ? resources : []} />
      )}
    </div>
  );
}