import React, { useState } from 'react';
import StarRating from './StarRating';
import { getTagDisplay } from '../data/parkingTags';
import './ParkingSpaceModal.css';

const ParkingSpaceModal = ({ space, onClose, userLocation }) => {
  const [userRating, setUserRating] = useState(0);
  const [userComment, setUserComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const formatPrice = (price) => {
    if (price === 0) return 'Free';
    return `$${price}/hour`;
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
              <span className="price">{formatPrice(space.price)}</span>
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
                  {space.features.map((tag, index) => (
                    <span key={index} className="tag">
                      {getTagDisplay(tag)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

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
        </div>

        <div className="modal-footer">
          <div className="footer-buttons">
            <button className="navigate-button" onClick={handleNavigate}>
              🧭 Navigate Here
            </button>
            <button className="reserve-button">
              Reserve This Spot
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParkingSpaceModal;