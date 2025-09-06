// Geocoding service using OpenStreetMap Nominatim API (free alternative to Google Places)

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org';

export const searchLocations = async (query, limit = 5) => {
  if (!query || query.trim().length < 3) {
    return [];
  }

  try {
    const response = await fetch(
      `${NOMINATIM_BASE_URL}/search?format=json&q=${encodeURIComponent(query)}&limit=${limit}&addressdetails=1&extratags=1&countrycodes=us,ca`
    );
    
    if (!response.ok) {
      throw new Error('Geocoding request failed');
    }

    const data = await response.json();
    
    return data.map(item => {
      const address = item.address || {};
      
      // Build street address
      const streetParts = [];
      if (address.house_number) streetParts.push(address.house_number);
      if (address.road) streetParts.push(address.road);
      const streetAddress = streetParts.join(' ');
      
      // Build location name - prefer the street address or first part of display name
      const locationName = streetAddress || item.display_name.split(',')[0];
      
      // Build formatted address for display
      const cityParts = [];
      if (address.city || address.town || address.village) {
        cityParts.push(address.city || address.town || address.village);
      }
      if (address.state) cityParts.push(address.state);
      const cityState = cityParts.join(', ');
      
      const fullAddress = [streetAddress, cityState].filter(Boolean).join(', ') || item.display_name;
      
      return {
        id: item.place_id,
        name: locationName,
        fullName: item.display_name,
        lat: parseFloat(item.lat),
        lng: parseFloat(item.lon),
        type: item.type || 'location',
        category: item.class || 'place',
        streetAddress: streetAddress,
        formattedAddress: fullAddress,
        address: {
          street: streetAddress,
          city: address.city || address.town || address.village || '',
          state: address.state || '',
          country: address.country || '',
          postcode: address.postcode || ''
        }
      };
    });
  } catch (error) {
    console.error('Geocoding error:', error);
    return [];
  }
};

export const reverseGeocode = async (lat, lng) => {
  try {
    const response = await fetch(
      `${NOMINATIM_BASE_URL}/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`
    );
    
    if (!response.ok) {
      throw new Error('Reverse geocoding request failed');
    }

    const data = await response.json();
    
    return {
      name: data.display_name.split(',')[0],
      fullName: data.display_name,
      lat: parseFloat(data.lat),
      lng: parseFloat(data.lon),
      address: {
        street: data.address?.road || '',
        city: data.address?.city || data.address?.town || data.address?.village || '',
        state: data.address?.state || '',
        country: data.address?.country || '',
        postcode: data.address?.postcode || ''
      }
    };
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    return null;
  }
};

// Debounce utility for search performance
export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};