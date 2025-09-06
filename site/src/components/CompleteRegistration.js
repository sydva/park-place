import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import apiService from '../services/api';
import './CompleteRegistration.css';

const CompleteRegistration = ({ onComplete }) => {
  const [formData, setFormData] = useState({
    username: '',
    licensePlate: '',
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

    if (!formData.licensePlate.trim()) {
      setError('License plate is required');
      setSubmitting(false);
      return;
    }

    try {
      const registrationData = {
        email: user.primaryEmailAddress.emailAddress,
        name: formData.username.trim(),
        user_type: 'parker',
        car_license_plate: formData.licensePlate.trim(),
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
      let errorMessage = 'Registration failed. Please try again.';
      
      if (error && typeof error === 'object') {
        if (error.message) {
          errorMessage = error.message;
        } else if (error.detail) {
          errorMessage = error.detail;
        } else {
          errorMessage = JSON.stringify(error);
        }
      } else if (typeof error === 'string') {
        errorMessage = error;
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

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
            <label htmlFor="licensePlate">License Plate *</label>
              <input
                type="text"
                id="licensePlate"
                name="licensePlate"
                value={formData.licensePlate}
                onChange={handleInputChange}
                placeholder="Enter license plate"
                maxLength="10"
                style={{ textTransform: 'uppercase' }}
                required
              />
              <small className="form-help">
                Required for parking and reporting violations
              </small>
            </div>

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
          <p>
            By completing registration, you agree to our <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy Policy</Link>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CompleteRegistration;