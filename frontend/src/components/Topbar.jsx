import { useState } from 'react';
import { Sun, Moon, Play, Loader2 } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { runPipeline } from '../api/ml';
import toast from 'react-hot-toast';

export default function Topbar() {
  const { theme, toggleTheme } = useTheme();
  const [isScanning, setIsScanning] = useState(false);

  const handleRunScan = async () => {
    setIsScanning(true);
    const toastId = toast.loading('Running ML Pipeline...');
    try {
      await runPipeline();
      toast.success('Optimization scan complete!', { id: toastId });
      // In a full app, you would trigger a refetch of React Query data here
    } catch (error) {
      toast.error('Scan failed to complete.', { id: toastId });
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