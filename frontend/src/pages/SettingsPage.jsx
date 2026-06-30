import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import AWSConnectCard from '../components/AWSConnectCard';
import ConnectionStatus from '../components/ConnectionStatus';
import Button from '../components/ui/Button';
import toast from 'react-hot-toast';
import client from '../api/client';
import { syncResources } from '../api/resources';

// BUG FIXED: previously isDemoMode lived only in local useState, starting at
// false every time the page mounted — so it always looked "off by default"
// even when the backend's USE_MOCK_DATA was actually true. Now we fetch the
// real value from the backend on load and write back to it on toggle.

export default function SettingsPage() {
  const [connStatus, setConnStatus] = useState('disconnected');
  const [accountId, setAccountId] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const queryClient = useQueryClient();

  // Fetch current credential status on mount — fixes connection status
  // always showing "disconnected" even after a successful save
  const { data: credStatus } = useQuery({
    queryKey: ['awsCredentialStatus'],
    queryFn: async () => (await client.get('/api/aws/credentials/status')).data,
  });

  useEffect(() => {
    if (credStatus?.has_credentials) {
      setConnStatus('connected');
    }
  }, [credStatus]);

  // Fetch REAL demo mode state from backend instead of defaulting to false
  const { data: demoModeData } = useQuery({
    queryKey: ['demoMode'],
    queryFn: async () => (await client.get('/api/settings/demo-mode')).data,
  });

  const demoModeMutation = useMutation({
    mutationFn: async (enabled) =>
      (await client.post('/api/settings/demo-mode', { enabled })).data,
    onSuccess: (data) => {
      queryClient.setQueryData(['demoMode'], data);
      toast.success(`Demo mode ${data.enabled ? 'enabled' : 'disabled'}`);
    },
    onError: () => toast.error('Failed to update demo mode'),
  });

  const handleSuccess = (id) => {
    setConnStatus('connected');
    setAccountId(id);
    setErrorMsg('');
    queryClient.invalidateQueries({ queryKey: ['awsCredentialStatus'] });
  };

  const handleError = (msg) => {
    setConnStatus('error');
    setErrorMsg(msg);
  };

  const handleRunFirstScan = async () => {
    const toastId = toast.loading('Running first scan...');
    try {
      await syncResources();
      toast.success('Scan complete! Check your dashboard.', { id: toastId });
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardSummary'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    } catch (err) {
      const msg = err.response?.data?.detail || 'Scan failed. Please try again.';
      toast.error(msg, { id: toastId });
    }
  };

  const isDemoMode = demoModeData?.enabled ?? false;

  return (
    <div className="space-y-8 animate-fade-in max-w-3xl mx-auto pb-12">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Platform Settings</h1>
        <p className="text-text-muted mt-1">Manage your account integrations and application preferences.</p>
      </div>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold text-text-primary border-b border-border pb-2">AWS Integration</h2>
        <ConnectionStatus status={connStatus} accountId={accountId} errorMessage={errorMsg} />
        <AWSConnectCard onConnectionSuccess={handleSuccess} onConnectionError={handleError} />

        {connStatus === 'connected' && (
          <Button onClick={handleRunFirstScan} className="w-full py-4 text-lg animate-fade-in shadow-lg shadow-accent/20">
            Run Initial Deep Scan
          </Button>
        )}
      </section>

      <section className="space-y-6 pt-6">
        <h2 className="text-xl font-semibold text-text-primary border-b border-border pb-2">Developer Tools</h2>
        <div className="bg-bg-secondary border border-border p-6 rounded-xl flex justify-between items-center">
          <div>
            <h3 className="font-medium text-text-primary">Demo Mode</h3>
            <p className="text-sm text-text-muted mt-1">
              Use mock data (no real AWS account needed). Toggle on, then go to Dashboard and click "Run Scan".
            </p>
          </div>
          <button
            onClick={() => demoModeMutation.mutate(!isDemoMode)}
            disabled={demoModeMutation.isPending}
            className={`w-14 h-7 rounded-full transition-colors relative shrink-0 ${isDemoMode ? 'bg-accent' : 'bg-gray-600'}`}
          >
            <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-transform ${isDemoMode ? 'translate-x-8' : 'translate-x-1'}`} />
          </button>
        </div>
      </section>
    </div>
  );
}
