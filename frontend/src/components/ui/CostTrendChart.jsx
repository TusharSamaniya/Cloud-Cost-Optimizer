import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function CostTrendChart({ data }) {
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorTrajectory" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorOptimised" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1D9E75" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#1D9E75" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
          <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#f9fafb', borderRadius: '8px' }}
            itemStyle={{ color: '#f9fafb' }}
            formatter={(value) => [`$${value}`, '']}
          />
          <Area type="monotone" name="Current Trajectory" dataKey="trajectory" stroke="#ef4444" fillOpacity={1} fill="url(#colorTrajectory)" />
          <Area type="monotone" name="After Optimisation" dataKey="optimised" stroke="#1D9E75" fillOpacity={1} fill="url(#colorOptimised)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}