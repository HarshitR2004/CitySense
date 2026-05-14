import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, Zap, TrendingUp } from 'lucide-react';

export function ActivityPanel({ activities }) {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'assignment':
        return <Zap size={16} className="text-blue-400" />;
      case 'resolution':
        return <CheckCircle2 size={16} className="text-green-400" />;
      case 'detection':
        return <AlertCircle size={16} className="text-red-400" />;
      default:
        return <TrendingUp size={16} className="text-slate-400" />;
    }
  };

  const getActivityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'border-l-4 border-l-red-500';
      case 'medium':
        return 'border-l-4 border-l-orange-500';
      default:
        return 'border-l-4 border-l-green-500';
    }
  };

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <motion.div
          key={activity.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`p-4 bg-slate-800/50 border border-slate-700/50 rounded-lg backdrop-blur hover:bg-slate-800/80 transition-colors ${getActivityColor(activity.severity)}`}
        >
          <div className="flex items-start gap-3">
            <div className="mt-1 flex-shrink-0">
              {getActivityIcon(activity.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium">{activity.action}</p>
              <p className="text-xs text-slate-500 mt-1">{activity.timestamp}</p>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
