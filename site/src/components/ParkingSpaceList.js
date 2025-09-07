import React from 'react';
import { getTagDisplay } from '../data/parkingTags';
import StarRating from './StarRating';
import Icon from './Icon';
import './ParkingSpaceList.css';

const ParkingSpaceListItem = ({ space, userLocation, onSpaceClick, onSpaceSelect }) => {
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
      return `${meters}m`;
    } else {
      return `${(meters / 1000).toFixed(1)}km`;
    }
  };

  const formatPrice = (space) => {
    if (space.price === 0) return 'Free';
    if (space.paymentType === 'flat') return `$${space.price}`;
    return `$${space.price}/hr`;
  };

  const getTypeColor = (type) => {
    const colors = {
      premium: '#FF6B35',
      standard: '#2196F3',
      basic: '#4CAF50'
    };
    return colors[type] || '#666';
  };

  return (
    <div className="parking-space-item" onClick={() => onSpaceClick(space)}>
      <div className="space-header">
        <div className="space-type-price">
          <span 
            className="space-type-dot" 
            style={{ backgroundColor: getTypeColor(space.type) }}
          ></span>
          <span className="space-price">
            {formatPrice(space)}
            {space.requiresPayment && <Icon name="dollar" size={12} className="payment-indicator" />}
            {space.requiresVerification && <Icon name="check" size={12} className="verification-indicator" />}
          </span>
        </div>
        <div className="space-distance">{formatDistance(distance)}</div>
      </div>
      
      <div className="space-rating">
        <StarRating rating={space.rating} readonly={true} size="small" />
      </div>
      
      {space.features && space.features.length > 0 && (
        <div className="space-features">
          {space.features.slice(0, 3).map((tagId, index) => {
            const tagInfo = getTagDisplay(tagId);
            return (
              <span key={index} className="feature-tag">
                <Icon name={tagInfo.icon} size={12} />
                <span className="feature-label">{tagInfo.label}</span>
              </span>
            );
          })}
          {space.features.length > 3 && (
            <span className="more-features">+{space.features.length - 3}</span>
          )}
        </div>
      )}
    </div>
  );
};

const ParkingSpaceList = ({ 
  spaces = [], 
  userLocation, 
  onSpaceClick, 
  onSpaceSelect,
  isVisible = true,
  onToggle,
  isUserVerified = false,
  spaceCounts = null
}) => {
  // Filter and sort spaces based on user verification status
  const visibleSpaces = isUserVerified 
    ? spaces 
    : spaces.filter(space => !space.requiresVerification);
  
  // Use spaceCounts prop if available, otherwise fall back to calculating from spaces
  const hiddenCount = spaceCounts && !isUserVerified 
    ? spaceCounts.verified_only_spaces 
    : (isUserVerified ? 0 : spaces.filter(space => space.requiresVerification).length);

  const sortedSpaces = userLocation 
    ? [...visibleSpaces].sort((a, b) => {
        const distA = Math.sqrt(Math.pow(a.lat - userLocation[0], 2) + Math.pow(a.lng - userLocation[1], 2));
        const distB = Math.sqrt(Math.pow(b.lat - userLocation[0], 2) + Math.pow(b.lng - userLocation[1], 2));
        return distA - distB;
      })
    : visibleSpaces;

  return (
    <div className={`parking-space-list ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="list-header">
        <div className="list-title">
          <h3>Nearby Parking</h3>
          <div className="space-counts">
            <span className="space-count">{sortedSpaces.length} spaces</span>
            {hiddenCount > 0 && (
              <span className="additional-count">
                +{hiddenCount} more with verification
              </span>
            )}
          </div>
        </div>
        <button className="toggle-list-btn" onClick={onToggle}>
          {isVisible ? '▼' : '▲'}
        </button>
      </div>
      
      <div className="list-content">
        {sortedSpaces.length === 0 ? (
          <div className="no-spaces">
            <p>No parking spaces found</p>
            <p className="no-spaces-subtitle">Try adjusting your filters or zooming out</p>
          </div>
        ) : (
          <div className="spaces-grid">
            {sortedSpaces.map((space) => (
              <ParkingSpaceListItem
                key={space.id}
                space={space}
                userLocation={userLocation}
                onSpaceClick={onSpaceClick}
                onSpaceSelect={onSpaceSelect}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ParkingSpaceList;