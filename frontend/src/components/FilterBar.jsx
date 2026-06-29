export default function FilterBar({ options, activeFilter, onFilterChange }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onFilterChange(opt)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
            activeFilter === opt 
              ? 'bg-accent text-white border-accent' 
              : 'bg-bg-secondary text-text-muted hover:text-text-primary border border-border'
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}