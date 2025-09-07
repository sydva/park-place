// Distance utility functions for handling unit conversions

/**
 * Format distance based on user's unit preference
 * @param {number} meters - Distance in meters
 * @param {string} unitsPreference - 'imperial' or 'metric'
 * @param {boolean} showShortForm - Use short form (ft/mi vs feet/miles)
 * @returns {string} Formatted distance string
 */
export function formatDistance(meters, unitsPreference = 'imperial', showShortForm = true) {
  if (unitsPreference === 'metric') {
    if (meters < 1000) {
      return showShortForm ? `${meters}m` : `${meters} meters`;
    } else {
      const km = (meters / 1000).toFixed(1);
      return showShortForm ? `${km}km` : `${km} kilometers`;
    }
  } else {
    // Imperial (feet and miles)
    const feet = Math.round(meters * 3.28084);
    if (feet < 5280) {
      return showShortForm ? `${feet}ft` : `${feet} feet`;
    } else {
      const miles = (feet / 5280).toFixed(1);
      return showShortForm ? `${miles}mi` : `${miles} miles`;
    }
  }
}

/**
 * Convert meters to feet
 * @param {number} meters
 * @returns {number} feet
 */
export function metersToFeet(meters) {
  return meters * 3.28084;
}

/**
 * Convert feet to meters
 * @param {number} feet
 * @returns {number} meters
 */
export function feetToMeters(feet) {
  return feet / 3.28084;
}

/**
 * Convert meters to miles
 * @param {number} meters
 * @returns {number} miles
 */
export function metersToMiles(meters) {
  return meters * 0.000621371;
}

/**
 * Convert miles to meters
 * @param {number} miles
 * @returns {number} meters
 */
export function milesToMeters(miles) {
  return miles / 0.000621371;
}

/**
 * Get the user's preferred units based on their location or saved preference
 * Defaults to imperial for US, metric for rest of world
 * @returns {string} 'imperial' or 'metric'
 */
export function getDefaultUnitsPreference() {
  try {
    // Try to detect user's locale
    const locale = navigator.language || navigator.userLanguage;
    
    // US territories and countries that use imperial
    const imperialCountries = ['US', 'LR', 'MM']; // US, Liberia, Myanmar
    const userCountry = locale.split('-')[1];
    
    if (imperialCountries.includes(userCountry)) {
      return 'imperial';
    }
    
    return 'metric';
  } catch (error) {
    // Default to imperial if detection fails
    return 'imperial';
  }
}

/**
 * Format distance for UI display with "away" suffix
 * @param {number} meters - Distance in meters
 * @param {string} unitsPreference - 'imperial' or 'metric'
 * @returns {string} Formatted distance string with "away"
 */
export function formatDistanceAway(meters, unitsPreference = 'imperial') {
  const formatted = formatDistance(meters, unitsPreference, true);
  return `${formatted} away`;
}