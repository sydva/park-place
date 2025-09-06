import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import Icon from './Icon';
import UserMenu from './UserMenu';
import ConfirmModal from './ConfirmModal';
import apiService from '../services/api';
import './MyBookings.css';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancellingId, setCancellingId] = useState(null);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [bookingToCancel, setBookingToCancel] = useState(null);
  const navigate = useNavigate();
  const { user } = useUser();

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    try {
      setLoading(true);
      const userBookings = await apiService.getMyBookings();
      setBookings(userBookings);
    } catch (error) {
      console.error('Failed to load bookings:', error);
      setError('Failed to load your bookings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = (bookingId) => {
    setBookingToCancel(bookingId);
    setShowCancelConfirm(true);
  };

  const confirmCancelBooking = async () => {
    if (!bookingToCancel) return;

    try {
      setCancellingId(bookingToCancel);
      await apiService.cancelBooking(bookingToCancel);
      
      // Update the booking status locally
      setBookings(bookings.map(booking => 
        booking.id === bookingToCancel 
          ? { ...booking, status: 'cancelled' }
          : booking
      ));
    } catch (error) {
      console.error('Failed to cancel booking:', error);
      alert('Failed to cancel booking. Please try again.');
    } finally {
      setCancellingId(null);
      setBookingToCancel(null);
    }
  };

  const handleCancelConfirmClose = () => {
    setShowCancelConfirm(false);
    setBookingToCancel(null);
  };

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    };
  };

  const getBookingStatus = (booking) => {
    const now = new Date();
    const startTime = new Date(booking.start_time);
    const endTime = new Date(booking.end_time);

    if (booking.status === 'cancelled') {
      return { status: 'cancelled', label: 'Cancelled', color: '#f44336' };
    }

    if (now < startTime) {
      return { status: 'upcoming', label: 'Upcoming', color: '#2196F3' };
    }

    if (now >= startTime && now <= endTime) {
      return { status: 'active', label: 'Active', color: '#4CAF50' };
    }

    return { status: 'completed', label: 'Completed', color: '#666' };
  };

  const calculateDuration = (startTime, endTime) => {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const hours = Math.ceil((end - start) / (1000 * 60 * 60));
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  };

  const goBack = () => {
    navigate('/map');
  };

  if (loading) {
    return (
      <div className="my-bookings-container">
        <div className="loading-state">
          <Icon name="loading" size={32} />
          <p>Loading your bookings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="my-bookings-container">
      <UserMenu />
      
      <div className="my-bookings-header">
        <button className="back-button" onClick={goBack}>
          ← Back to Map
        </button>
        <h1>My Bookings</h1>
      </div>

      <div className="my-bookings-content">
        {error && (
          <div className="error-message">
            <Icon name="alert" size={20} />
            {error}
            <button onClick={loadBookings} className="retry-button">
              Retry
            </button>
          </div>
        )}

        {bookings.length === 0 && !error ? (
          <div className="empty-state">
            <Icon name="calendar" size={64} />
            <h2>No bookings yet</h2>
            <p>When you book parking spaces, they'll appear here.</p>
            <button onClick={goBack} className="browse-button">
              Browse Parking Spaces
            </button>
          </div>
        ) : (
          <div className="bookings-list">
            {bookings.map((booking) => {
              const statusInfo = getBookingStatus(booking);
              const startDateTime = formatDateTime(booking.start_time);
              const endDateTime = formatDateTime(booking.end_time);
              const duration = calculateDuration(booking.start_time, booking.end_time);
              const canCancel = statusInfo.status === 'upcoming';

              return (
                <div key={booking.id} className="booking-card">
                  <div className="booking-header">
                    <div className="booking-id">Booking #{booking.id}</div>
                    <div 
                      className="booking-status"
                      style={{ color: statusInfo.color }}
                    >
                      {statusInfo.label}
                    </div>
                  </div>

                  <div className="booking-details">
                    <div className="detail-row">
                      <Icon name="location" size={16} />
                      <span>Space ID: {booking.space_id}</span>
                    </div>
                    
                    <div className="detail-row">
                      <Icon name="calendar" size={16} />
                      <span>
                        {startDateTime.date} at {startDateTime.time} - {endDateTime.time}
                      </span>
                    </div>
                    
                    <div className="detail-row">
                      <Icon name="clock" size={16} />
                      <span>Duration: {duration}</span>
                    </div>
                    
                    <div className="detail-row price-row">
                      <Icon name="dollar" size={16} />
                      <span>Total: ${booking.total_price.toFixed(2)}</span>
                    </div>
                  </div>

                  {canCancel && (
                    <div className="booking-actions">
                      <button
                        onClick={() => handleCancelBooking(booking.id)}
                        disabled={cancellingId === booking.id}
                        className="cancel-booking-button"
                      >
                        {cancellingId === booking.id ? (
                          <>
                            <Icon name="loading" size={16} />
                            Cancelling...
                          </>
                        ) : (
                          <>
                            <Icon name="x" size={16} />
                            Cancel Booking
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
        
        {/* Cancel Confirmation Modal */}
        <ConfirmModal
          isOpen={showCancelConfirm}
          onClose={handleCancelConfirmClose}
          onConfirm={confirmCancelBooking}
          title="Cancel Booking"
          message="Are you sure you want to cancel this booking? This action cannot be undone."
          confirmText="Cancel Booking"
          cancelText="Keep Booking"
          confirmButtonStyle="danger"
        />
      </div>
    </div>
  );
};

export default MyBookings;