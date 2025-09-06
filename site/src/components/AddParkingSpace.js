import React, { useState, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import SimpleTagInput from './SimpleTagInput';
import Icon from './Icon';
import apiService from '../services/api';
import './AddParkingSpace.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Create a red icon for parking space pins
const parkingIcon = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Create a blue icon for current location
const currentLocationIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="25" height="41" viewBox="0 0 25 41">
      <path fill="#2196F3" stroke="#fff" stroke-width="2" d="M12.5 0C5.6 0 0 5.6 0 12.5c0 8.8 12.5 28.5 12.5 28.5S25 21.3 25 12.5C25 5.6 19.4 0 12.5 0z"/>
      <circle fill="#fff" cx="12.5" cy="12.5" r="6"/>
    </svg>
  `),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  shadowSize: [41, 41],
});

const LocationMarker = ({ position, setPosition }) => {
  const map = useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
    },
  });

  return position === null ? null : (
    <Marker position={position} icon={parkingIcon}>
    </Marker>
  );
};

const AddParkingSpace = () => {
  const [position, setPosition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pinPosition, setPinPosition] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState(0);
  const [tags, setTags] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // Get user's location on component mount
  React.useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setPosition([pos.coords.latitude, pos.coords.longitude]);
          setLoading(false);
        },
        (error) => {
          console.error('Error getting location:', error);
          // Fallback to SF if geolocation fails
          setPosition([37.7749, -122.4194]);
          setLoading(false);
        }
      );
    } else {
      // Fallback to SF if geolocation not supported
      setPosition([37.7749, -122.4194]);
      setLoading(false);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!pinPosition) {
      alert('Please place a pin on the map to mark the parking space location.');
      return;
    }

    if (!title.trim()) {
      alert('Please enter a title for the parking space.');
      return;
    }

    if (!description.trim()) {
      alert('Please enter a description for the parking space.');
      return;
    }

    setSubmitting(true);
    
    try {
      const spaceData = {
        title: title.trim(),
        description: description.trim(),
        lat: pinPosition[0],
        lng: pinPosition[1],
        price: parseFloat(price) || 0,
        tags: tags,
        imageUrl: capturedImage // In a real app, we'd upload this to a file service first
      };

      await apiService.createSpace(spaceData);
      console.log('Parking space created successfully!');
      navigate('/map');
    } catch (error) {
      console.error('Error creating parking space:', error);
      alert('Failed to create parking space. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleImageCapture = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraClick = () => {
    fileInputRef.current.click();
  };

  const goBack = () => {
    navigate('/map');
  };

  if (loading || !position) {
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

  return (
    <div className="add-parking-container">
      <div className="add-parking-header">
        <button className="back-button" onClick={goBack}>
          ← Back
        </button>
        <h1>Add New Parking Space</h1>
      </div>

      <div className="add-parking-content">
        <div className="map-section">
          <h2>Select Location</h2>
          <p className="instruction">Tap on the map to place a pin where the parking space is located</p>
          <div className="map-container">
            <MapContainer
              center={position}
              zoom={16}
              style={{ height: '300px', width: '100%' }}
              zoomControl={false}
              attributionControl={false}
            >
              <TileLayer
                attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                subdomains="abcd"
                maxZoom={20}
              />
              {/* Current location marker (blue) */}
              <Marker position={position} icon={currentLocationIcon}>
              </Marker>
              {/* Parking space marker (red) */}
              <LocationMarker position={pinPosition} setPosition={setPinPosition} />
            </MapContainer>
          </div>
          {pinPosition && (
            <p className="coordinates">
              Selected: {pinPosition[0].toFixed(6)}, {pinPosition[1].toFixed(6)}
            </p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="parking-form">
          <div className="photo-section">
            <h2>Take a Photo</h2>
            <button
              type="button"
              className="camera-button"
              onClick={handleCameraClick}
            >
              <Icon name="camera" size={18} />
              Capture Photo
            </button>
            <input
              type="file"
              accept="image/*"
              capture="environment"
              ref={fileInputRef}
              onChange={handleImageCapture}
              style={{ display: 'none' }}
            />
            
            {capturedImage && (
              <div className="image-preview">
                <img src={capturedImage} alt="Parking space" />
              </div>
            )}
          </div>

          <div className="details-section">
            <h2>Parking Space Details</h2>
            
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Downtown garage spot, Driveway space..."
                className="title-input"
                maxLength="100"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description *</label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief description of the parking space..."
                className="description-input"
                rows="3"
                maxLength="200"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="price">Price per hour ($)</label>
              <input
                type="number"
                id="price"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="0.00"
                className="price-input"
                min="0"
                step="0.50"
              />
              <small className="price-help">Set to 0 for free parking</small>
            </div>
            
            <div className="tags-section">
              <h3>Features & Amenities</h3>
              <p className="tags-description">Select features that describe this parking space</p>
              <SimpleTagInput
                selectedTags={tags}
                onTagsChange={setTags}
                maxTags={8}
              />
            </div>
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={!pinPosition || submitting}
          >
            {submitting ? 'Creating Space...' : 'Add Parking Space'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AddParkingSpace;