import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import apiService from '../services/api';
import './EditProfile.css';

const EditProfile = () => {
  const [formData, setFormData] = useState({
    username: '',
    licensePlate: '',
    licensePlateState: '',
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const { user } = useUser();

  const stateOptions = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      if (user?.primaryEmailAddress?.emailAddress) {
        try {
          const profile = await apiService.getUserProfileByEmail(user.primaryEmailAddress.emailAddress);
          if (profile) {
            setFormData({
              username: profile.username || '',
              licensePlate: profile.license_plate || '',
              licensePlateState: profile.license_plate_state || '',
            });
          }
        } catch (error) {
          console.error('Failed to fetch profile:', error);
          setError('Failed to load profile data');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchProfile();
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      const updateData = {
        email: user.primaryEmailAddress.emailAddress,
        name: formData.username.trim(),
        user_type: 'both', // Keep existing user type
        car_license_plate: formData.licensePlateState && formData.licensePlate ? 
          `${formData.licensePlateState}${formData.licensePlate}`.trim() : 
          formData.licensePlate.trim() || null,
      };

      await apiService.updateProfile(updateData);
      setSuccess(true);
      setTimeout(() => {
        navigate('/map');
      }, 1500);
    } catch (error) {
      console.error('Update failed:', error);
      setError(error.message || 'Failed to update profile. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const goBack = () => {
    navigate('/map');
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading profile...
      </div>
    );
  }

  return (
    <div className="edit-profile-container">
      <div className="edit-profile-card">
        <div className="edit-profile-header">
          <button className="back-button" onClick={goBack}>
            ← Back
          </button>
          <h1>Edit Profile</h1>
          <p>Update your username and license plate information</p>
        </div>

        <form onSubmit={handleSubmit} className="edit-profile-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Enter your username"
              maxLength="50"
            />
          </div>

          <div className="form-group">
            <label htmlFor="licensePlateState">License Plate State</label>
            <select
              id="licensePlateState"
              name="licensePlateState"
              value={formData.licensePlateState}
              onChange={handleInputChange}
            >
              <option value="">Select State</option>
              {stateOptions.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="licensePlate">License Plate Number</label>
            <input
              type="text"
              id="licensePlate"
              name="licensePlate"
              value={formData.licensePlate}
              onChange={handleInputChange}
              placeholder="Enter license plate number"
              maxLength="10"
              style={{ textTransform: 'uppercase' }}
            />
            <small className="form-help">
              Used for parking and violation reporting
            </small>
          </div>

          {success && (
            <div className="success-message">
              Profile updated successfully! Redirecting...
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button
              type="submit"
              className="update-button"
              disabled={submitting}
            >
              {submitting ? 'Updating...' : 'Update Profile'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditProfile;