import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Sun, Moon, Play, Loader2 } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { syncResources } from '../api/resources';
import { runPipeline } from '../api/ml';
import toast from 'react-hot-toast';

export default function Topbar() {
  const { theme, toggleTheme } = useTheme();
  const [isScanning, setIsScanning] = useState(false);
  const queryClient = useQueryClient();

  const handleRunScan = async () => {
    setIsScanning(true);
    const toastId = toast.loading('Syncing resources...');
    try {
      // BUG FIXED: "Run Scan" used to call runPipeline() directly, which
      // only re-runs ML on whatever is ALREADY in the database. If the
      // database was empty (first time user, or after toggling demo mode),
      // the pipeline had nothing to cluster/forecast and silently did
      // nothing — which is why the dashboard stayed stuck at $0.
      //
      // Run Scan now does TWO things in order:
      //   1. syncResources() — pulls fresh data (mock or real AWS) into DB
      //   2. runPipeline()   — runs clustering/anomaly/forecast/recs on it
      // (sync already triggers the pipeline internally too, but we call it
      // again here in case the user just wants to re-run ML on existing data)
      await syncResources();
      toast.loading('Running ML pipeline...', { id: toastId });
      await runPipeline();

      toast.success('Optimization scan complete!', { id: toastId });

      // BUG FIXED: previously nothing told React Query the data was stale,
      // so the dashboard kept showing old (or zero) numbers until a manual
      // page refresh. Now every relevant query is invalidated and refetched
      // automatically right after the scan finishes.
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['anomalies'] });
      queryClient.invalidateQueries({ queryKey: ['forecast'] });
    } catch (error) {
      const msg = error.response?.data?.detail || 'Scan failed to complete.';
      toast.error(msg, { id: toastId });
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <header className="h-20 px-8 flex items-center justify-between border-b border-border bg-bg-primary">
      <h2 className="text-xl font-semibold text-text-primary">Dashboard Overview</h2>

      <div className="flex items-center gap-6">
        <div className="text-sm text-text-muted hidden sm:block">
          Last sync: Just now
        </div>

        <button
          onClick={handleRunScan}
          disabled={isScanning}
          className="flex items-center gap-2 bg-accent hover:bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-70"
        >
          {isScanning ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
          {isScanning ? 'Scanning...' : 'Run Scan'}
        </button>

        <button
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-bg-secondary text-text-muted transition-colors"
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </header>
  );
}
