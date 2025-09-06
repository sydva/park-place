import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useUser } from '@clerk/clerk-react';
import UserMenu from './UserMenu';
import ParkingSpaceMarker from './ParkingSpaceMarker';
import ParkingSpaceModal from './ParkingSpaceModal';
import SearchBar from './SearchBar';
import ParkingSpaceList from './ParkingSpaceList';
import FilterModal from './FilterModal';
import { filterSpacesByZoom } from '../data/parkingSpaces';
import apiService from '../services/api';
import './MapLayout.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Component to handle map events and update zoom-based filtering
const MapEventHandler = ({ onZoomChange, onMoveChange }) => {
  const map = useMapEvents({
    zoomend: () => {
      onZoomChange(map.getZoom());
    },
    moveend: () => {
      const center = map.getCenter();
      onMoveChange([center.lat, center.lng]);
    },
  });
  return null;
};

// Invalidate map size when layout changes (e.g., sidebar collapse/expand)
const ResizeHandler = ({ listVisible }) => {
  const map = useMapEvents({});
  useEffect(() => {
    // Immediate invalidate without animation to reduce jank
    try {
      map.invalidateSize({ animate: false });
    } catch (_) {}

    // Invalidate again after the sidebar transition completes
    const sidebar = document.querySelector('.parking-space-list');
    if (!sidebar) return;
    const onTransitionEnd = () => {
      try {
        map.invalidateSize({ animate: false });
      } catch (_) {}
    };
    sidebar.addEventListener('transitionend', onTransitionEnd, { once: true });
    return () => {
      sidebar.removeEventListener('transitionend', onTransitionEnd);
    };
  }, [listVisible, map]);
  return null;
};

