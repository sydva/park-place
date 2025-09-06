import React, { useState } from 'react';
import Icon from './Icon';
import apiService from '../services/api';
import './BookingModal.css';

const BookingModal = ({ space, onClose, onBookingSuccess }) => {
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!space) return null;

  // Get current date and time for minimum values
  const now = new Date();
  const today = now.toISOString().split('T')[0];
  const currentTime = now.toTimeString().slice(0, 5);

  const calculateDuration = () => {
    if (!startDate || !startTime || !endDate || !endTime) return 0;
    
    const start = new Date(`${startDate}T${startTime}`);
    const end = new Date(`${endDate}T${endTime}`);
    
    if (end <= start) return 0;
    
    return Math.ceil((end - start) / (1000 * 60 * 60)); // hours
  };

  const calculateTotalPrice = () => {
    const duration = calculateDuration();
    return duration * space.price;
  };

  const validateBooking = () => {
    if (!startDate || !startTime || !endDate || !endTime) {
      return 'Please select both start and end times';
    }

    const start = new Date(`${startDate}T${startTime}`);
    const end = new Date(`${endDate}T${endTime}`);
    const now = new Date();

    if (start < now) {
      return 'Start time cannot be in the past';
    }

    if (end <= start) {
      return 'End time must be after start time';
    }

    if (calculateDuration() > 24) {
      return 'Maximum booking duration is 24 hours';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateBooking();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const startDateTime = new Date(`${startDate}T${startTime}`);
      const endDateTime = new Date(`${endDate}T${endTime}`);

      const bookingData = {
        space_id: space.id,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString()
      };

      const booking = await apiService.createBooking(bookingData);
      
      if (onBookingSuccess) {
        onBookingSuccess(booking);
      }
      
      onClose();
    } catch (error) {
      console.error('Booking failed:', error);
      setError(error.message || 'Failed to create booking. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const duration = calculateDuration();
  const totalPrice = calculateTotalPrice();

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="booking-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Book Parking Space</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="booking-space-info">
          <div className="space-summary">
            <h3>{space.title || 'Parking Space'}</h3>
            <p className="space-price">${space.price}/hour</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="booking-form">
          <div className="datetime-section">
            <h3>When do you need parking?</h3>
            
            <div className="datetime-row">
              <div className="datetime-group">
                <label htmlFor="start-date">Start Date</label>
                <input
                  type="date"
                  id="start-date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  min={today}
                  className="date-input"
                  required
                />
              </div>
              <div className="datetime-group">
                <label htmlFor="start-time">Start Time</label>
                <input
                  type="time"
                  id="start-time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  min={startDate === today ? currentTime : undefined}
                  className="time-input"
                  required
                />
              </div>
            </div>

            <div className="datetime-row">
              <div className="datetime-group">
                <label htmlFor="end-date">End Date</label>
                <input
                  type="date"
                  id="end-date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate || today}
                  className="date-input"
                  required
                />
              </div>
              <div className="datetime-group">
                <label htmlFor="end-time">End Time</label>
                <input
                  type="time"
                  id="end-time"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  className="time-input"
                  required
                />
              </div>
            </div>
          </div>

          {duration > 0 && (
            <div className="booking-summary">
              <div className="summary-row">
                <span>Duration:</span>
                <span>{duration} hour{duration !== 1 ? 's' : ''}</span>
              </div>
              <div className="summary-row total">
                <span>Total Cost:</span>
                <span>${totalPrice.toFixed(2)}</span>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              <Icon name="alert" size={16} />
              {error}
            </div>
          )}

          <div className="booking-actions">
            <button type="button" className="cancel-button" onClick={onClose}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="book-button"
              disabled={isSubmitting || duration <= 0}
            >
              {isSubmitting ? (
                <>
                  <Icon name="loading" size={16} />
                  Booking...
                </>
              ) : (
                <>
                  <Icon name="check" size={16} />
                  Book for ${totalPrice.toFixed(2)}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BookingModal;