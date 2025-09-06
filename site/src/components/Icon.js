import React from 'react';
import './Icon.css';
import {
  MdSecurity,
  MdLock,
  MdVideocam,
  MdPerson,
  MdEvStation,
  MdRoomService,
  MdLocalCarWash,
  MdWc,
  MdAccessible,
  MdZoomOutMap,
  MdDirectionsCar,
  MdLocalShipping,
  MdTwoWheeler,
  MdWbSunny,
  MdLogin,
  MdFilterList,
  MdNavigation,
  MdPhotoCamera,
  MdCreditCard,
  MdAttachMoney,
  MdCheck,
  MdLocationOn,
  MdHome,
  MdTerrain,
  MdArrowDownward,
  MdRoofing,
  MdLocalOffer,
  MdSearch,
  MdEdit
} from 'react-icons/md';

// Icon components using Material Design icons via react-icons
const IconComponents = {
  // Location & Access
  covered: MdHome,
  ground_level: MdTerrain,
  underground: MdArrowDownward,
  rooftop: MdRoofing,

  // Security
  security: MdSecurity,
  gated: MdLock,
  lock: MdLock,
  camera_monitored: MdVideocam,
  attended: MdPerson,

  // Amenities
  ev_charging: MdEvStation,
  valet: MdRoomService,
  car_wash: MdLocalCarWash,
  restrooms: MdWc,

  // Accessibility
  accessible: MdAccessible,
  wide_spaces: MdZoomOutMap,

  // Vehicle Types
  compact_only: MdDirectionsCar,
  oversized_ok: MdLocalShipping,
  motorcycle: MdTwoWheeler,

  // Features
  well_lit: MdWbSunny,
  near_entrance: MdLogin,
  ventilated: MdZoomOutMap,

  // Payment & Status
  'credit-card': MdCreditCard,
  dollar: MdAttachMoney,
  check: MdCheck,

  // Map & UI
  'map-pin': MdLocationOn,
  filter: MdFilterList,
  navigation: MdNavigation,
  camera: MdPhotoCamera,
  tag: MdLocalOffer,
  search: MdSearch,
  edit: MdEdit
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