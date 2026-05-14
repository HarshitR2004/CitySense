import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { ReportsPage } from './pages/ReportsPage';
import { MapViewPage } from './pages/MapViewPage';
import { ReportDetailsPage } from './pages/ReportDetailsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/report/:id" element={<ReportDetailsPage />} />
        <Route path="/map" element={<MapViewPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
