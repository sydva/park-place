import React from 'react';
import { Marker } from 'react-leaflet';
import L from 'leaflet';
import './ParkingSpaceMarker.css';

// Create custom parking space icons
const createParkingIcon = (type, price) => {
  const size = type === 'premium' ? 24 : 20;
  const color = price === 0 ? '#4CAF50' : type === 'premium' ? '#FF6B35' : '#2196F3';
  const textColor = '#FFFFFF';
  
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 1}" fill="${color}" stroke="#FFFFFF" stroke-width="2"/>
      <text x="${size/2}" y="${size/2 + 1}" text-anchor="middle" dominant-baseline="middle" fill="${textColor}" font-family="Arial, sans-serif" font-size="${size * 0.6}" font-weight="bold">P</text>
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
const createPriceIcon = (price, type) => {
  const bgColor = price === 0 ? '#4CAF50' : type === 'premium' ? '#FF6B35' : '#2196F3';
  const text = price === 0 ? 'FREE' : `$${price}`;
  
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 24">
      <rect x="0" y="0" width="60" height="24" rx="12" fill="${bgColor}" stroke="#FFFFFF" stroke-width="2"/>
      <text x="30" y="16" text-anchor="middle" fill="#FFFFFF" font-family="Arial, sans-serif" font-size="11" font-weight="bold">${text}</text>
    </svg>
  `;

  return new L.DivIcon({
    html: svgIcon,
    className: 'parking-price-marker',
    iconSize: [60, 24],
    iconAnchor: [30, 12],
  });
};

const ParkingSpaceMarker = ({ space, showPrice = false, onClick }) => {
  const icon = showPrice 
    ? createPriceIcon(space.price, space.type)
    : createParkingIcon(space.type, space.price);

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