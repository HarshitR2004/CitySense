import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Home, FileText, Map } from 'lucide-react';
import { motion } from 'framer-motion';

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/map', label: 'Map View', icon: Map },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <motion.div
      initial={false}
      animate={{ width: isOpen ? 256 : 80 }}
      transition={{ duration: 0.3 }}
      className="bg-black border-r-2 border-white/20 h-screen flex flex-col fixed left-0 top-0 z-50"
    >
      {/* Logo Section */}
      <div className="p-6 border-b-2 border-white/20 flex items-center justify-between">
        <motion.div
          animate={{ opacity: isOpen ? 1 : 0, width: isOpen ? 'auto' : 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-acid border-2 border-white flex items-center justify-center shadow-brutal-sm">
              <span className="text-black font-heading font-bold text-xl">S</span>
            </div>
            <div>
              <h1 className="text-white font-heading font-bold uppercase tracking-wider text-sm">SmartCity</h1>
              <p className="text-acid font-mono text-xs">Municipal Hub</p>
            </div>
          </div>
        </motion.div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-slate-400 hover:text-white transition-colors"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                whileHover={{ x: isOpen ? 4 : 0 }}
                className={`relative p-3 flex items-center gap-3 transition-all cursor-pointer group border-2 ${
                  active
                    ? 'bg-acid text-black border-acid shadow-brutal-acid'
                    : 'text-slate-400 border-transparent hover:border-white/20 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon size={20} className="relative z-10 flex-shrink-0" />
                {isOpen && (
                  <span className="text-sm font-bold uppercase tracking-wide relative z-10">{item.label}</span>
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>
    </motion.div>
  );
}
