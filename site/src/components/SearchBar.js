import React, { useState, useRef, useEffect } from 'react';
import { searchTags, getAllTags } from '../data/parkingTags';
import { searchLocations, debounce } from '../services/geocoding';
import Icon from './Icon';
import './SearchBar.css';

const SearchBar = ({ onLocationSearch, onAmenityFilter, onFilterClick }) => {
  const [searchValue, setSearchValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchType, setSearchType] = useState('location'); // 'location' or 'amenity'
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Debounced search function
  const debouncedLocationSearch = useRef(
    debounce(async (query) => {
      if (query.length < 3) {
        setSuggestions([]);
        setShowSuggestions(false);
        setIsLoading(false);
        return;
      }

      try {
        const results = await searchLocations(query);
        const formattedResults = results.map(result => ({
          type: 'location',
          name: result.name,
          fullName: result.fullName,
          address: result.formattedAddress,
          lat: result.lat,
          lng: result.lng
        }));
        
        setSuggestions(formattedResults.slice(0, 5));
        setShowSuggestions(true);
      } catch (error) {
        console.error('Search error:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300)
  ).current;

  useEffect(() => {
    if (searchValue.length === 0) {
      setSuggestions([]);
      setShowSuggestions(false);
      setIsLoading(false);
      return;
    }

    if (searchType === 'location') {
      setIsLoading(true);
      debouncedLocationSearch(searchValue);
    } else {
      // Filter amenity/tag suggestions
      const tagSuggestions = searchTags(searchValue).map(tag => ({
        type: 'amenity',
        id: tag.id,
        name: tag.label,
        description: tag.description,
        icon: tag.icon
      }));
      setSuggestions(tagSuggestions.slice(0, 5));
      setShowSuggestions(tagSuggestions.length > 0);
    }
  }, [searchValue, searchType, debouncedLocationSearch]);

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
    if (e.key === 'Enter') {
      e.preventDefault();
      if (suggestions.length > 0) {
        handleSuggestionClick(suggestions[0]);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      inputRef.current?.blur();
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (suggestions.length > 0) {
      handleSuggestionClick(suggestions[0]);
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
            <Icon name="map-pin" size={16} className="suggestion-icon location-icon" />
            <span>Location</span>
          </button>
          <button 
            className={`search-tab ${searchType === 'amenity' ? 'active' : ''}`}
            onClick={() => setSearchType('amenity')}
          >
            <Icon name="tag" size={16} className="suggestion-icon" />
            <span>Amenities</span>
          </button>
        </div>

        <div className="search-input-container">
          <form onSubmit={handleFormSubmit} className="search-form">
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
                <button type="button" className="clear-search-btn" onClick={clearSearch}>
                  ✕
                </button>
              )}
            </div>
          </form>
          
          <button type="button" className="filter-btn" onClick={onFilterClick}>
            <Icon name="filter" size={18} />
            <span>Filter</span>
          </button>
        </div>

        {(showSuggestions || isLoading) && (
          <div ref={suggestionsRef} className="search-suggestions">
            {isLoading ? (
              <div className="suggestion-loading">
                <div className="loading-spinner"></div>
                <span>Searching locations...</span>
              </div>
            ) : suggestions.length > 0 ? (
              suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion.type === 'location' ? (
                    <>
                      <Icon name="map-pin" size={16} className="suggestion-icon location-icon" />
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
              ))
            ) : searchType === 'location' && searchValue.length >= 3 ? (
              <div className="no-suggestions">
                <span>No locations found for "{searchValue}"</span>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchBar;