import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import apiService from '../services/api';
import './CompleteRegistration.css';

const CompleteRegistration = ({ onComplete }) => {
  const [formData, setFormData] = useState({
    username: '',
    userType: 'parker', // Default to parker
    licensePlate: '',
    licensePlateState: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useUser();
  const navigate = useNavigate();

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

    if (!formData.username.trim()) {
      setError('Username is required');
      setSubmitting(false);
      return;
    }

    if (formData.userType === 'parker' && !formData.licensePlate.trim()) {
      setError('License plate is required for parkers');
      setSubmitting(false);
      return;
    }

    try {
      const registrationData = {
        email: user.primaryEmailAddress.emailAddress,
        name: formData.username.trim(),
        user_type: formData.userType,
        car_license_plate: formData.userType === 'parker' ? 
          `${formData.licensePlateState}${formData.licensePlate}`.trim() : null,
      };

      await apiService.register(registrationData);
      
      // Registration successful
      if (onComplete) {
        onComplete();
      } else {
        navigate('/map');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      setError(error.message || 'Registration failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const stateOptions = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ];

  return (
    <div className="complete-registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <h1>Complete Your Registration</h1>
          <p>Welcome to Park Place! We need a few more details to get you started.</p>
          <div className="user-info">
            <strong>Signed in as:</strong> {user?.primaryEmailAddress?.emailAddress}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Enter your username"
              maxLength="50"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="userType">I want to *</label>
            <select
              id="userType"
              name="userType"
              value={formData.userType}
              onChange={handleInputChange}
              required
            >
              <option value="parker">Find parking spaces (Parker)</option>
              <option value="provider">List my parking spaces (Provider)</option>
              <option value="both">Both find and list parking</option>
            </select>
          </div>

          {(formData.userType === 'parker' || formData.userType === 'both') && (
            <>
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
                <label htmlFor="licensePlate">License Plate Number *</label>
                <input
                  type="text"
                  id="licensePlate"
                  name="licensePlate"
                  value={formData.licensePlate}
                  onChange={handleInputChange}
                  placeholder="Enter license plate number"
                  maxLength="10"
                  style={{ textTransform: 'uppercase' }}
                  required
                />
                <small className="form-help">
                  Required for parking and reporting violations
                </small>
              </div>
            </>
          )}

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button
              type="submit"
              className="register-button"
              disabled={submitting}
            >
              {submitting ? 'Creating Account...' : 'Complete Registration'}
            </button>
          </div>
        </form>

        <div className="registration-footer">
          <p>By completing registration, you agree to our terms of service and privacy policy.</p>
        </div>
      </div>
    </div>
  );
};

export default CompleteRegistration;