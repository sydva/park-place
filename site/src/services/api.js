const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  async fetchSpaces(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/spaces?limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const spaces = await response.json();
      return this.transformApiSpacesToFrontend(spaces);
    } catch (error) {
      console.error('Error fetching spaces:', error);
      throw error;
    }
  }

  async searchSpaces(lat, lng, radius = 1.0, filters = {}) {
    try {
      const searchQuery = {
        lat,
        lng,
        radius,
        min_price: filters.priceRange ? filters.priceRange[0] : undefined,
        max_price: filters.priceRange ? filters.priceRange[1] : undefined,
      };

      const response = await fetch(`${API_BASE_URL}/spaces/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchQuery),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const spaces = await response.json();
      return this.transformApiSpacesToFrontend(spaces);
    } catch (error) {
      console.error('Error searching spaces:', error);
      throw error;
    }
  }

  async getNearbySpaces(lat, lng, radius = 1.0, userEmail = null) {
    try {
      let url = `${API_BASE_URL}/spaces/nearby?lat=${lat}&lng=${lng}&radius=${radius}`;
      if (userEmail) {
        url += `&user_email=${encodeURIComponent(userEmail)}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const spaces = await response.json();
      return this.transformApiSpacesToFrontend(spaces);
    } catch (error) {
      console.error('Error fetching nearby spaces:', error);
      throw error;
    }
  }

  async getSpacesCount(lat, lng, radius = 1.0) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/spaces/count?lat=${lat}&lng=${lng}&radius=${radius}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching spaces count:', error);
      throw error;
    }
  }

  async createSpace(spaceData) {
    try {
      const response = await fetch(`${API_BASE_URL}/spaces`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: spaceData.title,
          description: spaceData.description,
          lat: spaceData.lat,
          lng: spaceData.lng,
          price_per_hour: spaceData.price_per_hour,
          tags: spaceData.tags || [],
          image_url: spaceData.image_url,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const space = await response.json();
      return this.transformApiSpaceToFrontend(space);
    } catch (error) {
      console.error('Error creating space:', error);
      throw error;
    }
  }

  async getSpace(spaceId) {
    try {
      const response = await fetch(`${API_BASE_URL}/spaces/${spaceId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const space = await response.json();
      return this.transformApiSpaceToFrontend(space);
    } catch (error) {
      console.error('Error fetching space:', error);
      throw error;
    }
  }

  // Transform backend API format to frontend format
  transformApiSpacesToFrontend(apiSpaces) {
    return apiSpaces.map(space => this.transformApiSpaceToFrontend(space));
  }

  transformApiSpaceToFrontend(apiSpace) {
    // Calculate mock distance (in real app, backend would provide this)
    const distance = Math.floor(Math.random() * 2000) + 100; // 100-2100 meters

    return {
      id: apiSpace.id,
      lat: apiSpace.lat,
      lng: apiSpace.lng,
      title: apiSpace.title,
      description: apiSpace.description,
      price: apiSpace.price_per_hour,
      type: this.getPriceType(apiSpace.price_per_hour),
      rating: apiSpace.average_rating || 0, // Use real rating from backend
      distance: distance,
      availability: apiSpace.is_available,
      requiresPayment: apiSpace.price_per_hour > 0,
      requiresVerification: apiSpace.requires_verification || false, // Use backend data
      paymentType: 'hourly',
      features: apiSpace.tags || this.generateRandomFeatures(),
      imageUrl: apiSpace.image_url,
      ownerId: apiSpace.owner_id || apiSpace.added_by,
      createdAt: apiSpace.created_at,
    };
  }

  getPriceType(price) {
    if (price === 0) return 'basic';
    if (price >= 15) return 'premium';
    return 'standard';
  }

  generateRandomFeatures() {
    const allFeatures = [
      'covered', 'ev-charging', 'security-camera', '24-7-access', 
      'well-lit', 'wide-spaces', 'disabled-access', 'valet'
    ];
    const numFeatures = Math.floor(Math.random() * 4);
    const shuffled = allFeatures.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, numFeatures);
  }

  // Auth methods
  async getCurrentUser() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting current user:', error);
      throw error;
    }
  }

  async getUserProfileByEmail(email) {
    try {
      const response = await fetch(`${API_BASE_URL}/users/profile?email=${encodeURIComponent(email)}`);
      if (!response.ok) {
        if (response.status === 404) {
          return null; // User not found in database
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting user profile:', error);
      throw error;
    }
  }

  async register(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error registering user:', error);
      throw error;
    }
  }

  async reportLicensePlate(reportData) {
    try {
      const response = await fetch(`${API_BASE_URL}/reports/license-plate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData),
      });
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error reporting license plate:', error);
      throw error;
    }
  }

  // Notification methods
  async getNotifications(email) {
    try {
      const response = await fetch(`${API_BASE_URL}/notifications?email=${encodeURIComponent(email)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting notifications:', error);
      throw error;
    }
  }

  async getUnreadCount(email) {
    try {
      const response = await fetch(`${API_BASE_URL}/notifications/unread-count?email=${encodeURIComponent(email)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting unread count:', error);
      throw error;
    }
  }

  async markNotificationRead(notificationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
        method: 'PUT',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  }

  async updateProfile(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/users/update-profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  }

  async uploadVerificationDocuments(userEmail, profilePhoto, idDocument, vehicleRegistration) {
    try {
      const formData = new FormData();
      formData.append('user_email', userEmail);
      formData.append('profile_photo', profilePhoto);
      formData.append('id_document', idDocument);
      formData.append('vehicle_registration', vehicleRegistration);

      const response = await fetch(`${API_BASE_URL}/verification/upload`, {
        method: 'POST',
        body: formData, // Don't set Content-Type header - let browser set it with boundary
      });
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error uploading verification documents:', error);
      throw error;
    }
  }

  async getVerificationStatus(email) {
    try {
      const response = await fetch(`${API_BASE_URL}/verification/status?email=${encodeURIComponent(email)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting verification status:', error);
      throw error;
    }
  }

  // Booking methods
  async createBooking(bookingData) {
    try {
      const response = await fetch(`${API_BASE_URL}/bookings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData),
      });
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating booking:', error);
      throw error;
    }
  }

  // Rating methods
  async createPlaceRating(placeId, rating, description = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/ratings/places`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          place_id: placeId,
          rating: rating,
          description: description
        }),
      });
      
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating place rating:', error);
      throw error;
    }
  }

  async getMyBookings() {
    try {
      const response = await fetch(`${API_BASE_URL}/bookings/my-bookings`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting my bookings:', error);
      throw error;
    }
  }

  async getPlaceRatings(placeId) {
    try {
      const response = await fetch(`${API_BASE_URL}/ratings/places/${placeId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting place ratings:', error);
      throw error;
    }
  }

  async cancelBooking(bookingId) {
    try {
      const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/cancel`, {
        method: 'PUT',
      });
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error cancelling booking:', error);
      throw error;
    }
  }

  async createUserRating(userId, rating, description = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/ratings/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ratee_id: userId,
          rating: rating,
          description: description
        }),
      });
      
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If we can't parse the error response, use the generic message
        }
        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating user rating:', error);
      throw error;
    }
  }

  async getSpaceBookings(spaceId) {
    try {
      const response = await fetch(`${API_BASE_URL}/bookings/space/${spaceId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting space bookings:', error);
      throw error;
    }
  }

  async getUserRatings(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/ratings/users/${userId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting user ratings:', error);
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;