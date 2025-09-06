import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser, useClerk } from '@clerk/clerk-react';
import apiService from '../services/api';
import './UserMenu.css';

const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [dbUserProfile, setDbUserProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();

  useEffect(() => {
    const fetchUserProfile = async () => {
      if (user?.primaryEmailAddress?.emailAddress) {
        try {
          const profile = await apiService.getUserProfileByEmail(user.primaryEmailAddress.emailAddress);
          setDbUserProfile(profile);
        } catch (error) {
          console.error('Failed to fetch user profile from database:', error);
          setDbUserProfile(null);
        } finally {
          setProfileLoading(false);
        }
      } else {
        setProfileLoading(false);
      }
    };

    if (isLoaded && user) {
      fetchUserProfile();
    } else {
      setProfileLoading(false);
    }
  }, [user, isLoaded]);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = async () => {
    setIsOpen(false);
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleReportLicensePlate = () => {
    setIsOpen(false);
    navigate('/report-license-plate');
  };

  const handleAddParkingSpace = () => {
    setIsOpen(false);
    navigate('/add-parking-space');
  };

  return (
    <div className="user-menu-container">
      <button className="menu-button" onClick={toggleMenu}>
        ☰
      </button>
      
      {isOpen && (
        <div className="menu-dropdown">
          <div className="menu-backdrop" onClick={toggleMenu}></div>
          <div className="menu-content">
            {!isLoaded || profileLoading ? (
              <div className="menu-item">Loading...</div>
            ) : user ? (
              <>
                <div className="menu-item">
                  <strong>Name:</strong> {user.fullName || user.firstName || 'Unknown'}
                </div>
                <div className="menu-item">
                  <strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}
                </div>
                {dbUserProfile ? (
                  <>
                    <div className="menu-item">
                      <strong>Username:</strong> {dbUserProfile.username}
                    </div>
                    <div className="menu-item">
                      <strong>User Type:</strong> {dbUserProfile.user_type}
                    </div>
                    {dbUserProfile.license_plate && (
                      <div className="menu-item">
                        <strong>License Plate:</strong> {dbUserProfile.license_plate_state ? `${dbUserProfile.license_plate_state}-` : ''}{dbUserProfile.license_plate}
                      </div>
                    )}
                    <div className="menu-item">
                      <strong>Status:</strong> 
                      <span className="verification-status verified">
                        ✓ Registered User
                      </span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="menu-item">
                      <strong>Database Status:</strong> 
                      <span className="verification-status unverified">
                        ⚠ Not Registered
                      </span>
                    </div>
                    <div className="menu-item" style={{fontSize: '12px', color: '#666'}}>
                      Complete registration to access all features
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="menu-item">Not signed in</div>
            )}
            <button className="menu-action-button" onClick={handleReportLicensePlate}>
              Report License Plate
            </button>
            <button className="menu-action-button" onClick={handleAddParkingSpace}>
              Add New Parking Space
            </button>
            <button className="logout-button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;