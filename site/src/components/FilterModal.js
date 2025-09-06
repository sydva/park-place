import React, { useState } from 'react';
import { getAllTags, TAG_CATEGORIES, getTagsByCategory } from '../data/parkingTags';
import Icon from './Icon';
import './FilterModal.css';

const FilterModal = ({ isOpen, onClose, filters = {}, onFiltersChange }) => {
  const [localFilters, setLocalFilters] = useState({
    tags: filters.tags || [],
    priceRange: filters.priceRange || [0, 20],
    maxDistance: filters.maxDistance || 5000,
    spaceTypes: filters.spaceTypes || ['premium', 'standard', 'basic'],
    availability: filters.availability || 'available',
    rating: filters.rating || 0,
    ...filters
  });

  if (!isOpen) return null;

  const handleTagToggle = (tagId) => {
    const newTags = localFilters.tags.includes(tagId)
      ? localFilters.tags.filter(id => id !== tagId)
      : [...localFilters.tags, tagId];
    
    setLocalFilters({ ...localFilters, tags: newTags });
  };

  const handleSpaceTypeToggle = (type) => {
    const newTypes = localFilters.spaceTypes.includes(type)
      ? localFilters.spaceTypes.filter(t => t !== type)
      : [...localFilters.spaceTypes, type];
    
    setLocalFilters({ ...localFilters, spaceTypes: newTypes });
  };

  const handlePriceRangeChange = (index, value) => {
    const newRange = [...localFilters.priceRange];
    newRange[index] = parseInt(value);
    setLocalFilters({ ...localFilters, priceRange: newRange });
  };

  const handleApplyFilters = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  const handleClearFilters = () => {
    const clearedFilters = {
      tags: [],
      priceRange: [0, 20],
      maxDistance: 5000,
      spaceTypes: ['premium', 'standard', 'basic'],
      availability: 'available',
      rating: 0
    };
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const getSpaceTypeColor = (type) => {
    const colors = {
      premium: '#FF6B35',
      standard: '#2196F3',
      basic: '#4CAF50'
    };
    return colors[type];
  };

  return (
    <div className="filter-modal-backdrop" onClick={onClose}>
      <div className="filter-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="filter-modal-header">
          <h2>Filter Parking Spaces</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="filter-modal-body">
          {/* Price Range */}
          <div className="filter-section">
            <h3>Price Range</h3>
            <div className="price-range-controls">
              <div className="price-input-group">
                <label>Min: $</label>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={localFilters.priceRange[0]}
                  onChange={(e) => handlePriceRangeChange(0, e.target.value)}
                  className="price-input"
                />
              </div>
              <div className="price-input-group">
                <label>Max: $</label>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={localFilters.priceRange[1]}
                  onChange={(e) => handlePriceRangeChange(1, e.target.value)}
                  className="price-input"
                />
              </div>
            </div>
            <div className="price-range-display">
              ${localFilters.priceRange[0]} - ${localFilters.priceRange[1]} per hour
            </div>
          </div>

          {/* Distance */}
          <div className="filter-section">
            <h3>Maximum Distance</h3>
            <div className="distance-control">
              <input
                type="range"
                min="100"
                max="10000"
                step="100"
                value={localFilters.maxDistance}
                onChange={(e) => setLocalFilters({ ...localFilters, maxDistance: parseInt(e.target.value) })}
                className="distance-slider"
              />
              <div className="distance-display">
                {localFilters.maxDistance < 1000 
                  ? `${localFilters.maxDistance}m` 
                  : `${(localFilters.maxDistance / 1000).toFixed(1)}km`}
              </div>
            </div>
          </div>

          {/* Space Types */}
          <div className="filter-section">
            <h3>Space Types</h3>
            <div className="space-type-toggles">
              {['premium', 'standard', 'basic'].map(type => (
                <button
                  key={type}
                  className={`space-type-toggle ${localFilters.spaceTypes.includes(type) ? 'selected' : ''}`}
                  onClick={() => handleSpaceTypeToggle(type)}
                  style={{
                    borderColor: localFilters.spaceTypes.includes(type) ? getSpaceTypeColor(type) : '#ddd',
                    backgroundColor: localFilters.spaceTypes.includes(type) ? `${getSpaceTypeColor(type)}20` : 'transparent'
                  }}
                >
                  <div
                    className="space-type-dot"
                    style={{ backgroundColor: getSpaceTypeColor(type) }}
                  ></div>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Rating */}
          <div className="filter-section">
            <h3>Minimum Rating</h3>
            <div className="rating-control">
              <input
                type="range"
                min="0"
                max="5"
                step="0.5"
                value={localFilters.rating}
                onChange={(e) => setLocalFilters({ ...localFilters, rating: parseFloat(e.target.value) })}
                className="rating-slider"
              />
              <div className="rating-display">
                {localFilters.rating > 0 ? `${localFilters.rating}+ stars` : 'Any rating'}
              </div>
            </div>
          </div>

          {/* Availability */}
          <div className="filter-section">
            <h3>Availability</h3>
            <div className="availability-toggles">
              <button
                className={`availability-toggle ${localFilters.availability === 'available' ? 'selected' : ''}`}
                onClick={() => setLocalFilters({ ...localFilters, availability: 'available' })}
              >
                Available Now
              </button>
              <button
                className={`availability-toggle ${localFilters.availability === 'all' ? 'selected' : ''}`}
                onClick={() => setLocalFilters({ ...localFilters, availability: 'all' })}
              >
                Show All
              </button>
            </div>
          </div>

          {/* Amenities/Tags */}
          <div className="filter-section">
            <h3>Amenities</h3>
            {Object.entries(TAG_CATEGORIES).map(([categoryKey, category]) => {
              const tags = getTagsByCategory(categoryKey);
              if (tags.length === 0) return null;

              return (
                <div key={categoryKey} className="tag-category-filter">
                  <h4>{category.label}</h4>
                  <div className="tag-filter-grid">
                    {tags.map(tag => (
                      <button
                        key={tag.id}
                        className={`tag-filter-chip ${localFilters.tags.includes(tag.id) ? 'selected' : ''}`}
                        onClick={() => handleTagToggle(tag.id)}
                      >
                        <Icon name={tag.icon} size={14} />
                        <span>{tag.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="filter-modal-footer">
          <button className="clear-filters-btn" onClick={handleClearFilters}>
            Clear All
          </button>
          <button className="apply-filters-btn" onClick={handleApplyFilters}>
            Apply Filters ({localFilters.tags.length > 0 ? localFilters.tags.length + ' tags' : 'default'})
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterModal;