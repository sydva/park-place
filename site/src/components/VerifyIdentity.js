import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import apiService from '../services/api';
import './VerifyIdentity.css';

const VerifyIdentity = () => {
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState('');
  
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [idDocument, setIdDocument] = useState(null);
  const [vehicleRegistration, setVehicleRegistration] = useState(null);
  
  const navigate = useNavigate();
  const { user } = useUser();

  useEffect(() => {
    const fetchVerificationStatus = async () => {
      if (user?.primaryEmailAddress?.emailAddress) {
        try {
          const status = await apiService.getVerificationStatus(user.primaryEmailAddress.emailAddress);
          setVerificationStatus(status);
        } catch (error) {
          console.error('Failed to fetch verification status:', error);
          setError('Failed to load verification status');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchVerificationStatus();
  }, [user]);

  const handleFileChange = (e, setFile) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setError('Please select a JPEG, PNG, or PDF file');
        return;
      }
      
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setFile(file);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!profilePhoto || !idDocument || !vehicleRegistration) {
      setError('Please select all three required documents');
      return;
    }

    setUploading(true);
    setError('');

    try {
      await apiService.uploadVerificationDocuments(
        user.primaryEmailAddress.emailAddress,
        profilePhoto,
        idDocument,
        vehicleRegistration
      );
      
      setUploadSuccess(true);
      
      // Refresh verification status
      const status = await apiService.getVerificationStatus(user.primaryEmailAddress.emailAddress);
      setVerificationStatus(status);
      
    } catch (error) {
      console.error('Upload failed:', error);
      setError(error.message || 'Failed to upload documents. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'verified':
        return <span className="status-badge verified">✅ Verified</span>;
      case 'pending':
        return <span className="status-badge pending">⏳ Under Review</span>;
      case 'rejected':
        return <span className="status-badge rejected">❌ Rejected</span>;
      default:
        return <span className="status-badge not-started">⚠️ Not Started</span>;
    }
  };

  if (loading) {
    return (
      <div className="verify-identity-container">
        <div className="verify-identity-card">
          <div className="loading">Loading verification status...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="verify-identity-container">
      <div className="verify-identity-card">
        <div className="verify-identity-header">
          <button className="back-button" onClick={() => navigate(-1)}>
            ← Back
          </button>
          <h1>Identity Verification</h1>
          <p>Upload documents to get verified and access premium parking spots</p>
        </div>

        <div className="verify-identity-content">
          <div className="status-section">
            <h3>Current Status</h3>
            {getStatusBadge(verificationStatus?.status)}
            
            {verificationStatus?.status === 'verified' && (
              <div className="success-message">
                🎉 Congratulations! Your identity has been verified. You now have access to verified-only parking spaces.
              </div>
            )}
            
            {verificationStatus?.status === 'rejected' && verificationStatus?.verification_notes && (
              <div className="error-message">
                <strong>Rejection Reason:</strong> {verificationStatus.verification_notes}
              </div>
            )}
          </div>

          {verificationStatus?.status !== 'verified' && (
            <>
              <div className="requirements-section">
                <h3>Required Documents</h3>
                <div className="requirements-list">
                  <div className="requirement">
                    <span className="requirement-icon">📷</span>
                    <div>
                      <strong>Profile Photo</strong>
                      <p>Clear photo of yourself (selfie style)</p>
                    </div>
                  </div>
                  <div className="requirement">
                    <span className="requirement-icon">🆔</span>
                    <div>
                      <strong>Government ID</strong>
                      <p>Driver's license, passport, or state ID</p>
                    </div>
                  </div>
                  <div className="requirement">
                    <span className="requirement-icon">🚗</span>
                    <div>
                      <strong>Vehicle Registration</strong>
                      <p>Current vehicle registration document</p>
                    </div>
                  </div>
                </div>
              </div>

              {!uploadSuccess ? (
                <form onSubmit={handleSubmit} className="upload-form">
                  <div className="form-group">
                    <label htmlFor="profilePhoto">Profile Photo *</label>
                    <input
                      type="file"
                      id="profilePhoto"
                      accept="image/jpeg,image/jpg,image/png"
                      onChange={(e) => handleFileChange(e, setProfilePhoto)}
                      disabled={uploading}
                    />
                    {profilePhoto && <div className="file-selected">✓ {profilePhoto.name}</div>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="idDocument">Government ID Document *</label>
                    <input
                      type="file"
                      id="idDocument"
                      accept="image/jpeg,image/jpg,image/png,application/pdf"
                      onChange={(e) => handleFileChange(e, setIdDocument)}
                      disabled={uploading}
                    />
                    {idDocument && <div className="file-selected">✓ {idDocument.name}</div>}
                  </div>

                  <div className="form-group">
                    <label htmlFor="vehicleRegistration">Vehicle Registration *</label>
                    <input
                      type="file"
                      id="vehicleRegistration"
                      accept="image/jpeg,image/jpg,image/png,application/pdf"
                      onChange={(e) => handleFileChange(e, setVehicleRegistration)}
                      disabled={uploading}
                    />
                    {vehicleRegistration && <div className="file-selected">✓ {vehicleRegistration.name}</div>}
                  </div>

                  {error && <div className="error-message">{error}</div>}

                  <div className="form-actions">
                    <button 
                      type="submit" 
                      className="submit-button" 
                      disabled={uploading || !profilePhoto || !idDocument || !vehicleRegistration}
                    >
                      {uploading ? 'Uploading...' : 'Submit for Verification'}
                    </button>
                  </div>

                  <div className="info-text">
                    <p>
                      <strong>Privacy Notice:</strong> Your documents are encrypted and stored securely. 
                      They will only be used for identity verification purposes.
                    </p>
                    <p>
                      <strong>Processing Time:</strong> Verification typically takes 24-48 hours.
                    </p>
                  </div>
                </form>
              ) : (
                <div className="success-section">
                  <div className="success-message">
                    ✅ Documents uploaded successfully! Your submission is now under review.
                  </div>
                  <p>You'll receive a notification once your verification is complete.</p>
                  <button className="secondary-button" onClick={() => navigate('/')}>
                    Return to Map
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerifyIdentity;