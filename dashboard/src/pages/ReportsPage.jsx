import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';
import { ReportsTable } from '../components/ReportsTable';

import { Filter, Download } from 'lucide-react';
import apiService from '../services/apiService';

export function ReportsPage() {
  const [issues, setIssues] = useState([]);
  const [filters, setFilters] = useState({
    urgency: 'all',
    issueType: 'all',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    const unsubscribe = apiService.subscribeReports(
      (data) => {
        setIssues(data);
        setLoading(false);
      },
      (err) => {
        console.error('Failed to subscribe to reports:', err);
        setLoading(false);
      }
    );

    return () => unsubscribe?.();
  }, []);

  const filteredIssues = issues.filter((issue) => {
    if (filters.urgency !== 'all' && issue.urgency !== filters.urgency) return false;
    if (filters.issueType !== 'all' && issue.issueType !== filters.issueType) return false;
    return true;
  });

  const issueTypes = [...new Set(issues.map((i) => i.issueType))];
  const urgencies = ['critical', 'medium', 'low'];

  return (
    <div className="min-h-screen bg-transparent">
      <Sidebar />
      <Topbar />

      <main className="ml-80 mt-16 p-8">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          {/* Header */}
          <div className="border-b-2 border-white/20 pb-4">
            <h1 className="text-4xl font-heading font-bold uppercase tracking-wider text-white mb-2">Reports</h1>
            <p className="text-acid font-mono uppercase tracking-widest text-sm">Manage and track all civic issues</p>
          </div>

          {/* Filters & Actions */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between p-6 bg-black border-2 border-white/20 shadow-brutal"
          >
            <div className="flex flex-col md:flex-row gap-4 flex-1">
              {/* Urgency Filter */}
              <select
                value={filters.urgency}
                onChange={(e) => setFilters({ ...filters, urgency: e.target.value })}
                className="px-4 py-2 bg-black border-2 border-white/20 text-sm font-bold uppercase text-white focus:outline-none focus:border-acid focus:shadow-brutal-acid transition-all appearance-none cursor-pointer"
              >
                <option value="all">All Urgencies</option>
                {urgencies.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>

              {/* Issue Type Filter */}
              <select
                value={filters.issueType}
                onChange={(e) => setFilters({ ...filters, issueType: e.target.value })}
                className="px-4 py-2 bg-black border-2 border-white/20 text-sm font-bold uppercase text-white focus:outline-none focus:border-acid focus:shadow-brutal-acid transition-all appearance-none cursor-pointer"
              >
                <option value="all">All Types</option>
                {issueTypes.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </motion.div>

          {/* Results Counter */}
          <div className="text-sm font-mono text-white/70 uppercase">
            Showing <span className="font-bold text-acid">{filteredIssues.length}</span> of{' '}
            <span className="font-bold text-acid">{issues.length}</span> reports
          </div>

          {/* Reports Table */}
          <ReportsTable issues={filteredIssues} />
        </motion.div>
      </main>
    </div>
  );
}
