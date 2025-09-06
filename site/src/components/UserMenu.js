import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserMenu.css';

const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  
  // Mock user data - ready for backend integration
  const userData = {
    username: 'JohnDoe',
    rating: 1247,
    licensePlate: 'ABC-123'
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    // Ready for backend logout logic
    console.log('Logout clicked');
    setIsOpen(false);
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
            <div className="menu-item">
              <strong>Username:</strong> {userData.username}
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
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;