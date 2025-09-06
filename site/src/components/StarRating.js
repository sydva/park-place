import React, { useState } from 'react';
import './StarRating.css';

const StarRating = ({ rating, onRatingChange, readonly = false, size = 'medium' }) => {
  const [hoverRating, setHoverRating] = useState(0);
  
  const handleStarClick = (starValue) => {
    if (!readonly && onRatingChange) {
      onRatingChange(starValue);
    }
  };

  const handleStarHover = (starValue) => {
    if (!readonly) {
      setHoverRating(starValue);
    }
  };

  const handleMouseLeave = () => {
    setHoverRating(0);
  };

  const getStarClass = (starIndex) => {
    const currentRating = hoverRating || rating;
    let className = `star ${size}`;
    
    if (starIndex <= currentRating) {
      className += ' filled';
    } else if (starIndex - 0.5 <= currentRating) {
      className += ' half-filled';
    }
    
    if (!readonly) {
      className += ' interactive';
    }
    
    return className;
  };

  return (
    <div className="star-rating" onMouseLeave={handleMouseLeave}>
      {[1, 2, 3, 4, 5].map((starIndex) => (
        <span
          key={starIndex}
          className={getStarClass(starIndex)}
          onClick={() => handleStarClick(starIndex)}
          onMouseEnter={() => handleStarHover(starIndex)}
        >
          ★
        </span>
      ))}
      {rating > 0 && (
        <span className="rating-text">
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
};

export default StarRating;