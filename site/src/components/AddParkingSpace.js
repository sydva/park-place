import React, { useState, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './AddParkingSpace.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const LocationMarker = ({ position, setPosition }) => {
  const map = useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
    },
  });

  return position === null ? null : (
    <Marker position={position}>
    </Marker>
  );
};

const AddParkingSpace = () => {
  const [position, setPosition] = useState([37.7749, -122.4194]); // Default to SF
  const [pinPosition, setPinPosition] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // Get user's location on component mount
  React.useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setPosition([pos.coords.latitude, pos.coords.longitude]);
      });
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!pinPosition) {
      alert('Please place a pin on the map to mark the parking space location.');
      return;
    }

    // Ready for backend integration
    console.log('Adding parking space at:', pinPosition);
    console.log('Image:', capturedImage);
    console.log('Description:', description);
    console.log('Tags:', tags);

    navigate('/map');
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
              zoom={15}
              style={{ height: '300px', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
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
              📷 Capture Photo
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
            <h2>Additional Details (Optional)</h2>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the parking space..."
              className="description-input"
              rows="3"
              maxLength="200"
            />
            
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="Tags (e.g., covered, street, garage)"
              className="tags-input"
            />
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={!pinPosition}
          >
            Add Parking Space
          </button>
        </form>
      </div>
    </div>
  );
};

export default AddParkingSpace;