import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const chartColors = ['#3b82f6', '#f97316', '#ef4444', '#22c55e', '#8b5cf6', '#06b6d4', '#ec4899', '#eab308'];

export function IssuesCategoryChart({ data }) {
  return (
    <div className="bg-black border-2 border-white/20 p-6 shadow-brutal">
      <h3 className="text-lg font-heading font-bold uppercase tracking-wider text-white mb-4 border-b-2 border-white/20 pb-2">Issues by Type</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff" strokeOpacity={0.1} />
          <XAxis dataKey="name" stroke="#ffffff" style={{ fontSize: '12px', fontFamily: 'JetBrains Mono' }} />
          <YAxis stroke="#ffffff" style={{ fontSize: '12px', fontFamily: 'JetBrains Mono' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#000000',
              border: '2px solid #ffffff',
              borderRadius: '0px',
              color: '#E0FF00',
              fontFamily: 'JetBrains Mono',
            }}
          />
          <Legend wrapperStyle={{ color: '#ffffff', fontFamily: 'JetBrains Mono' }} />
          <Bar dataKey="value" fill="#E0FF00" radius={[0, 0, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ReportsTimelineChart({ data }) {
  return (
    <div className="bg-black border-2 border-white/20 p-6 shadow-brutal">
      <h3 className="text-lg font-heading font-bold uppercase tracking-wider text-white mb-4 border-b-2 border-white/20 pb-2">Reports Timeline</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff" strokeOpacity={0.1} />
          <XAxis dataKey="date" stroke="#ffffff" style={{ fontSize: '12px', fontFamily: 'JetBrains Mono' }} />
          <YAxis stroke="#ffffff" style={{ fontSize: '12px', fontFamily: 'JetBrains Mono' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#000000',
              border: '2px solid #ffffff',
              borderRadius: '0px',
              color: '#E0FF00',
              fontFamily: 'JetBrains Mono',
            }}
          />
          <Legend wrapperStyle={{ color: '#ffffff', fontFamily: 'JetBrains Mono' }} />
          <Line
            type="step"
            dataKey="reports"
            stroke="#E0FF00"
            strokeWidth={3}
            dot={{ fill: '#000000', stroke: '#E0FF00', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, fill: '#E0FF00' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
