import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import * as Icons from 'lucide-react';

export function StatCard({ label, value, icon, trend, color = 'blue' }) {
  const Icon = Icons[icon] || Icons.Activity;

  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-500/30 text-blue-400',
    red: 'from-red-500/20 to-red-600/20 border-red-500/30 text-red-400',
    orange: 'from-orange-500/20 to-orange-600/20 border-orange-500/30 text-orange-400',
    green: 'from-green-500/20 to-green-600/20 border-green-500/30 text-green-400',
  };

  const isTrendingUp = !trend.startsWith('-');

  return (
    <motion.div
      whileHover={{ translateY: -4 }}
      transition={{ duration: 0.2 }}
      className={`p-6 rounded-2xl bg-gradient-to-br ${colorClasses[color]} border backdrop-blur-sm cursor-pointer group overflow-hidden relative`}
    >
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-lg ${color === 'blue' ? 'bg-blue-500/20' : color === 'red' ? 'bg-red-500/20' : color === 'orange' ? 'bg-orange-500/20' : 'bg-green-500/20'}`}>
            <Icon size={24} />
          </div>
          <div className={`flex items-center gap-1 text-sm font-semibold ${isTrendingUp ? 'text-green-400' : 'text-red-400'}`}>
            {isTrendingUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{trend}</span>
          </div>
        </div>

        <p className="text-slate-400 text-sm mb-1">{label}</p>
        <h3 className="text-3xl font-bold text-white">{value}</h3>
      </div>
    </motion.div>
  );
}
