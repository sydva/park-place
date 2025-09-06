import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, SignUp, SignIn, useAuth } from '@clerk/clerk-react';
import './App.css';
import Home from './components/Home';
import Map from './components/Map';
import ReportLicensePlate from './components/ReportLicensePlate';
import AddParkingSpace from './components/AddParkingSpace';
import ProtectedRoute from './components/ProtectedRoute';
import CompleteRegistration from './components/CompleteRegistration';

function AppRoutes() {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  return (
    <Routes>
      <Route 
        path="/" 
        element={
          isSignedIn ? (
            <ProtectedRoute><Map /></ProtectedRoute>
          ) : (
            <Home />
          )
        } 
      />
      <Route 
        path="/sign-in/*" 
        element={<SignIn routing="path" path="/sign-in" />} 
      />
      <Route 
        path="/sign-up/*" 
        element={<SignUp routing="path" path="/sign-up" />} 
      />
      <Route path="/complete-registration" element={<CompleteRegistration />} />
      <Route path="/map" element={<ProtectedRoute><Map /></ProtectedRoute>} />
      <Route 
        path="/report-license-plate" 
        element={<ProtectedRoute><ReportLicensePlate /></ProtectedRoute>} 
      />
      <Route 
        path="/add-parking-space" 
        element={<ProtectedRoute><AddParkingSpace /></ProtectedRoute>} 
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;