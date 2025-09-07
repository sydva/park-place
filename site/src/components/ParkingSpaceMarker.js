import React from 'react';
import { Marker } from 'react-leaflet';
import L from 'leaflet';
import './ParkingSpaceMarker.css';

// Create custom parking space icons with neobrutalist game styling
const createParkingIcon = (space) => {
  const size = space.type === 'premium' ? 32 : 28;
  const baseColor = space.price === 0 ? '#4ECDC4' : space.type === 'premium' ? '#FF4757' : '#FFD700';
  const borderColor = '#000';
  const shadowOffset = 3;
  const displayText = space.requiresPayment ? '$' : 'P';
  
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size + shadowOffset}" height="${size + shadowOffset}" viewBox="0 0 ${size + shadowOffset} ${size + shadowOffset}">
      <!-- Shadow -->
      <circle cx="${size/2 + shadowOffset}" cy="${size/2 + shadowOffset}" r="${size/2 - 2}" fill="#000" opacity="1"/>
      <!-- Main circle -->
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 2}" fill="${baseColor}" stroke="${borderColor}" stroke-width="3"/>
      <!-- Text -->
      <text x="${size/2}" y="${size/2 + 2}" text-anchor="middle" dominant-baseline="middle" fill="${borderColor}" font-family="Arial, sans-serif" font-size="${size * 0.45}" font-weight="900">${displayText}</text>
    </svg>
  `;

  return new L.DivIcon({
    html: svgIcon,
    className: 'parking-space-marker',
    iconSize: [size + shadowOffset, size + shadowOffset],
    iconAnchor: [size/2, size/2],
  });
};

// Create price label for parking spaces with neobrutalist styling
const createPriceIcon = (space) => {
  const bgColor = space.price === 0 ? '#4ECDC4' : space.type === 'premium' ? '#FF4757' : '#FFD700';
  const borderColor = '#000';
  const shadowOffset = 4;
  const text = space.price === 0 ? 'FREE' : 
    space.paymentType === 'flat' ? `$${space.price}` : `$${space.price}/h`;
  
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${80 + shadowOffset} ${30 + shadowOffset}" style="transform: rotate(-2deg);">
      <!-- Shadow -->
      <rect x="${shadowOffset}" y="${shadowOffset}" width="80" height="30" fill="#000" opacity="1"/>
      <!-- Main rectangle -->
      <rect x="0" y="0" width="80" height="30" fill="${bgColor}" stroke="${borderColor}" stroke-width="4"/>
      <!-- Text -->
      <text x="40" y="21" text-anchor="middle" fill="${borderColor}" font-family="Arial, sans-serif" font-size="12" font-weight="900" text-transform="uppercase">${text}</text>
    </svg>
  `;

  return new L.DivIcon({
    html: svgIcon,
    className: 'parking-price-marker',
    iconSize: [80 + shadowOffset, 30 + shadowOffset],
    iconAnchor: [40, 15],
  });
};

const ParkingSpaceMarker = ({ space, showPrice = false, onClick }) => {
  const icon = showPrice 
    ? createPriceIcon(space)
    : createParkingIcon(space);

  const handleClick = () => {
    if (onClick) {
      onClick(space);
    }
  };

  return (
    <Marker
      position={[space.lat, space.lng]}
      icon={icon}
      eventHandlers={{
        click: handleClick,
      }}
    />
  );
};

export default ParkingSpaceMarker;