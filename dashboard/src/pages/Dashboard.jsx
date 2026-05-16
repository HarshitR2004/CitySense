import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';
import { IssuesMap } from '../components/IssuesMap';
import { ReportsTable } from '../components/ReportsTable';
import { IssuesCategoryChart, ReportsTimelineChart } from '../components/Charts';
import apiService from '../services/apiService';

export function Dashboard() {
  const [issues, setIssues] = useState([]);
  const [selectedIssue, setSelectedIssue] = useState(null);
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

  const recentIssues = issues.slice(0, 5);
  const criticalIssues = issues.filter((i) => i.urgency === 'critical');



  const issuesByCategoryChart = useMemo(() => {
    const counts = {};
    issues.forEach(i => {
      const cat = i.issueType || 'unknown';
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [issues]);

  const reportsTimelineData = useMemo(() => {
    const counts = {};
    issues.forEach(i => {
      const dateStr = new Date(i.createdAt).toLocaleDateString('en-US', { month: 'short', day: '2-digit' });
      counts[dateStr] = (counts[dateStr] || 0) + 1;
    });
    const sortedDates = Object.keys(counts).sort((a, b) => new Date(a) - new Date(b));
    return sortedDates.slice(-7).map(date => ({ date, reports: counts[date] }));
  }, [issues]);



  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  return (
    <div className="min-h-screen bg-transparent">
      <Sidebar />
      <Topbar />

      <main className="ml-80 mt-16 p-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          {/* Hero Section */}
          <motion.div variants={itemVariants} className="border-b-2 border-white/20 pb-4">
            <h1 className="text-4xl font-heading font-bold uppercase tracking-wider text-white mb-2">
              Smart City Terminal
            </h1>
            <p className="text-acid font-mono uppercase tracking-widest text-sm">AI-powered</p>
          </motion.div>



          {/* Map */}
          <motion.div variants={itemVariants} className="bg-black border-2 border-white/20 p-6 shadow-brutal">
            <h2 className="text-xl font-heading font-bold uppercase tracking-wider text-white mb-4 border-b-2 border-white/20 pb-2">Map</h2>
            <div className="h-[400px]">
              <IssuesMap issues={issues} onMarkerClick={setSelectedIssue} />
            </div>
          </motion.div>

          {/* Reports Table */}
          <motion.div variants={itemVariants}>
            <div className="flex items-center justify-between mb-4 border-b-2 border-white/20 pb-2">
              <h2 className="text-xl font-heading font-bold uppercase tracking-wider text-white">Recent Reports</h2>
              <span className="text-sm font-mono text-acid font-bold">[{issues.length} total]</span>
            </div>
            <ReportsTable issues={recentIssues} />
          </motion.div>

          {/* Charts */}
          <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <IssuesCategoryChart data={issuesByCategoryChart} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <ReportsTimelineChart data={reportsTimelineData} />
          </motion.div>

          {/* Critical Issues Alert */}
          {criticalIssues.length > 0 && (
            <motion.div
              variants={itemVariants}
              className="p-6 bg-acid border-2 border-white shadow-brutal"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-heading font-bold uppercase tracking-wider text-black mb-2">Critical Issues Detected</h3>
                  <p className="text-black font-mono font-bold">
                    {criticalIssues.length} critical issue{criticalIssues.length !== 1 ? 's' : ''} require immediate attention
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-2 bg-black text-acid font-bold border-2 border-black hover:bg-transparent hover:text-black hover:border-black transition-all shadow-brutal-sm"
                >
                  REVIEW
                </motion.button>
              </div>
            </motion.div>
          )}
        </motion.div>
      </main>
    </div>
  );
}

