import React, { useState } from 'react';
import StarRating from './StarRating';
import { getTagDisplay } from '../data/parkingTags';
import Icon from './Icon';
import StripePayment from './StripePayment';
import './ParkingSpaceModal.css';

const ParkingSpaceModal = ({ space, onClose, userLocation }) => {
  const [userRating, setUserRating] = useState(0);
  const [userComment, setUserComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [selectedHours, setSelectedHours] = useState(1);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  if (!space) return null;

  // Calculate distance from user location
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c * 1000; // Convert to meters
    return Math.round(distance);
  };

  const distance = userLocation 
    ? calculateDistance(userLocation[0], userLocation[1], space.lat, space.lng)
    : space.distance;

  const formatDistance = (meters) => {
    if (meters < 1000) {
      return `${meters}m away`;
    } else {
      return `${(meters / 1000).toFixed(1)}km away`;
    }
  };

  const formatPrice = (price, paymentType) => {
    if (price === 0) return 'Free';
    if (paymentType === 'flat') return `$${price}`;
    return `$${price}/hour`;
  };

  const calculateTotalPrice = () => {
    if (!space.requiresPayment) return 0;
    if (space.paymentType === 'flat') return space.price;
    return space.price * selectedHours;
  };

  const getTypeDisplay = (type) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };


  const handleSubmitRating = async () => {
    if (userRating === 0) return;
    
    setIsSubmitting(true);
    
    // Mock API call - replace with actual backend call
    console.log('Submitting rating:', {
      spaceId: space.id,
      rating: userRating,
      comment: userComment
    });
    
    // Simulate API delay
    setTimeout(() => {
      setIsSubmitting(false);
      setUserRating(0);
      setUserComment('');
      onClose();
    }, 1000);
  };

  const handleNavigate = () => {
    // Open Google Maps with directions to parking space
    const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${space.lat},${space.lng}&travelmode=driving`;
    window.open(googleMapsUrl, '_blank');
  };

  const handleReserveClick = () => {
    if (!space.requiresPayment) {
      // Handle free reservation
      console.log('Reserving free parking space:', space.id);
      setPaymentSuccess(true);
    } else {
      setShowPayment(true);
    }
  };

  const handlePaymentSuccess = (paymentResult) => {
    console.log('Payment successful:', paymentResult);
    setPaymentSuccess(true);
    setShowPayment(false);
  };

  const handlePaymentCancel = () => {
    setShowPayment(false);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Parking Space Details</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="space-info">
            <div className="info-row">
              <span className="label">Type:</span>
              <span className={`type-badge ${space.type}`}>
                {getTypeDisplay(space.type)}
              </span>
            </div>

            <div className="info-row">
              <span className="label">Price:</span>
              <span className="price">
                {formatPrice(space.price, space.paymentType)}
                {space.requiresPayment && space.paymentType === 'hourly' && space.maxHours && (
                  <span className="max-hours"> (max {space.maxHours}h)</span>
                )}
              </span>
            </div>

            <div className="info-row">
              <span className="label">Distance:</span>
              <span className="distance">{formatDistance(distance)}</span>
            </div>

            {space.timeLimit && (
              <div className="info-row">
                <span className="label">Time Limit:</span>
                <span className="time-limit">{space.timeLimit} minutes</span>
              </div>
            )}

            <div className="info-row">
              <span className="label">Rating:</span>
              <StarRating rating={space.rating} readonly={true} />
            </div>

            {space.features && space.features.length > 0 && (
              <div className="info-row">
                <span className="label">Features:</span>
                <div className="tags">
                  {space.features.map((tag, index) => {
                    const tagInfo = getTagDisplay(tag);
                    return (
                      <span key={index} className="tag">
                        <Icon name={tagInfo.icon} size={14} className="tag-icon" />
                        <span className="tag-label">{tagInfo.label}</span>
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {showPayment ? (
            <div className="payment-section">
              <h3>Reserve Parking Space</h3>
              {space.paymentType === 'hourly' && (
                <div className="hours-selector">
                  <label htmlFor="hours">Duration:</label>
                  <select 
                    id="hours" 
                    value={selectedHours} 
                    onChange={(e) => setSelectedHours(parseInt(e.target.value))}
                    className="hours-input"
                  >
                    {Array.from({length: space.maxHours || 8}, (_, i) => i + 1).map(hour => (
                      <option key={hour} value={hour}>{hour} hour{hour > 1 ? 's' : ''}</option>
                    ))}
                  </select>
                </div>
              )}
              <StripePayment
                amount={calculateTotalPrice()}
                onSuccess={handlePaymentSuccess}
                onCancel={handlePaymentCancel}
                parkingSpace={space}
                selectedHours={selectedHours}
              />
            </div>
          ) : paymentSuccess ? (
            <div className="success-section">
              <div className="success-message">
                <Icon name="check" size={24} />
                <h3>Reservation Confirmed!</h3>
                <p>Your parking space has been reserved successfully.</p>
                {space.requiresPayment && (
                  <p>You have reserved this space for {space.paymentType === 'hourly' ? `${selectedHours} hour${selectedHours > 1 ? 's' : ''}` : 'unlimited time'}.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="rating-section">
              <h3>Rate this parking space</h3>
              <div className="user-rating">
                <StarRating 
                  rating={userRating} 
                  onRatingChange={setUserRating}
                  size="large"
                />
              </div>
              
              <textarea
                className="comment-input"
                placeholder="Add a comment (optional)..."
                value={userComment}
                onChange={(e) => setUserComment(e.target.value)}
                maxLength={200}
                rows={3}
              />
              
              <button 
                className="submit-rating-button"
                onClick={handleSubmitRating}
                disabled={userRating === 0 || isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Rating'}
              </button>
            </div>
          )}
        </div>

        {!showPayment && (
          <div className="modal-footer">
            <div className="footer-buttons">
              <button className="navigate-button" onClick={handleNavigate}>
                <Icon name="navigation" size={16} />
                Navigate Here
              </button>
              {!paymentSuccess && (
                <button className="reserve-button" onClick={handleReserveClick}>
                  <Icon name={space.requiresPayment ? "dollar" : "check"} size={16} />
                  {space.requiresPayment ? 
                    `Reserve - $${calculateTotalPrice().toFixed(2)}` : 
                    'Reserve (Free)'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParkingSpaceModal;