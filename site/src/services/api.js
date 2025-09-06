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

  async getNearbySpaces(lat, lng, radius = 1.0) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/spaces/nearby?lat=${lat}&lng=${lng}&radius=${radius}`
      );
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
          price_per_hour: spaceData.price,
          tags: spaceData.tags || [],
          image_url: spaceData.imageUrl,
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
      rating: apiSpace.rating || Math.random() * 2 + 3, // 3-5 rating
      distance: distance,
      availability: apiSpace.is_available,
      requiresPayment: apiSpace.price_per_hour > 0,
      requiresVerification: Math.random() > 0.9, // 10% require verification
      paymentType: 'hourly',
      features: apiSpace.tags || this.generateRandomFeatures(),
      imageUrl: apiSpace.image_url,
      ownerId: apiSpace.owner_id,
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
}

export default new ApiService();