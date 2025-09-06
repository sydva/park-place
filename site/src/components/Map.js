import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import UserMenu from './UserMenu';
import ParkingSpaceMarker from './ParkingSpaceMarker';
import ParkingSpaceModal from './ParkingSpaceModal';
import { generateParkingSpaces, filterSpacesByZoom } from '../data/parkingSpaces';

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
  const [currentZoom, setCurrentZoom] = useState(16);
  const [selectedSpace, setSelectedSpace] = useState(null);

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
    setVisibleSpaces(filterSpacesByZoom(parkingSpaces, zoom));
  };

  const handleMoveChange = (center) => {
    // Could regenerate parking spaces for new area in real app
  };

  const handleParkingSpaceClick = (space) => {
    setSelectedSpace(space);
    console.log('Selected parking space:', space);
  };

  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <UserMenu />
      <MapContainer 
        center={position} 
        zoom={16} 
        style={{ height: '100%', width: '100%' }}
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