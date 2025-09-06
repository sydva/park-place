import React, { useState, useEffect } from 'react';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';
import apiService from '../services/api';

const ProtectedRoute = ({ children }) => {
  const { isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();
  const [registrationStatus, setRegistrationStatus] = useState('checking');
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkRegistration = async () => {
      if (isLoaded && isSignedIn && user?.primaryEmailAddress?.emailAddress) {
        try {
          const profile = await apiService.getUserProfileByEmail(user.primaryEmailAddress.emailAddress);
          if (profile) {
            setRegistrationStatus('complete');
          } else {
            setRegistrationStatus('incomplete');
          }
        } catch (error) {
          console.error('Failed to check registration status:', error);
          setRegistrationStatus('incomplete');
        }
      }
    };

    if (isLoaded && isSignedIn) {
      checkRegistration();
    }
  }, [isLoaded, isSignedIn, user]);

  if (!isLoaded || registrationStatus === 'checking') {
    return <div>Loading...</div>;
  }

  if (!isSignedIn) {
    return <Navigate to="/sign-in" replace />;
  }

  if (registrationStatus === 'incomplete') {
    return <Navigate to="/complete-registration" replace />;
  }

  return children;
};

export default ProtectedRoute;