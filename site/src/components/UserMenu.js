import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionContext } from 'supertokens-auth-react/recipe/session';
import { signOut } from 'supertokens-auth-react/recipe/session';
import './UserMenu.css';

const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const session = useSessionContext();
  
  // Mock user data - will be replaced with real user data from backend
  const userData = {
    username: session.doesSessionExist ? session.userId?.substring(0, 8) || 'User' : 'Guest',
    rating: 1247,
    licensePlate: 'ABC-123'
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = async () => {
    await signOut();
    setIsOpen(false);
    navigate('/');
  };

  const handleReportLicensePlate = () => {
    setIsOpen(false);
    navigate('/report-license-plate');
  };

  const handleAddParkingSpace = () => {
    setIsOpen(false);
    navigate('/add-parking-space');
  };

  if (!session.doesSessionExist) {
    return null; // Don't show menu if user is not logged in
  }

  return (
    <div className="user-menu-container">
      <button className="menu-button" onClick={toggleMenu}>
        ☰
      </button>
      
      {isOpen && (
        <div className="menu-dropdown">
          <div className="menu-backdrop" onClick={toggleMenu}></div>
          <div className="menu-content">
            <div className="menu-item">
              <strong>User ID:</strong> {userData.username}
            </div>
            <div className="menu-item">
              <strong>Rating:</strong> {userData.rating}
            </div>
            <div className="menu-item">
              <strong>License Plate:</strong> {userData.licensePlate}
            </div>
            <button className="menu-action-button" onClick={handleReportLicensePlate}>
              Report License Plate
            </button>
            <button className="menu-action-button" onClick={handleAddParkingSpace}>
              Add New Parking Space
            </button>
            <button className="logout-button" onClick={handleLogout}>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;