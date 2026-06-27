import { Loader2 } from 'lucide-react';

export default function Button({ children, isLoading, className = '', ...props }) {
  return (
    <button
      disabled={isLoading || props.disabled}
      className={`flex items-center justify-center gap-2 w-full px-4 py-2 bg-accent hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {isLoading && <Loader2 size={18} className="animate-spin" />}
      {children}
    </button>
  );
}