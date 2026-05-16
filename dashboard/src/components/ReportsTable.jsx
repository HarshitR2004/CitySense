import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye } from 'lucide-react';
import { Link } from 'react-router-dom';

export function ReportsTable({ issues }) {
  const [hoveredRow, setHoveredRow] = useState(null);

  const getStatusBadgeStyle = (status) => {
    switch ((status || '').toLowerCase()) {
      case 'reported':
        return 'bg-white text-black border-white';
      case 'reviewed':
        return 'bg-violet text-white border-violet';
      case 'resolved':
        return 'bg-acid text-black border-acid';
      case 'closed':
        return 'bg-white/10 text-white border-white/20';
      default:
        return 'bg-transparent text-white border-white/50';
    }
  };


  const getUrgencyBadgeStyle = (urgency) => {
    switch (urgency) {
      case 'critical':
        return 'bg-acid text-black border-acid';
      case 'medium':
        return 'bg-violet text-white border-violet';
      case 'low':
        return 'bg-white text-black border-white';
      default:
        return 'bg-transparent text-white border-white/50';
    }
  };

  return (
    <div className="w-full bg-black border-2 border-white/20 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-white/20 bg-white/5">
              <th className="px-6 py-4 text-left text-xs font-heading font-bold text-white uppercase tracking-wider border-r-2 border-white/10">
                Issue
              </th>
              <th className="px-6 py-4 text-left text-xs font-heading font-bold text-white uppercase tracking-wider border-r-2 border-white/10">
                Urgency
              </th>
              <th className="px-6 py-4 text-left text-xs font-heading font-bold text-white uppercase tracking-wider border-r-2 border-white/10">
                Location
              </th>
              <th className="px-6 py-4 text-left text-xs font-heading font-bold text-white uppercase tracking-wider border-r-2 border-white/10">
                Date
              </th>
              <th className="px-6 py-4 text-right text-xs font-heading font-bold text-white uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue, index) => (
              <motion.tr
                key={issue.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                onMouseEnter={() => setHoveredRow(issue.id)}
                onMouseLeave={() => setHoveredRow(null)}
                className="border-b-2 border-white/20 hover:bg-white/10 transition-colors cursor-pointer group"
              >
                <td className="px-6 py-4 border-r-2 border-white/10">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <div className="flex flex-col gap-1">
                        <img
                          src={issue.image}
                          alt={`${issue.id} original`}
                          className="w-12 h-12 object-cover border-2 border-white/20 grayscale group-hover:grayscale-0 transition-all"
                        />
                      </div>
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-bold text-white truncate uppercase font-mono">{issue.id}</p>
                      <span className={`mt-2 inline-flex items-center px-2 py-1 text-[10px] font-bold uppercase tracking-wider border ${getStatusBadgeStyle(issue.reportStatus)}`}>
                        {issue.reportStatus}
                      </span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 border-r-2 border-white/10">
                  <span className={`inline-flex items-center px-3 py-1 text-xs font-bold uppercase tracking-wider border-2 ${getUrgencyBadgeStyle(issue.urgency)}`}>
                    {issue.urgency.toUpperCase()}
                  </span>
                </td>
                {/* AI processing UI removed per request */}
                <td className="px-6 py-4 border-r-2 border-white/10">
                  <p className="text-sm text-white/70 truncate font-mono">{issue.latitude.toFixed(4)}, {issue.longitude.toFixed(4)}</p>
                </td>
                <td className="px-6 py-4 border-r-2 border-white/10">
                  <p className="text-sm text-white/70 font-mono">
                    {new Date(issue.createdAt).toLocaleDateString()}
                  </p>
                </td>
                <td className="px-6 py-4 text-right">
                  <motion.div
                    animate={{ opacity: hoveredRow === issue.id ? 1 : 0.7 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Link
                      to={`/report/${issue.id}`}
                      className="inline-flex items-center gap-2 px-4 py-2 border-2 border-white text-white hover:bg-acid hover:text-black hover:border-acid shadow-brutal hover:shadow-none hover:translate-x-1 hover:translate-y-1 transition-all uppercase font-bold text-xs tracking-wider"
                    >
                      <Eye size={16} />
                      <span>View</span>
                    </Link>
                  </motion.div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
