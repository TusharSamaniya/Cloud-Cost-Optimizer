import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function ForecastChart({ data }) {
  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
          
          <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} />
          
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#f9fafb', borderRadius: '8px' }}
            itemStyle={{ color: '#f9fafb' }}
            labelStyle={{ color: '#9ca3af', marginBottom: '4px' }}
            formatter={(value, name) => {
              if (name === 'confidence_bounds') return [`$${value} - $${value}`, 'Confidence Interval'];
              return [`$${value}`, 'Predicted Cost'];
            }}
          />

          {/* Shaded Confidence Interval */}
          <Area type="monotone" dataKey="confidence_bounds" stroke="none" fill="#1D9E75" fillOpacity={0.15} />
          
          {/* Solid Prediction Line */}
          <Line type="monotone" dataKey="predicted_cost" stroke="#1D9E75" strokeWidth={3} dot={false} />
          
          {/* Vertical marker for today */}
          <ReferenceLine x="Today" stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'top', value: 'Today', fill: '#ef4444', fontSize: 12 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}