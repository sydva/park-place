import React from 'react';
import { Marker } from 'react-leaflet';
import L from 'leaflet';
import './ParkingSpaceMarker.css';

// Create custom parking space icons
const createParkingIcon = (space) => {
  const size = space.type === 'premium' ? 26 : 22;
  const baseColor = space.price === 0 ? '#4CAF50' : space.type === 'premium' ? '#FF6B35' : '#2196F3';
  const textColor = '#FFFFFF';
  const hasPayment = space.requiresPayment;
  
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 1}" fill="${baseColor}" stroke="#FFFFFF" stroke-width="2"/>
      <text x="${size/2}" y="${size/2 + 1}" text-anchor="middle" dominant-baseline="middle" fill="${textColor}" font-family="Arial, sans-serif" font-size="${size * 0.5}" font-weight="bold">P</text>
      ${hasPayment ? `<circle cx="${size - 4}" cy="4" r="3" fill="#FFD700" stroke="#FFFFFF" stroke-width="1"/>
      <text x="${size - 4}" y="6" text-anchor="middle" dominant-baseline="middle" fill="#000" font-family="Arial, sans-serif" font-size="5" font-weight="bold">$</text>` : ''}
    </svg>
  `;

  return new L.DivIcon({
    html: svgIcon,
    className: 'parking-space-marker',
    iconSize: [size, size],
    iconAnchor: [size/2, size/2],
  });
};

// Create price label for parking spaces
const createPriceIcon = (space) => {
  const bgColor = space.price === 0 ? '#4CAF50' : space.type === 'premium' ? '#FF6B35' : '#2196F3';
  const text = space.price === 0 ? 'FREE' : 
    space.paymentType === 'flat' ? `$${space.price}` : `$${space.price}/h`;
  
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 70 24">
      <rect x="0" y="0" width="70" height="24" rx="12" fill="${bgColor}" stroke="#FFFFFF" stroke-width="2"/>
      <text x="35" y="16" text-anchor="middle" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="10" font-weight="bold">${text}</text>
      ${space.requiresPayment ? `<circle cx="62" cy="6" r="4" fill="#FFD700" stroke="#FFFFFF" stroke-width="1"/>
      <text x="62" y="8" text-anchor="middle" dominant-baseline="middle" fill="#000" font-family="Arial, sans-serif" font-size="6" font-weight="bold">$</text>` : ''}
    </svg>
  `;

  return new L.DivIcon({
    html: svgIcon,
    className: 'parking-price-marker',
    iconSize: [70, 24],
    iconAnchor: [35, 12],
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