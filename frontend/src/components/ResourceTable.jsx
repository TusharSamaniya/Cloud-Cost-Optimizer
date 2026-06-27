import { useState, useMemo } from 'react';
import { Search, ChevronDown, ChevronUp } from 'lucide-react';

export default function ResourceTable({ resources = [] }) {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sort, setSort] = useState({ key: 'name', direction: 'asc' });

  // This automatically re-runs only when search, filter, sort, or data changes
  const filteredAndSorted = useMemo(() => {
    let result = resources.filter(r => 
      (r.name?.toLowerCase().includes(search.toLowerCase()) || '') &&
      (statusFilter === 'all' || r.status === statusFilter)
    );

    result.sort((a, b) => {
      let valA = a[sort.key];
      let valB = b[sort.key];
      if (valA < valB) return sort.direction === 'asc' ? -1 : 1;
      if (valA > valB) return sort.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [resources, search, statusFilter, sort]);

  const handleSort = (key) => {
    setSort(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const getStatusColor = (status) => {
    if (status === 'idle') return 'bg-red-500/10 text-red-500 border-red-500/20';
    if (status === 'overprovisioned') return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
    return 'bg-green-500/10 text-green-500 border-green-500/20';
  };

  return (
    <div className="bg-bg-secondary border border-border rounded-xl overflow-hidden shadow-sm">
      <div className="p-4 border-b border-border flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={18} />
          <input 
            type="text" 
            placeholder="Search resources by name..." 
            className="w-full pl-10 pr-4 py-2 bg-bg-primary border border-border rounded-lg text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select 
          className="px-4 py-2 bg-bg-primary border border-border rounded-lg text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">All Statuses</option>
          <option value="healthy">Healthy</option>
          <option value="idle">Idle</option>
          <option value="overprovisioned">Overprovisioned</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-bg-primary/50 text-text-muted text-sm border-b border-border">
              <th className="p-4 font-medium cursor-pointer hover:text-text-primary" onClick={() => handleSort('name')}>
                <div className="flex items-center gap-1">Name {sort.key === 'name' && (sort.direction === 'asc' ? <ChevronUp size={14}/> : <ChevronDown size={14}/>)}</div>
              </th>
              <th className="p-4 font-medium">Type</th>
              <th className="p-4 font-medium">Region</th>
              <th className="p-4 font-medium">CPU %</th>
              <th className="p-4 font-medium cursor-pointer hover:text-text-primary" onClick={() => handleSort('monthly_cost')}>
                <div className="flex items-center gap-1">Cost/Mo {sort.key === 'monthly_cost' && (sort.direction === 'asc' ? <ChevronUp size={14}/> : <ChevronDown size={14}/>)}</div>
              </th>
              <th className="p-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSorted.map((res, i) => (
              <tr key={i} className="border-b border-border/50 hover:bg-bg-primary/30 text-sm text-text-primary transition-colors">
                <td className="p-4 font-medium">{res.name}</td>
                <td className="p-4 text-text-muted">{res.type}</td>
                <td className="p-4 text-text-muted">{res.region}</td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <span className="w-8 text-right">{res.cpu_percent || 0}%</span>
                    <div className="flex-1 h-2 bg-bg-primary rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${res.cpu_percent > 80 ? 'bg-red-500' : res.cpu_percent < 20 ? 'bg-amber-500' : 'bg-green-500'}`} 
                        style={{ width: `${Math.max(0, Math.min(100, res.cpu_percent || 0))}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="p-4">${(res.monthly_cost || 0).toFixed(2)}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 text-xs rounded-full border ${getStatusColor(res.status)} capitalize font-medium`}>
                    {res.status}
                  </span>
                </td>
              </tr>
            ))}
            {filteredAndSorted.length === 0 && (
              <tr><td colSpan="6" className="p-8 text-center text-text-muted">No matching resources found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}