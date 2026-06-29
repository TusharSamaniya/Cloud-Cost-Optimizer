import { CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';

export default function ConnectionStatus({ status, accountId, errorMessage }) {
  if (status === 'connected') {
    return (
      <div className="flex items-center gap-3 text-green-500 bg-green-500/10 px-4 py-4 rounded-xl border border-green-500/20">
        <CheckCircle size={22} />
        <span className="font-medium">Connected to AWS (Account: {accountId})</span>
      </div>
    );
  }
  if (status === 'error') {
    return (
      <div className="flex items-center gap-3 text-red-500 bg-red-500/10 px-4 py-4 rounded-xl border border-red-500/20">
        <AlertCircle size={22} />
        <span className="font-medium">{errorMessage || 'Connection failed'}</span>
      </div>
    );
  }
  return (
    <div className="flex items-center gap-3 text-text-muted bg-bg-primary px-4 py-4 rounded-xl border border-border">
      <HelpCircle size={22} />
      <span className="font-medium">Not connected to AWS</span>
    </div>
  );
}