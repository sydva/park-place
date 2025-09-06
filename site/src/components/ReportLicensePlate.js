import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './ReportLicensePlate.css';

const ReportLicensePlate = () => {
  const [licensePlate, setLicensePlate] = useState('');
  const [capturedImage, setCapturedImage] = useState(null);
  const [useCamera, setUseCamera] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Ready for backend integration
    console.log('Reporting license plate:', licensePlate);
    console.log('Image:', capturedImage);
    
    // Navigate back to map after submission
    navigate('/map');
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

        <div className="divider">OR</div>

        <div className="camera-section">
          <h2>Take a Photo</h2>
          <button
            type="button"
            className="camera-button"
            onClick={handleCameraClick}
          >
            📷 Capture Photo
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

        <button
          type="submit"
          className="submit-button"
          disabled={!licensePlate && !capturedImage}
        >
          Submit Report
        </button>
      </form>
    </div>
  );
};

export default ReportLicensePlate;