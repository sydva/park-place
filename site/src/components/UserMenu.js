import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useUser, useClerk, SignInButton } from '@clerk/clerk-react';
import apiService from '../services/api';
import './UserMenu.css';
import Icon from './Icon';
import NotificationsModal from './NotificationsModal';
import { usePreferences } from '../contexts/PreferencesContext';

const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [dbUserProfile, setDbUserProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [editingField, setEditingField] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [editState, setEditState] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const navigate = useNavigate();
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();
  const { unitsPreference, setUnitsPreference } = usePreferences();

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

  const handleVerifyIdentity = () => {
    setIsOpen(false);
    navigate('/verify-identity');
  };

  const startEditing = (field, currentValue) => {
    setEditingField(field);
    if (field === 'license_plate' && currentValue) {
      // Parse existing license plate to separate state and number
      const state = currentValue.length >= 2 ? currentValue.substring(0, 2) : '';
      const number = currentValue.length >= 2 ? currentValue.substring(2) : currentValue;
      setEditState(state);
      setEditValue(number);
    } else {
      setEditValue(currentValue || '');
      setEditState('');
    }
  };

  const cancelEditing = () => {
    setEditingField(null);
    setEditValue('');
    setEditState('');
  };

  const handleUnitsToggle = async () => {
    const newUnits = unitsPreference === 'imperial' ? 'metric' : 'imperial';
    try {
      await setUnitsPreference(newUnits);
    } catch (error) {
      console.error('Failed to update units preference:', error);
    }
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
        const fullPlate = editState && editValue ? `${editState}${editValue}`.trim() : editValue.trim();
        updateData.car_license_plate = fullPlate || null;
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
        MENU
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <div className="menu-dropdown">
          <div className="menu-backdrop" onClick={toggleMenu}></div>
          <div className="menu-content">
            {!isLoaded ? (
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
                        <div className="inline-edit license-edit">
                          <select
                            value={editState}
                            onChange={(e) => setEditState(e.target.value)}
                            className="edit-select"
                          >
                            <option value="">State</option>
                            {['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'].map(state => (
                              <option key={state} value={state}>{state}</option>
                            ))}
                          </select>
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
                            {dbUserProfile.license_plate ?
                              `${dbUserProfile.license_plate_state || ''}${dbUserProfile.license_plate_state ? '-' : ''}${dbUserProfile.license_plate}` :
                              'Not set'}
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
                    <div className="menu-item status-item">
                      <strong>Status:</strong>
                      <span className={`verification-status ${dbUserProfile.is_verified ? 'verified' : 'unverified'}`}>
                        {dbUserProfile.is_verified ? '✓ Verified User' : '⚠ Unverified'}
                      </span>
                      {!dbUserProfile.is_verified && (
                        <button className="verify-inline-button" onClick={handleVerifyIdentity}>
                          <Icon name="lock" size={12} /> Verify
                        </button>
                      )}
                    </div>
                    <div className="menu-item toggle-item">
                      <strong>Distance Units:</strong>
                      <div className="units-toggle">
                        <span className={unitsPreference === 'imperial' ? 'active' : ''}>
                          Feet/Miles
                        </span>
                        <button
                          className="toggle-switch"
                          onClick={handleUnitsToggle}
                          aria-label={`Switch to ${unitsPreference === 'imperial' ? 'metric' : 'imperial'} units`}
                        >
                          <div className={`toggle-slider ${unitsPreference}`}></div>
                        </button>
                        <span className={unitsPreference === 'metric' ? 'active' : ''}>
                          Meters/Km
                        </span>
                      </div>
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
                {/* Authenticated actions */}
                <button className="menu-action-button" onClick={() => setShowNotifications(true)}>
                  Messages {unreadCount > 0 ? `(${unreadCount})` : ''}
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
                <button className="logout-button" onClick={handleLogout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <div className="menu-item">Not signed in</div>
                <SignInButton mode="modal">
                  <button className="menu-action-button">Sign In</button>
                </SignInButton>
              </>
            )}
            <div className="menu-footer">
              <Link to="/terms">Terms</Link>
              ·
              <Link to="/privacy">Privacy</Link>
            </div>
          </div>
        </div>
      )}

      {showNotifications && user?.primaryEmailAddress?.emailAddress && (
        <NotificationsModal 
          email={user.primaryEmailAddress.emailAddress} 
          onClose={() => {
            setShowNotifications(false);
            // Optionally refresh unread count after closing
            apiService.getUnreadCount(user.primaryEmailAddress.emailAddress)
              .then((c) => setUnreadCount(c.unread_count))
              .catch(() => {});
          }}
        />
      )}
    </div>
  );
};

export default UserMenu;
