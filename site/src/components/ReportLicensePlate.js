import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import Icon from './Icon';
import apiService from '../services/api';
import './ReportLicensePlate.css';

const ReportLicensePlate = () => {
  const [licensePlate, setLicensePlate] = useState('');
  const [capturedImage, setCapturedImage] = useState(null);
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const { user } = useUser();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!licensePlate.trim()) {
      setError('Please enter a license plate number');
      return;
    }

    setSubmitting(true);
    setError(null);
    
    try {
      const reportData = {
        license_plate: licensePlate.trim().toUpperCase(),
        description: description.trim() || 'License plate violation reported',
        reporter_email: user?.primaryEmailAddress?.emailAddress || null,
        space_id: null // Could be enhanced to allow reporting for specific spaces
      };

      await apiService.reportLicensePlate(reportData);
      console.log('License plate reported successfully!');
      navigate('/map');
    } catch (error) {
      console.error('Error reporting license plate:', error);
      setError(error.message || 'Failed to submit report. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleImageCapture = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraClick = () => {
    fileInputRef.current.click();
  };

  const goBack = () => {
    navigate('/map');
  };

  return (
    <div className="report-container">
      <div className="report-header">
        <button className="back-button" onClick={goBack}>
          ← Back
        </button>
        <h1>Report License Plate</h1>
      </div>

      <form onSubmit={handleSubmit} className="report-form">
        <div className="input-section">
          <h2>Enter License Plate Number</h2>
          <input
            type="text"
            value={licensePlate}
            onChange={(e) => setLicensePlate(e.target.value.toUpperCase())}
            placeholder="ABC-123"
            className="license-input"
            maxLength="10"
          />
        </div>

        <div className="input-section">
          <h2>Description (Optional)</h2>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the violation (e.g., parked illegally, blocking space, etc.)"
            className="description-input"
            rows="3"
            maxLength="200"
          />
        </div>

        <div className="divider"></div>

        <div className="camera-section">
          <h2>Take a Photo</h2>
          <button
            type="button"
            className="camera-button"
            onClick={handleCameraClick}
          >
            <Icon name="camera" size={18} />
            Capture Photo
          </button>
          <input
            type="file"
            accept="image/*"
            capture="environment"
            ref={fileInputRef}
            onChange={handleImageCapture}
            style={{ display: 'none' }}
          />
          
          {capturedImage && (
            <div className="image-preview">
              <img src={capturedImage} alt="Captured license plate" />
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          type="submit"
          className="submit-button"
          disabled={!licensePlate.trim() || submitting}
        >
          {submitting ? 'Submitting Report...' : 'Submit Report'}
        </button>
      </form>
    </div>
  );
};

export default ReportLicensePlate;