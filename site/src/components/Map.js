import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import UserMenu from './UserMenu';
import ParkingSpaceMarker from './ParkingSpaceMarker';
import ParkingSpaceModal from './ParkingSpaceModal';
import SearchBar from './SearchBar';
import ParkingSpaceList from './ParkingSpaceList';
import FilterModal from './FilterModal';
import { generateParkingSpaces, filterSpacesByZoom } from '../data/parkingSpaces';
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
  const [filters, setFilters] = useState({
    tags: [],
    priceRange: [0, 20],
    maxDistance: 5000,
    spaceTypes: ['premium', 'standard', 'basic'],
    availability: 'available',
    rating: 0
  });

  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser.');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userPos = [position.coords.latitude, position.coords.longitude];
        setPosition(userPos);
        
        // Generate parking spaces around user location
        const spaces = generateParkingSpaces(userPos[0], userPos[1]);
        setParkingSpaces(spaces);
        setFilteredSpaces(spaces);
        setVisibleSpaces(filterSpacesByZoom(spaces, 16));
        
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
  };

  const handleLocationSearch = (location) => {
    // Move map to searched location
    console.log('Searching for location:', location);
    // In real app, would update map center and generate new parking spaces
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

  const applyFilters = (currentFilters) => {
    let filtered = [...parkingSpaces];

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
      <div className="map-wrapper">
        <MapContainer 
          center={position} 
          zoom={16} 
          style={{ 
            height: '100%', 
            width: '100%'
          }}
          zoomControl={false}
          attributionControl={false}
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
        {/* User location marker */}
        <Marker position={position}>
        </Marker>
        {/* Parking space markers */}
        {visibleSpaces.map((space) => (
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