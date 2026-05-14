import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';
import { ArrowLeft, AlertCircle, MapPin } from 'lucide-react';
import apiService from '../services/apiService';

export function ReportDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIssue = async () => {
      setLoading(true);
      try {
        const data = await apiService.fetchReportById(id);
        setIssue(data);
      } catch (err) {
        console.error('Failed to fetch report:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchIssue();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-transparent">
        <Sidebar />
        <Topbar />
        <main className="ml-80 mt-16 p-8 flex items-center justify-center">
          <div className="text-acid font-mono uppercase tracking-widest animate-pulse font-bold">Loading Terminal...</div>
        </main>
      </div>
    );
  }

  if (!issue) {
    return (
      <div className="min-h-screen bg-transparent">
        <Sidebar />
        <Topbar />
        <main className="ml-80 mt-16 p-8">
          <div className="text-center font-mono text-white/50 uppercase tracking-widest border-2 border-dashed border-white/20 p-12">
            [ ERROR: Issue not found in database ]
          </div>
        </main>
      </div>
    );
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'critical':
        return 'text-black bg-acid border-white';
      case 'medium':
        return 'text-white bg-violet border-white';
      default:
        return 'text-black bg-white border-white';
    }
  };

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
          {/* Back Button */}
          <motion.button
            whileHover={{ x: -4 }}
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 px-4 py-2 border-2 border-transparent hover:border-white/20 text-white hover:bg-white/5 transition-all font-bold uppercase tracking-widest text-sm"
          >
            <ArrowLeft size={20} />
            <span>Back</span>
          </motion.button>

          {/* Header */}
          <div className="flex items-start justify-between border-b-2 border-white/20 pb-4">
            <div>
              <h1 className="text-4xl font-heading font-bold uppercase tracking-wider text-white mb-2">Report {issue.id}</h1>
            </div>
            <div className={`flex items-center gap-2 px-6 py-2 border-2 shadow-brutal ${getUrgencyColor(issue.urgency)}`}>
              <AlertCircle size={20} />
              <span className="font-bold uppercase tracking-widest">{issue.urgency}</span>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Image */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative bg-black border-2 border-white/20 shadow-brutal"
              >
                <img
                  src={issue.image}
                  alt={issue.title}
                  className="w-full h-96 object-cover"
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-6 p-6 bg-black border-2 border-white/20 shadow-brutal"
              >
                <h2 className="text-2xl font-heading font-bold uppercase tracking-wider text-white mb-6 border-b-2 border-white/20 pb-2">Analysis</h2>
                
                <div className="space-y-6 font-mono">
                  <div>
                    <p className="text-acid text-sm mb-1 uppercase font-bold tracking-widest">Description</p>
                    <p className="text-white text-lg leading-relaxed">{issue.description}</p>
                  </div>
                  
                  <div>
                    <p className="text-acid text-sm mb-1 uppercase font-bold tracking-widest">Impact</p>
                    <p className="text-white text-lg leading-relaxed">{issue.impact}</p>
                  </div>
                  
                  <div>
                    <p className="text-acid text-sm mb-1 uppercase font-bold tracking-widest">Suggested Action</p>
                    <p className="text-white text-lg leading-relaxed">{issue.suggestedAction}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t-2 border-white/20">
                    <div className="p-4 bg-white/5 border-2 border-white/20">
                      <p className="text-white/50 text-sm mb-1 uppercase tracking-widest">Issue Type</p>
                      <p className="text-xl font-bold text-white uppercase">{issue.issueType}</p>
                    </div>
                    <div className="p-4 bg-white/5 border-2 border-white/20">
                      <p className="text-white/50 text-sm mb-1 uppercase tracking-widest">Urgency</p>
                      <p className={`text-xl font-bold text-white uppercase ${getUrgencyColor(issue.urgency).split(' ')[0]}`}>
                        {issue.urgency}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Right: Details & Actions */}
            <div className="space-y-6">
              {/* Location */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="p-6 bg-black border-2 border-white/20 shadow-brutal"
              >
                <h3 className="text-xl font-heading font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2 border-b-2 border-white/20 pb-2">
                  <MapPin size={24} className="text-acid" />
                  Location
                </h3>
                <p className="text-acid text-sm mb-1 uppercase font-bold tracking-widest">Coordinates</p>
                <p className="text-white font-mono text-lg">
                  {issue.latitude.toFixed(4)}, {issue.longitude.toFixed(4)}
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="p-6 bg-black border-2 border-white/20 shadow-brutal"
              >
                <h3 className="text-xl font-heading font-bold uppercase tracking-wider text-white mb-4 border-b-2 border-white/20 pb-2">Timestamps</h3>
                <div className="space-y-2 font-mono text-sm text-white/50">
                  <p>
                    CREATED: <span className="text-white">{new Date(issue.createdAt).toLocaleString()}</span>
                  </p>
                </div>
              </motion.div>

            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