const Map = () => {
  const [position, setPosition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [parkingSpaces, setParkingSpaces] = useState([]);
  const [visibleSpaces, setVisibleSpaces] = useState([]);
  const [filteredSpaces, setFilteredSpaces] = useState([]);
  const [currentZoom, setCurrentZoom] = useState(16);
  const [selectedSpace, setSelectedSpace] = useState(null);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [listVisible, setListVisible] = useState(true);
  const [mapCenter, setMapCenter] = useState(null);
  const [searchLocation, setSearchLocation] = useState(null);
  
  // User verification status from Clerk
  const { user: clerkUser, isLoaded: isUserLoaded } = useUser();
  const [isUserVerified, setIsUserVerified] = useState(false);
  const [filters, setFilters] = useState({
    tags: [],
    priceRange: [0, 20],
    maxDistance: 5000,
    spaceTypes: ['premium', 'standard', 'basic'],
    availability: 'available',
    rating: 0
  });

  useEffect(() => {
    const loadParkingData = async () => {
      if (!navigator.geolocation) {
        setError('Geolocation is not supported by this browser.');
        setLoading(false);
        return;
      }

      try {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const userPos = [position.coords.latitude, position.coords.longitude];
            setPosition(userPos);
            setMapCenter(userPos);
            
            // Load parking spaces from backend
            try {
              // Set user verification status (for now, all Clerk users are verified)
              setIsUserVerified(true);
              
              // Load parking spaces 
              const spaces = await apiService.getNearbySpaces(userPos[0], userPos[1], 5.0);
              setParkingSpaces(spaces);
              setFilteredSpaces(spaces);
              setVisibleSpaces(filterSpacesByZoom(spaces, 16));
            } catch (apiError) {
              console.error('Failed to load parking spaces from API:', apiError);
              // Fallback to mock data if API fails
              const { generateParkingSpaces } = await import('../data/parkingSpaces');
              const fallbackSpaces = generateParkingSpaces(userPos[0], userPos[1]);
              setParkingSpaces(fallbackSpaces);
              setFilteredSpaces(fallbackSpaces);
              setVisibleSpaces(filterSpacesByZoom(fallbackSpaces, 16));
            }
            
            setLoading(false);
          },
          (error) => {
            setError('Unable to retrieve your location: ' + error.message);
            setLoading(false);
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
          }
        );
      } catch (error) {
        setError('Failed to initialize map: ' + error.message);
        setLoading(false);
      }
    };

    loadParkingData();
  }, []);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Getting your location...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: 'red'
      }}>
        {error}
      </div>
    );
  }

  const handleZoomChange = (zoom) => {
    setCurrentZoom(zoom);
    const zoomFiltered = filterSpacesByZoom(filteredSpaces.length > 0 ? filteredSpaces : parkingSpaces, zoom);
    setVisibleSpaces(zoomFiltered);
  };

  const handleMoveChange = (center) => {
    // Could regenerate parking spaces for new area in real app
  };

  const handleParkingSpaceClick = (space) => {
    setSelectedSpace(space);
    setMapCenter([space.lat, space.lng]);
  };

  const handleLocationSearch = async (location) => {
    console.log('Navigating to location:', location);
    const newCenter = [location.lat, location.lng];
    
    // Update map center and search location marker
    setMapCenter(newCenter);
    setSearchLocation(location);
    
    // Load new parking spaces around the searched location
    try {
      const newSpaces = await apiService.getNearbySpaces(location.lat, location.lng, 5.0);
      setParkingSpaces(newSpaces);
      // Apply current filters to new spaces
      applyFilters(filters, newSpaces);
    } catch (error) {
      console.error('Failed to load parking spaces for search location:', error);
      // Fallback to mock data if API fails
      const { generateParkingSpaces } = await import('../data/parkingSpaces');
      const fallbackSpaces = generateParkingSpaces(location.lat, location.lng);
      setParkingSpaces(fallbackSpaces);
      applyFilters(filters, fallbackSpaces);
    }
  };

  const handleAmenityFilter = (tagId) => {
    // Add tag to filters
    const newFilters = {
      ...filters,
      tags: [...filters.tags, tagId]
    };
    setFilters(newFilters);
    applyFilters(newFilters);
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    applyFilters(newFilters);
  };

  const applyFilters = (currentFilters, spacesToFilter = null) => {
    let filtered = [...(spacesToFilter || parkingSpaces)];

    // Filter by availability
    if (currentFilters.availability === 'available') {
      filtered = filtered.filter(space => space.availability);
    }

    // Filter by space types
    if (currentFilters.spaceTypes.length > 0) {
      filtered = filtered.filter(space => currentFilters.spaceTypes.includes(space.type));
    }

    // Filter by price range
    filtered = filtered.filter(space => 
      space.price >= currentFilters.priceRange[0] && 
      space.price <= currentFilters.priceRange[1]
    );

    // Filter by rating
    if (currentFilters.rating > 0) {
      filtered = filtered.filter(space => space.rating >= currentFilters.rating);
    }

    // Filter by tags
    if (currentFilters.tags.length > 0) {
      filtered = filtered.filter(space => 
        currentFilters.tags.some(tag => space.features.includes(tag))
      );
    }

    // Filter by distance (if user location available)
    if (position && currentFilters.maxDistance) {
      filtered = filtered.filter(space => space.distance <= currentFilters.maxDistance);
    }

    setFilteredSpaces(filtered);
    
    // Update visible spaces with zoom filtering applied to filtered results
    const zoomFiltered = filterSpacesByZoom(filtered, currentZoom);
    setVisibleSpaces(zoomFiltered);
  };


  return (
    <div className="map-container-with-search">
      <UserMenu />
      
      {/* Search Bar */}
      <SearchBar 
        onLocationSearch={handleLocationSearch}
        onAmenityFilter={handleAmenityFilter}
        onFilterClick={() => setShowFilterModal(true)}
      />
      
      {/* Main Map Container */}
      <div className={`map-wrapper ${listVisible ? 'with-sidebar' : 'sidebar-hidden'}`}>
        <MapContainer 
          center={mapCenter || position} 
          zoom={16} 
          style={{ 
            height: '100%', 
            width: '100%'
          }}
          zoomControl={false}
          attributionControl={false}
          key={mapCenter ? `${mapCenter[0]}-${mapCenter[1]}` : 'default'}
        >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
          maxZoom={20}
        />
        <MapEventHandler 
          onZoomChange={handleZoomChange} 
          onMoveChange={handleMoveChange}
        />
        {/* Ensure map resizes after sidebar visibility changes */}
        <ResizeHandler listVisible={listVisible} />
        {/* User location marker */}
        {position && (
          <Marker position={position}>
          </Marker>
        )}
        
        {/* Search location marker */}
        {searchLocation && (
          <Marker 
            position={[searchLocation.lat, searchLocation.lng]}
            icon={L.divIcon({
              html: `<div style="background: #ff6b6b; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🔍</div>`,
              className: 'search-location-marker',
              iconSize: [20, 20],
              iconAnchor: [10, 10],
            })}
          >
          </Marker>
        )}
        {/* Parking space markers */}
        {visibleSpaces
          .filter(space => isUserVerified || !space.requiresVerification)
          .map((space) => (
            <ParkingSpaceMarker 
              key={space.id}
              space={space}
              showPrice={currentZoom > 17}
              onClick={handleParkingSpaceClick}
            />
          ))}
        </MapContainer>
      </div>
      
      {/* Parking Space List */}
      <ParkingSpaceList
        spaces={filteredSpaces.length > 0 ? filteredSpaces : parkingSpaces}
        userLocation={position}
        onSpaceClick={handleParkingSpaceClick}
        onSpaceSelect={handleParkingSpaceClick}
        isVisible={listVisible}
        onToggle={() => setListVisible(!listVisible)}
        isUserVerified={isUserVerified}
      />
      
      {/* Filter Modal */}
      <FilterModal
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        filters={filters}
        onFiltersChange={handleFiltersChange}
      />
      
      {/* Parking Space Modal */}
      {selectedSpace && (
        <ParkingSpaceModal
          space={selectedSpace}
          userLocation={position}
          onClose={() => setSelectedSpace(null)}
        />
      )}
    </div>
  );
};

export default Map;