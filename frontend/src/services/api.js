/**
 * API Service - Centralized API communication layer
 * Includes caching for performance optimization
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

/**
 * Simple in-memory cache with TTL
 */
const cache = new Map()
const CACHE_TTL = 30000 // 30 seconds
const pendingRequests = new Map() // Prevent duplicate concurrent requests

const getCacheKey = (endpoint, options) => {
  return `${options?.method || 'GET'}:${endpoint}`
}

const getCachedData = (key) => {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }
  cache.delete(key)
  return null
}

const setCachedData = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() })
}

/**
 * Clear cache for a specific endpoint or all cache
 */
export const clearCache = (endpoint = null) => {
  if (endpoint) {
    for (const key of cache.keys()) {
      if (key.includes(endpoint)) {
        cache.delete(key)
      }
    }
  } else {
    cache.clear()
  }
}

/**
 * Get auth token from localStorage
 */
const getToken = () => localStorage.getItem('auth_token')

/**
 * Make an authenticated API request with caching
 */
const apiRequest = async (endpoint, options = {}) => {
  const token = getToken()
  const method = options.method || 'GET'
  const cacheKey = getCacheKey(endpoint, options)
  
  // Only cache GET requests
  if (method === 'GET') {
    // Check cache first
    const cached = getCachedData(cacheKey)
    if (cached) {
      return cached
    }
    
    // Prevent duplicate concurrent requests
    if (pendingRequests.has(cacheKey)) {
      return pendingRequests.get(cacheKey)
    }
  }
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = `Token ${token}`
  }
  
  const requestPromise = (async () => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }))
      throw new Error(error.error || error.detail || 'Request failed')
    }
    
    // Handle 204 No Content
    if (response.status === 204) {
      return null
    }
    
    const data = await response.json()
    
    // Cache GET responses
    if (method === 'GET') {
      setCachedData(cacheKey, data)
    } else {
      // Invalidate related cache on mutations
      clearCache(endpoint.split('/').slice(0, 2).join('/'))
    }
    
    return data
  })()
  
  // Track pending requests
  if (method === 'GET') {
    pendingRequests.set(cacheKey, requestPromise)
    requestPromise.finally(() => pendingRequests.delete(cacheKey))
  }
  
  return requestPromise
}

/**
 * Profile API
 */
export const profileApi = {
  /**
   * Get current user's profile
   */
  getMyProfile: () => apiRequest('/profiles/me/'),
  
  /**
   * Update current user's profile
   */
  updateProfile: (data) => apiRequest('/profiles/me/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  
  /**
   * Get all disability tags
   */
  getTags: () => apiRequest('/profiles/tags/'),
  
  /**
   * Get all interests
   */
  getInterests: () => apiRequest('/profiles/interests/'),
  
  /**
   * Update current mood
   */
  updateMood: (mood) => apiRequest('/profiles/me/mood/', {
    method: 'POST',
    body: JSON.stringify({ mood }),
  }),
  
  /**
   * Get looking for preferences
   */
  getLookingFor: () => apiRequest('/profiles/me/looking-for/'),
  
  /**
   * Update looking for preferences
   */
  updateLookingFor: (data) => apiRequest('/profiles/me/looking-for/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  
  /**
   * Upload profile photo
   */
  uploadPhoto: async (file) => {
    const token = getToken()
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await fetch(`${API_URL}/profiles/me/photos/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
      },
      body: formData,
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Upload failed' }))
      throw new Error(error.error || 'Upload failed')
    }
    
    return response.json()
  },
  
  /**
   * Delete a photo
   */
  deletePhoto: (photoId) => apiRequest(`/profiles/me/photos/${photoId}/`, {
    method: 'DELETE',
  }),
  
  /**
   * Set a photo as primary
   */
  setPrimaryPhoto: (photoId) => apiRequest(`/profiles/me/photos/${photoId}/primary/`, {
    method: 'POST',
  }),
}

/**
 * Discovery/Matching API
 */
export const matchingApi = {
  /**
   * Get profiles for discovery
   */
  discover: () => apiRequest('/discover/'),
  
  /**
   * Swipe on a profile
   * @param {number} toUserId - User ID to swipe on
   * @param {string} action - 'pass', 'like', or 'super'
   */
  swipe: (toUserId, action) => apiRequest('/swipe/', {
    method: 'POST',
    body: JSON.stringify({ to_user: toUserId, action }),
  }),
  
  /**
   * Get all matches
   */
  getMatches: () => apiRequest('/matches/'),
  
  /**
   * Cleanup all matches, swipes, messages for current user
   */
  cleanup: () => apiRequest('/cleanup/', {
    method: 'POST',
  }),
  
  /**
   * Block a user
   */
  blockUser: (userId, reason = '', description = '') => apiRequest('/block/', {
    method: 'POST',
    body: JSON.stringify({ blocked: userId, reason, description }),
  }),
  
  /**
   * Unblock a user
   */
  unblockUser: (userId) => apiRequest(`/block/${userId}/`, {
    method: 'DELETE',
  }),
  
  /**
   * Disconnect/unmatch from a match (also clears chat)
   * @param {number} matchId - Match ID to disconnect from
   */
  unmatch: (matchId) => apiRequest(`/matches/${matchId}/unmatch/`, {
    method: 'POST',
  }),
}

/**
 * Chat/Conversation API
 */
export const chatApi = {
  /**
   * Get all conversations
   */
  getConversations: () => apiRequest('/conversations/'),
  
  /**
   * Get messages in a conversation
   */
  getMessages: (conversationId) => apiRequest(`/conversations/${conversationId}/messages/`),
  
  /**
   * Send a message
   */
  sendMessage: (conversationId, content, messageType = 'text') => 
    apiRequest(`/conversations/${conversationId}/messages/`, {
      method: 'POST',
      body: JSON.stringify({ content, message_type: messageType }),
    }),
}

/**
 * User API
 */
export const userApi = {
  /**
   * Get current user
   */
  getCurrentUser: () => apiRequest('/auth/me/'),
  
  /**
   * Update current user
   */
  updateUser: (data) => apiRequest('/auth/me/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  
  /**
   * Update language preference
   */
  updateLanguage: (language) => apiRequest('/auth/language/', {
    method: 'POST',
    body: JSON.stringify({ language }),
  }),
  
  /**
   * Mark onboarding as complete
   */
  completeOnboarding: () => apiRequest('/auth/onboarding/complete/', {
    method: 'POST',
  }),
  
  /**
   * Validate token
   */
  validateToken: () => apiRequest('/auth/validate/'),
  
  /**
   * Logout
   */
  logout: () => apiRequest('/auth/logout/', {
    method: 'POST',
  }),
}

export default {
  profile: profileApi,
  matching: matchingApi,
  chat: chatApi,
  user: userApi,
  apiUrl: API_URL,
  clearCache,
}
