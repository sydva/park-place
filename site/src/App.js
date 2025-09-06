import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './components/Home';
import Map from './components/Map';
import ReportLicensePlate from './components/ReportLicensePlate';
import AddParkingSpace from './components/AddParkingSpace';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/map" element={<Map />} />
        <Route path="/report-license-plate" element={<ReportLicensePlate />} />
        <Route path="/add-parking-space" element={<AddParkingSpace />} />
      </Routes>
    </Router>
  );
}

export default App;