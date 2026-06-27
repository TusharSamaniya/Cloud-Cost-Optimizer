import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { login as loginApi } from '../api/auth';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  // Step 6: If already logged in, send them straight to the dashboard
  useEffect(() => {
    if (isAuthenticated) navigate('/');
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault(); // Stop the page from reloading
    setError('');

    if (!email || !password) {
      return setError('Please fill in all fields.');
    }

    setIsLoading(true);
    try {
      const data = await loginApi(email, password);
      login(data.access_token); // Save token to context
      toast.success('Welcome back!');
      navigate('/'); // Go to dashboard
    } catch (err) {
      setError('Invalid email or password. Please try again.'); // Friendly error message
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary p-4">
      <div className="w-full max-w-md bg-bg-secondary border border-border rounded-xl p-8 shadow-lg animate-fade-in">
        <h1 className="text-2xl font-bold text-text-primary text-center mb-6">Welcome Back</h1>
        
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded text-red-500 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input label="Password" type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button type="submit" isLoading={isLoading} className="mt-6">Sign In</Button>
        </form>

        <p className="mt-6 text-center text-sm text-text-muted">
          Don't have an account? <Link to="/register" className="text-accent hover:underline">Register here</Link>
        </p>
      </div>
    </div>
  );
}