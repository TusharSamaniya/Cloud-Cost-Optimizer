import { useState } from 'react';
import { Lock } from 'lucide-react';
import Input from './ui/Input';
import Button from './ui/Button';
import toast from 'react-hot-toast';
import client from '../api/client';

export default function AWSConnectCard({ onConnectionSuccess, onConnectionError }) {
  const [accessKey, setAccessKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleTestConnection = async (e) => {
    e.preventDefault();
    if (!accessKey || !secretKey) return toast.error('Please provide both keys.');

    setIsLoading(true);
    try {
      // Step 1 — save (backend now validates against AWS STS before saving)
      const saveResponse = await client.post('/api/aws/credentials', {
        access_key: accessKey,
        secret_key: secretKey,
      });

      toast.success('AWS Connection successful!');
      // BUG FIXED: account ID was hardcoded as 'AWS-9382-7481' before.
      // The backend now actually returns the real AWS account_id from STS.
      onConnectionSuccess(saveResponse.data.account_id || 'Connected');
    } catch (error) {
      // BUG FIXED: previously this called '/api/sync/aws' which does not
      // exist on the backend (correct route is '/api/sync/'), so the
      // validation step ALWAYS failed with a 404 — even with perfectly
      // valid AWS keys. That extra unnecessary call has been removed
      // entirely because /api/aws/credentials now validates internally.
      //
      // We now read the REAL error message returned by the backend
      // (invalid credentials vs no permissions vs network issue) instead
      // of always showing a generic "Invalid credentials" message.
      const detail = error.response?.data?.detail;
      const msg = detail || 'Connection failed. Please check your keys and try again.';
      toast.error(msg);
      onConnectionError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-bg-secondary border border-border p-6 rounded-xl shadow-sm">
      <h2 className="text-lg font-semibold text-text-primary mb-2">Connect AWS Account</h2>
      <p className="text-sm text-text-muted mb-6">Enter your IAM credentials to allow the engine to scan your resources.</p>

      <div className="flex items-start gap-3 p-4 mb-6 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-400">
        <Lock size={20} className="shrink-0 mt-0.5" />
        <p className="text-sm leading-relaxed">
          <strong>Security Note:</strong> Your keys are encrypted with AES-256 and are never stored in plain text. We only require Read-Only permissions.
        </p>
      </div>

      <form onSubmit={handleTestConnection} className="space-y-4">
        <Input
          label="Access Key ID"
          type="text"
          placeholder="AKIAIOSFODNN7EXAMPLE"
          value={accessKey}
          onChange={(e) => setAccessKey(e.target.value)}
          autoComplete="off"
        />
        <Input
          label="Secret Access Key"
          type="password"
          placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
          value={secretKey}
          onChange={(e) => setSecretKey(e.target.value)}
          autoComplete="off"
        />
        <Button type="submit" isLoading={isLoading} className="mt-4">
          Test & Save Connection
        </Button>
      </form>
    </div>
  );
}
