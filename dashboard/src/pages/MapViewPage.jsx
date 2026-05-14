import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';
import { IssuesMap } from '../components/IssuesMap';

import apiService from '../services/apiService';

export function MapViewPage() {
  const [issues, setIssues] = useState([]);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await apiService.fetchReports();
        setIssues(data);
      } catch (err) {
        console.error('Failed to fetch reports:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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
            <h1 className="text-4xl font-heading font-bold uppercase tracking-wider text-white mb-2">Map View</h1>
            <p className="text-acid font-mono uppercase tracking-widest text-sm">Geographic visualization of all civic issues</p>
          </div>


          {/* Map */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="h-[600px] bg-black border-2 border-white/20 shadow-brutal p-4">
              <IssuesMap issues={issues} onMarkerClick={setSelectedIssue} />
            </div>
          </motion.div>

          {/* Selected Issue Details */}
          {selectedIssue ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              <div className="p-6 bg-black border-2 border-white/20 shadow-brutal flex flex-col justify-between">
                <div>
                  <h3 className="text-xl font-heading font-bold uppercase tracking-wider text-white mb-4 border-b-2 border-white/20 pb-2">Issue Details</h3>
                  <div className="space-y-4 font-mono">
                    <div className="flex justify-between border-b border-white/10 pb-2">
                      <p className="text-sm text-white/50 uppercase">Report ID</p>
                      <p className="text-white font-bold">{selectedIssue.id}</p>
                    </div>
                    <div className="flex justify-between border-b border-white/10 pb-2">
                      <p className="text-sm text-white/50 uppercase">Location</p>
                      <p className="text-white">
                        {selectedIssue.latitude.toFixed(4)}, {selectedIssue.longitude.toFixed(4)}
                      </p>
                    </div>
                    <div className="flex justify-between border-b border-white/10 pb-2">
                      <p className="text-sm text-white/50 uppercase">Urgency</p>
                      <p
                        className={`font-bold uppercase ${
                          selectedIssue.urgency === 'critical'
                            ? 'text-acid'
                            : selectedIssue.urgency === 'medium'
                            ? 'text-violet'
                            : 'text-white'
                        }`}
                      >
                        {selectedIssue.urgency}
                      </p>
                    </div>
                    <div className="flex justify-between">
                      <p className="text-sm text-white/50 uppercase">Detected</p>
                      <p className="text-white">
                        {new Date(selectedIssue.createdAt).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-6 bg-black border-2 border-white/20 shadow-brutal flex flex-col">
                <h3 className="text-xl font-heading font-bold uppercase tracking-wider text-white mb-4 border-b-2 border-white/20 pb-2">Analysis</h3>
                <img
                  src={selectedIssue.image}
                  alt={selectedIssue.id}
                  className="w-full h-48 object-cover border-2 border-white/20 mb-4 grayscale hover:grayscale-0 transition-all"
                />
                <div className="space-y-4 font-mono flex-1">
                  <div>
                    <p className="text-sm text-acid uppercase mb-1">Description</p>
                    <p className="text-white text-sm leading-relaxed">
                      {selectedIssue.description}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-acid uppercase mb-1">Impact</p>
                    <p className="text-white text-sm leading-relaxed">
                      {selectedIssue.impact}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-acid uppercase mb-1">Issue Type</p>
                    <p className="text-white font-bold text-sm uppercase">
                      {selectedIssue.issueType}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : null}
        </motion.div>
      </main>
    </div>
  );
}
