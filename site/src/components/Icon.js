import React from 'react';
import './Icon.css';

// SVG icon components using clean, professional icons
const IconComponents = {
  // Location & Access
  covered: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/>
    </svg>
  ),
  
  ground_level: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
  ),
  
  underground: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
    </svg>
  ),
  
  rooftop: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2l-5.5 9h11z"/>
      <path d="M17.5 17c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5z"/>
      <path d="M3 13h18v6H3z"/>
    </svg>
  ),

  // Security
  security: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16V13C8,12.4 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
    </svg>
  ),
  
  gated: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M6 19h3v-6h6v6h3v-9l-6-4.5L6 10v9zm12 2H6a1 1 0 01-1-1V10a1 1 0 01.4-.8l6-4.5a1 1 0 011.2 0l6 4.5a1 1 0 01.4.8v10a1 1 0 01-1 1z"/>
    </svg>
  ),
  
  camera_monitored: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4zM14 13c0 .55-.45 1-1 1H5c-.55 0-1-.45-1-1v-2c0-.55.45-1 1-1h8c.55 0 1 .45 1 1v2z"/>
    </svg>
  ),
  
  attended: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 6c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2m0 10c2.7 0 5.8 1.29 6 2H6c.23-.72 3.31-2 6-2m0-12C9.79 4 8 5.79 8 8s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 10c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>
  ),

  // Amenities
  ev_charging: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M14.5 11l-3 6v-4h-2l3-6v4h2zm3.5-6h-2V3h-2v2h-1.5C11.11 5 10 6.11 10 7.5v11c0 1.39 1.11 2.5 2.5 2.5h1v-13h4V5zm2 5V8.5C20 7.11 18.89 6 17.5 6H16v2h1.5v2.5H16V13h1.5v2.5H16V18h1.5c1.39 0 2.5-1.11 2.5-2.5V13h-1.5v-2.5H20z"/>
    </svg>
  ),
  
  valet: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.65 10C11.83 7.67 9.61 6 7 6c-3.31 0-6 2.69-6 6s2.69 6 6 6c2.61 0 4.83-1.67 5.65-4H17v4h4v-4h2v-4h-8.35zM7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
    </svg>
  ),
  
  car_wash: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M17 8.5c0 1.38-1.12 2.5-2.5 2.5S12 9.88 12 8.5s1.12-2.5 2.5-2.5S17 7.12 17 8.5zm-8.5 0C8.5 7.12 7.38 6 6 6S3.5 7.12 3.5 8.5 4.62 11 6 11s2.5-1.12 2.5-2.5zM6 18c0-1.1.9-2 2-2h8c1.1 0 2 .9 2 2v1H6v-1z"/>
      <path d="M19 12H5l-.6 8h15.2L19 12z"/>
    </svg>
  ),
  
  restrooms: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M5.5 22v-7.5H4V9c0-1.1.9-2 2-2h3c1.1 0 2 .9 2 2v5.5H9.5V22h-4zM18 22v-6h1.5l-2.54-7.63A1.5 1.5 0 0015.54 7h-.08c-.8 0-1.54.5-1.85 1.37L11.07 16H12.5v6H18z"/>
      <circle cx="7.5" cy="4.5" r="2.5"/>
      <circle cx="15.5" cy="4.5" r="2.5"/>
    </svg>
  ),

  // Accessibility
  accessible: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm9 7h-6v13h-2v-6h-2v6H9V9H3V7h18v2z"/>
    </svg>
  ),
  
  wide_spaces: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M9 11H7l-4-4 4-4h2v3h6V3h2l4 4-4 4h-2V8H9v3z"/>
    </svg>
  ),

  // Vehicle Types
  compact_only: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
    </svg>
  ),
  
  oversized_ok: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
    </svg>
  ),
  
  motorcycle: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M19.44 9.03L15.41 5H11v2h3.59l2 2H5c-2.8 0-5 2.2-5 5s2.2 5 5 5c2.46 0 4.45-1.69 4.9-4h1.65l2.77-2.77c-.21-.54-.32-1.14-.32-1.75 0-.58.1-1.13.25-1.65L12.6 9.5c-.22-.22-.22-.58 0-.8L14.5 7c.22-.22.58-.22.8 0l1.48 1.48L18 7.35c.8-.8 2.07-.8 2.87 0 .8.8.8 2.07 0 2.87l-1.43 1.43zm-1.91 2.53c-.8.8-2.07.8-2.87 0-.8-.8-.8-2.07 0-2.87.8-.8 2.07-.8 2.87 0 .8.8.8 2.07 0 2.87z"/>
    </svg>
  ),

  // Features
  well_lit: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"/>
    </svg>
  ),
  
  near_entrance: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z"/>
    </svg>
  ),
  
  ventilated: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M14.5 17c0 1.65-1.35 3-3 3-.96 0-1.84-.49-2.35-1.3l-.78.78C9.14 20.72 10.13 21.5 11.5 21.5c2.76 0 5-2.24 5-5 0-1.37-.78-2.36-2.02-3.13l-.78.78c.81.51 1.3 1.39 1.3 2.35z"/>
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
  )
};

const Icon = ({ name, size = 16, className = '' }) => {
  const IconComponent = IconComponents[name];
  
  if (!IconComponent) {
    // Fallback for unknown icons
    return <span className={`icon-fallback ${className}`}>•</span>;
  }

  return (
    <span 
      className={`icon ${className}`} 
      style={{ width: size, height: size }}
    >
      <IconComponent />
    </span>
  );
};

export default Icon;