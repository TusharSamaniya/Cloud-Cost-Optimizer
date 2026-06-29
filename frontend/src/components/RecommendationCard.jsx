import Button from './ui/Button';

export default function RecommendationCard({ id, title, description, savingAmount, priority, status, onAction }) {
  const borderColors = { high: 'border-l-red-500', medium: 'border-l-amber-500', low: 'border-l-blue-500' };
  const borderColor = borderColors[priority?.toLowerCase()] || 'border-l-gray-500';
  
  const isApplied = status === 'applied';

  return (
    <div className={`bg-bg-secondary border border-border border-l-4 ${borderColor} p-6 rounded-r-xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition-all duration-300 ${isApplied ? 'opacity-60 grayscale' : ''}`}>
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-1">
          <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
          <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${isApplied ? 'border-green-500 text-green-500' : 'border-border text-text-muted'}`}>
            {isApplied ? 'Applied' : priority}
          </span>
        </div>
        <p className="text-sm text-text-muted">{description}</p>
      </div>
      
      <div className="flex flex-col items-end gap-3 w-full md:w-auto">
        <span className="text-2xl font-bold text-green-500 transition-all">+${savingAmount}/mo</span>
        
        {status === 'pending' && (
          <div className="flex gap-2 w-full md:w-auto">
            <button 
              onClick={() => onAction(id, 'dismissed')} 
              className="flex-1 md:flex-none px-4 py-2 text-sm font-medium text-text-muted border border-border rounded-lg hover:bg-bg-primary transition-colors"
            >
              Dismiss
            </button>
            <Button onClick={() => onAction(id, 'applied')} className="flex-1 md:flex-none py-2 text-sm">
              Apply
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}