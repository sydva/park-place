import React, { useState, useRef, useEffect } from 'react';
import { getAllTags, getTagsByCategory, TAG_CATEGORIES, searchTags } from '../data/parkingTags';
import './TagInput.css';

const TagInput = ({ selectedTags = [], onTagsChange, maxTags = 10 }) => {
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const inputRef = useRef(null);
  const suggestionRef = useRef(null);

  const allTags = getAllTags();

  // Handle input change and filter suggestions
  useEffect(() => {
    if (inputValue.length > 0) {
      let filteredTags = searchTags(inputValue);
      
      // Filter by category if selected
      if (selectedCategory !== 'all') {
        filteredTags = filteredTags.filter(tag => tag.category === selectedCategory);
      }
      
      // Remove already selected tags
      filteredTags = filteredTags.filter(tag => !selectedTags.includes(tag.id));
      
      setSuggestions(filteredTags.slice(0, 8)); // Limit to 8 suggestions
      setShowSuggestions(true);
    } else {
      // Show popular/common tags when no input
      const popularTags = allTags
        .filter(tag => ['covered', 'security', 'ev_charging', 'accessible', 'ground_level', 'well_lit'])
        .filter(tag => !selectedTags.includes(tag.id));
      
      setSuggestions(popularTags);
      setShowSuggestions(inputValue.length === 0 && document.activeElement === inputRef.current);
    }
  }, [inputValue, selectedTags, selectedCategory, allTags]);

  // Handle tag selection
  const handleTagSelect = (tag) => {
    if (selectedTags.length >= maxTags) return;
    
    const newTags = [...selectedTags, tag.id];
    onTagsChange(newTags);
    setInputValue('');
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  // Remove selected tag
  const handleTagRemove = (tagId) => {
    const newTags = selectedTags.filter(id => id !== tagId);
    onTagsChange(newTags);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
      inputRef.current?.blur();
    } else if (e.key === 'Enter' && suggestions.length > 0) {
      e.preventDefault();
      handleTagSelect(suggestions[0]);
    }
  };

  // Handle input focus
  const handleFocus = () => {
    setShowSuggestions(true);
  };

  // Handle clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(event.target) &&
        suggestionRef.current &&
        !suggestionRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Get tag display info
  const getTagInfo = (tagId) => allTags.find(tag => tag.id === tagId);

  return (
    <div className="tag-input-container">
      {/* Category Filter */}
      <div className="category-filter">
        <select 
          value={selectedCategory} 
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="category-select"
        >
          <option value="all">All Categories</option>
          {Object.entries(TAG_CATEGORIES).map(([key, category]) => (
            <option key={key} value={key}>{category.label}</option>
          ))}
        </select>
      </div>

      {/* Selected Tags Display */}
      <div className="selected-tags">
        {selectedTags.map(tagId => {
          const tag = getTagInfo(tagId);
          if (!tag) return null;
          
          return (
            <span key={tagId} className="selected-tag">
              <span className="tag-icon">{tag.icon}</span>
              <span className="tag-label">{tag.label}</span>
              <button
                type="button"
                className="remove-tag"
                onClick={() => handleTagRemove(tagId)}
                aria-label={`Remove ${tag.label} tag`}
              >
                ×
              </button>
            </span>
          );
        })}
      </div>

      {/* Input Field */}
      <div className="input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={selectedTags.length === 0 ? "Add tags (e.g., covered, security, EV charging...)" : "Add more tags..."}
          className="tag-input"
          disabled={selectedTags.length >= maxTags}
        />
        
        {selectedTags.length >= maxTags && (
          <div className="max-tags-message">
            Maximum {maxTags} tags allowed
          </div>
        )}
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div ref={suggestionRef} className="suggestions-dropdown">
          <div className="suggestions-header">
            {inputValue ? 'Matching tags:' : 'Popular tags:'}
          </div>
          {suggestions.map(tag => (
            <button
              key={tag.id}
              type="button"
              className="suggestion-item"
              onClick={() => handleTagSelect(tag)}
            >
              <span className="suggestion-icon">{tag.icon}</span>
              <div className="suggestion-content">
                <span className="suggestion-label">{tag.label}</span>
                <span className="suggestion-description">{tag.description}</span>
              </div>
              <span className="suggestion-category">
                {TAG_CATEGORIES[tag.category]?.label}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Tag Count */}
      <div className="tag-count">
        {selectedTags.length} / {maxTags} tags
      </div>
    </div>
  );
};

export default TagInput;