// Mock parking space data - will be replaced with database calls
export const generateParkingSpaces = (centerLat, centerLng) => {
  const spaces = [];
  const radius = 0.005; // ~500m radius for closer spaces
  
  // Calculate distance function
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
  
  // Generate parking spaces in a grid around the center point
  for (let i = 0; i < 100; i++) {
    const latOffset = (Math.random() - 0.5) * radius * 2;
    const lngOffset = (Math.random() - 0.5) * radius * 2;
    const spaceLat = centerLat + latOffset;
    const spaceLng = centerLng + lngOffset;
    
    const hasPrice = Math.random() > 0.3; // 70% of spaces have pricing
    const space = {
      id: `space-${i}`,
      lat: spaceLat,
      lng: spaceLng,
      type: Math.random() > 0.7 ? 'premium' : Math.random() > 0.4 ? 'standard' : 'basic',
      price: hasPrice ? Math.floor(Math.random() * 8) + 2 : 0, // 0 for free, 2-10 for paid
      rating: Math.random() * 2 + 3, // 3-5 star rating
      availability: Math.random() > 0.3, // 70% available
      distance: calculateDistance(centerLat, centerLng, spaceLat, spaceLng), // actual calculated distance
      timeLimit: Math.random() > 0.5 ? null : [30, 60, 120, 180][Math.floor(Math.random() * 4)], // minutes
      features: getRandomFeatures(),
      // Payment-related fields
      requiresPayment: hasPrice,
      paymentType: hasPrice ? (Math.random() > 0.5 ? 'hourly' : 'flat') : null,
      maxHours: hasPrice ? Math.floor(Math.random() * 8) + 1 : null, // 1-8 hours max
      ownerId: hasPrice ? `owner-${Math.floor(Math.random() * 20)}` : null, // Some spaces are owned privately
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