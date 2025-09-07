import React, { createContext, useContext, useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import apiService from '../services/api';
import { getDefaultUnitsPreference } from '../utils/distance';

const PreferencesContext = createContext();

export const usePreferences = () => {
  const context = useContext(PreferencesContext);
  if (!context) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
};

export const PreferencesProvider = ({ children }) => {
  const { user } = useUser();
  const [unitsPreference, setUnitsPreference] = useState('imperial');
  const [loading, setLoading] = useState(true);

  // Load user preferences when user is available
  useEffect(() => {
    const loadPreferences = async () => {
      if (user?.primaryEmailAddress?.emailAddress) {
        try {
          const profile = await apiService.getUserProfileByEmail(user.primaryEmailAddress.emailAddress);
          if (profile && profile.units_preference) {
            setUnitsPreference(profile.units_preference);
          } else {
            // Use default based on user's location
            const defaultUnits = getDefaultUnitsPreference();
            setUnitsPreference(defaultUnits);
          }
        } catch (error) {
          console.error('Failed to load user preferences:', error);
          // Fallback to default
          setUnitsPreference(getDefaultUnitsPreference());
        } finally {
          setLoading(false);
        }
      } else {
        // No user, use default
        setUnitsPreference(getDefaultUnitsPreference());
        setLoading(false);
      }
    };

    loadPreferences();
  }, [user]);

  const updateUnitsPreference = async (newUnits) => {
    try {
      if (user?.primaryEmailAddress?.emailAddress) {
        // Get current user profile to include all required fields
        const profile = await apiService.getUserProfileByEmail(user.primaryEmailAddress.emailAddress);
        
        await apiService.updateProfile({
          email: user.primaryEmailAddress.emailAddress,
          name: profile.username,
          user_type: profile.user_type,
          car_license_plate: profile.license_plate || null,
          units_preference: newUnits
        });
        
        // Only update state if API call succeeded
        setUnitsPreference(newUnits);
      } else {
        // No user, just update local state
        setUnitsPreference(newUnits);
      }
    } catch (error) {
      console.error('Failed to update units preference:', error);
      throw error;
    }
  };

  const value = {
    unitsPreference,
    setUnitsPreference: updateUnitsPreference,
    loading
  };

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
};