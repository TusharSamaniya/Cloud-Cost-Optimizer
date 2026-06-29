import { useState } from 'react';
import AWSConnectCard from '../components/AWSConnectCard';
import ConnectionStatus from '../components/ConnectionStatus';
import Button from '../components/ui/Button';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const [connStatus, setConnStatus] = useState('disconnected');
  const [accountId, setAccountId] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isDemoMode, setIsDemoMode] = useState(false);

  const handleSuccess = (id) => {
    setConnStatus('connected');
    setAccountId(id);
    setErrorMsg('');
  };

  const handleError = (msg) => {
    setConnStatus('error');
    setErrorMsg(msg);
  };

  const toggleDemoMode = () => {
    setIsDemoMode(!isDemoMode);
    toast.success(`Demo mode ${!isDemoMode ? 'enabled' : 'disabled'}`);
    // Optional: Call your backend to flip the USE_MOCK_DATA environment variable
  };

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
          <Button className="w-full py-4 text-lg animate-fade-in shadow-lg shadow-accent/20">
            Run Initial Deep Scan
          </Button>
        )}
      </section>

      <section className="space-y-6 pt-6">
        <h2 className="text-xl font-semibold text-text-primary border-b border-border pb-2">Developer Tools</h2>
        <div className="bg-bg-secondary border border-border p-6 rounded-xl flex justify-between items-center">
          <div>
            <h3 className="font-medium text-text-primary">Demo Mode</h3>
            <p className="text-sm text-text-muted mt-1">Use mock data (No real AWS account needed).</p>
          </div>
          <button 
            onClick={toggleDemoMode}
            className={`w-14 h-7 rounded-full transition-colors relative ${isDemoMode ? 'bg-accent' : 'bg-gray-600'}`}
          >
            <div className={`w-5 h-5 bg-white rounded-full absolute top-1 transition-transform ${isDemoMode ? 'translate-x-8' : 'translate-x-1'}`} />
          </button>
        </div>
      </section>
    </div>
  );
}