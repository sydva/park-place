import React from 'react';
import { getAllTags, TAG_CATEGORIES } from '../data/parkingTags';
import Icon from './Icon';
import './SimpleTagInput.css';

const SimpleTagInput = ({ selectedTags = [], onTagsChange, maxTags = 8 }) => {
  const allTags = getAllTags();

  // Group tags by category
  const tagsByCategory = allTags.reduce((acc, tag) => {
    if (!acc[tag.category]) {
      acc[tag.category] = [];
    }
    acc[tag.category].push(tag);
    return acc;
  }, {});

  const handleTagToggle = (tagId) => {
    if (selectedTags.includes(tagId)) {
      // Remove tag
      onTagsChange(selectedTags.filter(id => id !== tagId));
    } else {
      // Add tag (if under limit)
      if (selectedTags.length < maxTags) {
        onTagsChange([...selectedTags, tagId]);
      }
    }
  };

  return (
    <div className="simple-tag-input">
      <div className="tag-counter">
        {selectedTags.length} / {maxTags} selected
      </div>
      
      {Object.entries(tagsByCategory).map(([categoryKey, tags]) => (
        <div key={categoryKey} className="tag-category">
          <h4 className="category-title">
            {TAG_CATEGORIES[categoryKey]?.label || categoryKey}
          </h4>
          <div className="tag-grid">
            {tags.map(tag => {
              const isSelected = selectedTags.includes(tag.id);
              const isDisabled = !isSelected && selectedTags.length >= maxTags;
              
              return (
                <button
                  key={tag.id}
                  type="button"
                  className={`tag-chip ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
                  onClick={() => handleTagToggle(tag.id)}
                  disabled={isDisabled}
                  title={tag.description}
                >
                  <Icon name={tag.icon} size={16} className="tag-icon" />
                  <span className="tag-label">{tag.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SimpleTagInput;