export default function Input({ label, error, ...props }) {
  return (
    <div className="flex flex-col gap-1 w-full">
      {label && <label className="text-sm font-medium text-text-primary">{label}</label>}
      <input
        // We replaced the custom variables here with explicit Tailwind colors to prevent browser overrides
        className={`px-4 py-2 bg-white dark:bg-gray-900 border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent text-gray-900 dark:text-white transition-colors ${
          error ? 'border-red-500' : 'border-border'
        }`}
        {...props}
      />
      {error && <span className="text-xs text-red-500 mt-1">{error}</span>}
    </div>
  );
}