import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser, useClerk } from '@clerk/clerk-react';
import apiService from '../services/api';
import './UserMenu.css';
import Icon from './Icon';

const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [dbUserProfile, setDbUserProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [editingField, setEditingField] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [editState, setEditState] = useState('');
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
          console.error('Failed to fetch user profile:', error);
          setDbUserProfile(null);
        } finally {
          setProfileLoading(false);
        }
      } else {
        setProfileLoading(false);
      }
    };

    const fetchNotificationCount = async () => {
      if (user?.primaryEmailAddress?.emailAddress) {
        try {
          const countData = await apiService.getUnreadCount(user.primaryEmailAddress.emailAddress);
          setUnreadCount(countData.unread_count);
        } catch (error) {
          console.error('Failed to fetch notification count:', error);
          setUnreadCount(0);
        }
      }
    };

    if (isLoaded && user) {
      fetchUserProfile();
      fetchNotificationCount();
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

  const handleEditProfile = () => {
    setIsOpen(false);
    navigate('/edit-profile');
  };

  const handleVerifyIdentity = () => {
    setIsOpen(false);
    navigate('/verify-identity');
  };

  const startEditing = (field, currentValue) => {
    setEditingField(field);
    setEditValue(currentValue || '');
    setEditState('');
  };

  const cancelEditing = () => {
    setEditingField(null);
    setEditValue('');
    setEditState('');
  };

  const saveField = async () => {
    if (!user?.primaryEmailAddress?.emailAddress) return;

    try {
      let updateData = {
        email: user.primaryEmailAddress.emailAddress,
        name: dbUserProfile.username,
        user_type: dbUserProfile.user_type,
        car_license_plate: dbUserProfile.license_plate || null,
      };

      if (editingField === 'username') {
        updateData.name = editValue.trim();
      } else if (editingField === 'license_plate') {
        updateData.car_license_plate = editValue.trim() || null;
      }

      await apiService.updateProfile(updateData);
      
      // Refresh profile data
      const profile = await apiService.getUserProfileByEmail(user.primaryEmailAddress.emailAddress);
      setDbUserProfile(profile);
      
      cancelEditing();
    } catch (error) {
      console.error('Failed to update field:', error);
      alert('Failed to update. Please try again.');
    }
  };

  return (
    <div className="user-menu-container">
      <button className="menu-button" onClick={toggleMenu}>
        ☰
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
        )}
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
                  <strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}
                </div>
                {dbUserProfile ? (
                  <>
                    <div className="menu-item editable-item">
                      <strong>Username:</strong> 
                      {editingField === 'username' ? (
                        <div className="inline-edit">
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="edit-input"
                            maxLength="50"
                            autoFocus
                          />
                          <button className="save-btn" onClick={saveField}>✓</button>
                          <button className="cancel-btn" onClick={cancelEditing}>✕</button>
                        </div>
                      ) : (
                        <div className="field-display">
                          <span>{dbUserProfile.username}</span>
                          <button 
                            className="edit-icon"
                            onClick={() => startEditing('username', dbUserProfile.username)}
                            aria-label="Edit username"
                            title="Edit username"
                          >
                            <Icon name="edit" size={14} />
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="menu-item">
                      <strong>User Type:</strong> {dbUserProfile.user_type}
                    </div>
                    <div className="menu-item editable-item">
                      <strong>License Plate:</strong>
                      {editingField === 'license_plate' ? (
                        <div className="inline-edit">
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value.toUpperCase())}
                            className="edit-input"
                            placeholder="ABC123"
                            maxLength="10"
                            autoFocus
                          />
                          <button className="save-btn" onClick={saveField}>✓</button>
                          <button className="cancel-btn" onClick={cancelEditing}>✕</button>
                        </div>
                      ) : (
                        <div className="field-display">
                          <span>
                            {dbUserProfile.license_plate || 'Not set'}
                          </span>
                          <button 
                            className="edit-icon"
                            onClick={() => startEditing('license_plate', dbUserProfile.license_plate)}
                            aria-label="Edit license plate"
                            title="Edit license plate"
                          >
                            <Icon name="edit" size={14} />
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="menu-item">
                      <strong>Status:</strong> 
                      <span className={`verification-status ${dbUserProfile.is_verified ? 'verified' : 'unverified'}`}>
                        {dbUserProfile.is_verified ? '✓ Verified User' : '⚠ Unverified'}
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
            <button className="menu-action-button" onClick={handleEditProfile}>
              Edit Profile
            </button>
            {dbUserProfile && !dbUserProfile.is_verified && (
              <button className="menu-action-button verify-button" onClick={handleVerifyIdentity}>
                <Icon name="lock" size={14} /> Get Verified
              </button>
            )}
            <button className="menu-action-button" onClick={handleReportLicensePlate}>
              Report License Plate
            </button>
            <button className="menu-action-button" onClick={handleAddParkingSpace}>
              Add New Parking Space
            </button>
            <button className="menu-action-button" onClick={() => { setIsOpen(false); navigate('/my-bookings'); }}>
              My Bookings
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