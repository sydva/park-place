// Mock parking space data - will be replaced with database calls
export const generateParkingSpaces = (centerLat, centerLng) => {
  const spaces = [];
  const radius = 0.01; // ~1km radius
  
  // Generate parking spaces in a grid around the center point
  for (let i = 0; i < 100; i++) {
    const latOffset = (Math.random() - 0.5) * radius * 2;
    const lngOffset = (Math.random() - 0.5) * radius * 2;
    
    const space = {
      id: `space-${i}`,
      lat: centerLat + latOffset,
      lng: centerLng + lngOffset,
      type: Math.random() > 0.7 ? 'premium' : Math.random() > 0.4 ? 'standard' : 'basic',
      price: Math.random() > 0.5 ? Math.floor(Math.random() * 8) + 2 : 0, // 0 for free, 2-10 for paid
      rating: Math.random() * 2 + 3, // 3-5 star rating
      availability: Math.random() > 0.3, // 70% available
      distance: Math.random() * 1000, // meters from user
      timeLimit: Math.random() > 0.5 ? null : [30, 60, 120, 180][Math.floor(Math.random() * 4)], // minutes
      features: getRandomFeatures(),
    };
    
    spaces.push(space);
  }
  
  // Sort by rating and availability (best spaces first)
  return spaces.sort((a, b) => {
    if (a.availability !== b.availability) return b.availability - a.availability;
    return b.rating - a.rating;
  });
};

const getRandomFeatures = () => {
  const allFeatures = [
    'covered', 'ev_charging', 'accessible', 'security', 'ground_level',
    'well_lit', 'gated', 'camera_monitored', 'wide_spaces', 'near_entrance',
    'valet', 'car_wash', 'restrooms', 'ventilated', 'underground'
  ];
  const numFeatures = Math.floor(Math.random() * 4) + 1; // 1-4 features
  const features = [];
  
  for (let i = 0; i < numFeatures; i++) {
    const feature = allFeatures[Math.floor(Math.random() * allFeatures.length)];
    if (!features.includes(feature)) {
      features.push(feature);
    }
  }
  
  return features;
};

// Filter spaces based on zoom level (like Google Maps)
export const filterSpacesByZoom = (spaces, zoomLevel) => {
  if (zoomLevel <= 14) {
    // Very zoomed out - show only premium spaces
    return spaces
      .filter(space => space.type === 'premium' && space.availability)
      .slice(0, 10);
  } else if (zoomLevel <= 16) {
    // Medium zoom - show premium and high-rated standard spaces
    return spaces
      .filter(space => 
        space.availability && 
        (space.type === 'premium' || (space.type === 'standard' && space.rating > 4))
      )
      .slice(0, 25);
  } else if (zoomLevel <= 18) {
    // Close zoom - show most available spaces
    return spaces
      .filter(space => space.availability && space.rating > 3.5)
      .slice(0, 50);
  } else {
    // Very close - show all available spaces
    return spaces.filter(space => space.availability);
  }
};