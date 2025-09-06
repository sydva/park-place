import React, { useState, useRef, useEffect } from 'react';
import { searchTags, getAllTags } from '../data/parkingTags';
import Icon from './Icon';
import './SearchBar.css';

const SearchBar = ({ onLocationSearch, onAmenityFilter, onFilterClick }) => {
  const [searchValue, setSearchValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchType, setSearchType] = useState('location'); // 'location' or 'amenity'
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Mock location suggestions - in real app, use geocoding API
  const locationSuggestions = [
    { type: 'location', name: 'Downtown', address: 'Downtown Area', lat: 37.7749, lng: -122.4194 },
    { type: 'location', name: 'Union Square', address: 'Union Square, San Francisco', lat: 37.7880, lng: -122.4075 },
    { type: 'location', name: 'Fisherman\'s Wharf', address: 'Fisherman\'s Wharf, San Francisco', lat: 37.8080, lng: -122.4177 },
    { type: 'location', name: 'Mission District', address: 'Mission District, San Francisco', lat: 37.7599, lng: -122.4148 },
    { type: 'location', name: 'Castro District', address: 'Castro District, San Francisco', lat: 37.7609, lng: -122.4350 },
  ];

  useEffect(() => {
    if (searchValue.length === 0) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    let newSuggestions = [];

    if (searchType === 'location') {
      // Filter location suggestions
      newSuggestions = locationSuggestions.filter(location =>
        location.name.toLowerCase().includes(searchValue.toLowerCase()) ||
        location.address.toLowerCase().includes(searchValue.toLowerCase())
      );
    } else {
      // Filter amenity/tag suggestions
      const tagSuggestions = searchTags(searchValue).map(tag => ({
        type: 'amenity',
        id: tag.id,
        name: tag.label,
        description: tag.description,
        icon: tag.icon
      }));
      newSuggestions = tagSuggestions;
    }

    setSuggestions(newSuggestions.slice(0, 5));
    setShowSuggestions(true);
  }, [searchValue, searchType]);

  // Handle clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(event.target) &&
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    setSearchValue(e.target.value);
  };

  const handleSuggestionClick = (suggestion) => {
    if (suggestion.type === 'location') {
      setSearchValue(suggestion.name);
      onLocationSearch(suggestion);
    } else if (suggestion.type === 'amenity') {
      setSearchValue(suggestion.name);
      onAmenityFilter(suggestion.id);
    }
    setShowSuggestions(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && suggestions.length > 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[0]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      inputRef.current?.blur();
    }
  };

  const handleFocus = () => {
    if (searchValue.length > 0) {
      setShowSuggestions(true);
    }
  };

  const clearSearch = () => {
    setSearchValue('');
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  return (
    <div className="search-bar-container">
      <div className="search-bar">
        <div className="search-type-tabs">
          <button 
            className={`search-tab ${searchType === 'location' ? 'active' : ''}`}
            onClick={() => setSearchType('location')}
          >
            📍 Location
          </button>
          <button 
            className={`search-tab ${searchType === 'amenity' ? 'active' : ''}`}
            onClick={() => setSearchType('amenity')}
          >
            🏷️ Amenities
          </button>
        </div>

        <div className="search-input-container">
          <div className="search-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={searchValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={handleFocus}
              placeholder={
                searchType === 'location' 
                  ? 'Search locations...' 
                  : 'Search amenities (covered, EV charging, etc.)'
              }
              className="search-input"
            />
            {searchValue && (
              <button className="clear-search-btn" onClick={clearSearch}>
                ✕
              </button>
            )}
          </div>
          
          <button className="filter-btn" onClick={onFilterClick}>
            <Icon name="filter" size={18} />
            <span>Filter</span>
          </button>
        </div>

        {showSuggestions && suggestions.length > 0 && (
          <div ref={suggestionsRef} className="search-suggestions">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-item"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion.type === 'location' ? (
                  <>
                    <span className="suggestion-icon">📍</span>
                    <div className="suggestion-content">
                      <span className="suggestion-name">{suggestion.name}</span>
                      <span className="suggestion-address">{suggestion.address}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <Icon name={suggestion.icon} size={16} className="suggestion-icon" />
                    <div className="suggestion-content">
                      <span className="suggestion-name">{suggestion.name}</span>
                      <span className="suggestion-description">{suggestion.description}</span>
                    </div>
                  </>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchBar;