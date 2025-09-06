// Standardized parking space tags with categories, icons, and descriptions
export const PARKING_TAGS = {
  // Location/Access
  covered: {
    id: 'covered',
    label: 'Covered',
    icon: '🏠',
    category: 'location',
    description: 'Protected from weather'
  },
  ground_level: {
    id: 'ground_level',
    label: 'Ground Level',
    icon: '🏢',
    category: 'location',
    description: 'No stairs or elevators needed'
  },
  underground: {
    id: 'underground',
    label: 'Underground',
    icon: '🚇',
    category: 'location',
    description: 'Below ground level'
  },
  rooftop: {
    id: 'rooftop',
    label: 'Rooftop',
    icon: '🏙️',
    category: 'location',
    description: 'Top floor parking'
  },
  
  // Security
  security: {
    id: 'security',
    label: 'Security',
    icon: '🔒',
    category: 'security',
    description: 'Monitored or gated parking'
  },
  gated: {
    id: 'gated',
    label: 'Gated',
    icon: '🚪',
    category: 'security',
    description: 'Access controlled entry'
  },
  camera_monitored: {
    id: 'camera_monitored',
    label: 'Camera Monitored',
    icon: '📹',
    category: 'security',
    description: 'CCTV surveillance'
  },
  attended: {
    id: 'attended',
    label: 'Attended',
    icon: '👮',
    category: 'security',
    description: 'Staff on site'
  },
  
  // Amenities
  ev_charging: {
    id: 'ev_charging',
    label: 'EV Charging',
    icon: '⚡',
    category: 'amenities',
    description: 'Electric vehicle charging station'
  },
  valet: {
    id: 'valet',
    label: 'Valet',
    icon: '🔑',
    category: 'amenities',
    description: 'Valet parking service'
  },
  car_wash: {
    id: 'car_wash',
    label: 'Car Wash',
    icon: '🚿',
    category: 'amenities',
    description: 'Car wash available'
  },
  restrooms: {
    id: 'restrooms',
    label: 'Restrooms',
    icon: '🚻',
    category: 'amenities',
    description: 'Bathroom facilities nearby'
  },
  
  // Accessibility
  accessible: {
    id: 'accessible',
    label: 'Accessible',
    icon: '♿',
    category: 'accessibility',
    description: 'ADA compliant parking'
  },
  wide_spaces: {
    id: 'wide_spaces',
    label: 'Wide Spaces',
    icon: '↔️',
    category: 'accessibility',
    description: 'Extra wide parking spaces'
  },
  
  // Vehicle Types
  compact_only: {
    id: 'compact_only',
    label: 'Compact Only',
    icon: '🚗',
    category: 'vehicle_type',
    description: 'Small cars only'
  },
  oversized_ok: {
    id: 'oversized_ok',
    label: 'Oversized OK',
    icon: '🚛',
    category: 'vehicle_type',
    description: 'Large vehicles welcome'
  },
  motorcycle: {
    id: 'motorcycle',
    label: 'Motorcycle',
    icon: '🏍️',
    category: 'vehicle_type',
    description: 'Motorcycle parking'
  },
  
  // Special Features
  well_lit: {
    id: 'well_lit',
    label: 'Well Lit',
    icon: '💡',
    category: 'features',
    description: 'Good lighting at night'
  },
  near_entrance: {
    id: 'near_entrance',
    label: 'Near Entrance',
    icon: '🚪',
    category: 'features',
    description: 'Close to building entrance'
  },
  ventilated: {
    id: 'ventilated',
    label: 'Ventilated',
    icon: '💨',
    category: 'features',
    description: 'Good air circulation'
  }
};

// Categories for organizing tags in UI
export const TAG_CATEGORIES = {
  location: {
    label: 'Location & Access',
    color: '#2196F3'
  },
  security: {
    label: 'Security',
    color: '#FF6B35'
  },
  amenities: {
    label: 'Amenities',
    color: '#4CAF50'
  },
  accessibility: {
    label: 'Accessibility',
    color: '#9C27B0'
  },
  vehicle_type: {
    label: 'Vehicle Type',
    color: '#FF9800'
  },
  features: {
    label: 'Features',
    color: '#607D8B'
  }
};

// Get all tags as an array
export const getAllTags = () => Object.values(PARKING_TAGS);

// Get tags by category
export const getTagsByCategory = (category) => 
  Object.values(PARKING_TAGS).filter(tag => tag.category === category);

// Get tag display info
export const getTagDisplay = (tagId) => {
  const tag = PARKING_TAGS[tagId];
  return tag ? `${tag.icon} ${tag.label}` : tagId;
};

// Search tags by text
export const searchTags = (query) => {
  const searchTerm = query.toLowerCase();
  return Object.values(PARKING_TAGS).filter(tag =>
    tag.label.toLowerCase().includes(searchTerm) ||
    tag.description.toLowerCase().includes(searchTerm) ||
    tag.category.toLowerCase().includes(searchTerm)
  );
};