export default function Input({ label, error, ...props }) {
  return (
    <div className="flex flex-col gap-1 w-full">
      {label && <label className="text-sm font-medium text-text-primary">{label}</label>}
      <input
        className={`px-4 py-2 bg-bg-primary border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent text-text-primary transition-colors ${
          error ? 'border-red-500' : 'border-border'
        }`}
        {...props}
      />
      {error && <span className="text-xs text-red-500 mt-1">{error}</span>}
    </div>
  );
}