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
import EditProfile from './components/EditProfile';
import AuthLayout from './components/AuthLayout';
import Terms from './components/Terms';
import Privacy from './components/Privacy';
import VerifyIdentity from './components/VerifyIdentity';
import { PreferencesProvider } from './contexts/PreferencesContext';

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
        element={
          <AuthLayout>
            <SignIn routing="path" path="/sign-in" />
          </AuthLayout>
        } 
      />
      <Route 
        path="/sign-up/*" 
        element={
          <AuthLayout>
            <SignUp routing="path" path="/sign-up" />
          </AuthLayout>
        } 
      />
      <Route path="/complete-registration" element={<CompleteRegistration />} />
      <Route path="/map" element={<ProtectedRoute><Map /></ProtectedRoute>} />
      <Route path="/browse" element={<Map />} />
      <Route 
        path="/edit-profile" 
        element={<ProtectedRoute><EditProfile /></ProtectedRoute>} 
      />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route 
        path="/report-license-plate" 
        element={<ProtectedRoute><ReportLicensePlate /></ProtectedRoute>} 
      />
      <Route 
        path="/add-parking-space" 
        element={<ProtectedRoute><AddParkingSpace /></ProtectedRoute>} 
      />
      <Route 
        path="/verify-identity" 
        element={<ProtectedRoute><VerifyIdentity /></ProtectedRoute>} 
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <PreferencesProvider>
        <AppRoutes />
      </PreferencesProvider>
    </Router>
  );
}

export default App;