import { ref, computed } from 'vue'

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Facebook App ID - set this in .env file
const FACEBOOK_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID || ''

// Load saved user data from localStorage on initialization
const loadSavedUser = () => {
  try {
    const savedUserData = localStorage.getItem('user_data')
    if (savedUserData) {
      return JSON.parse(savedUserData)
    }
  } catch (e) {
    console.warn('Failed to parse saved user data:', e)
    localStorage.removeItem('user_data')
  }
  return null
}

// Auth state - initialize from localStorage
const user = ref(loadSavedUser())
const token = ref(localStorage.getItem('auth_token') || null)
const facebookAccessToken = ref(localStorage.getItem('fb_access_token') || null)
const isLoading = ref(false)
const error = ref(null)
const isAuthenticated = computed(() => !!token.value && !!user.value)
const facebookSDKLoaded = ref(false)

/**
 * Initialize Facebook SDK with timeout (kept for potential future use)
 */
const initFacebookSDK = () => {
  return Promise.resolve() // No longer needed for redirect flow
}

/**
 * Check if we're on HTTPS (required for Facebook login)
 */
const isHttps = () => {
  return window.location.protocol === 'https:' || window.location.hostname === 'localhost'
}

/**
 * Login with Facebook using redirect flow (no popup)
 * Redirects user to Facebook, then back to our app
 */
const loginWithFacebook = async () => {
  isLoading.value = true
  error.value = null

  try {
    // Check if we're on HTTP (not localhost) - Facebook requires HTTPS
    if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
      throw new Error('Facebook login requires HTTPS. Please use HTTPS or localhost for development.')
    }

    if (!FACEBOOK_APP_ID) {
      throw new Error('Facebook App ID not configured')
    }

    // Build Facebook OAuth URL for redirect flow
    const redirectUri = encodeURIComponent(window.location.origin + '/auth/facebook/callback')
    // Request user_friends permission to allow inviting friends
    const scope = encodeURIComponent('email,public_profile,user_birthday,user_gender,user_friends')
    const state = encodeURIComponent(JSON.stringify({ 
      returnUrl: window.location.pathname,
      timestamp: Date.now() 
    }))
    
    // Store state in localStorage for verification when we return
    localStorage.setItem('fb_auth_state', state)
    
    // Redirect to Facebook OAuth
    const facebookAuthUrl = `https://www.facebook.com/v18.0/dialog/oauth?` +
      `client_id=${FACEBOOK_APP_ID}` +
      `&redirect_uri=${redirectUri}` +
      `&scope=${scope}` +
      `&state=${state}` +
      `&response_type=code`
    
    console.log('Redirecting to Facebook OAuth:', facebookAuthUrl)
    
    // Redirect to Facebook (this will navigate away from the app)
    window.location.href = facebookAuthUrl
    
    // This won't be reached as we're redirecting
    return { success: true, redirecting: true }

  } catch (err) {
    console.error('Facebook login error:', err)
    error.value = err.message
    isLoading.value = false
    return {
      success: false,
      error: err.message,
    }
  }
}

/**
 * Handle Facebook OAuth callback (called when returning from Facebook)
 */
const handleFacebookCallback = async () => {
  isLoading.value = true
  error.value = null

  try {
    // Get the authorization code from URL
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const returnedState = urlParams.get('state')
    const errorParam = urlParams.get('error')
    const errorDescription = urlParams.get('error_description')

    // Check for errors from Facebook
    if (errorParam) {
      throw new Error(errorDescription || `Facebook auth error: ${errorParam}`)
    }

    if (!code) {
      throw new Error('No authorization code received from Facebook')
    }

    // Verify state matches what we sent
    const storedState = localStorage.getItem('fb_auth_state')
    if (storedState && returnedState !== storedState) {
      console.warn('State mismatch - possible CSRF attack')
      // Continue anyway for now, but log warning
    }
    
    // Clear stored state
    localStorage.removeItem('fb_auth_state')

    // Send authorization code to backend
    const redirectUri = window.location.origin + '/auth/facebook/callback'
    console.log('Sending auth code to backend:', API_URL + '/auth/facebook/')
    
    let backendResponse
    try {
      backendResponse = await fetch(`${API_URL}/auth/facebook/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          redirect_uri: redirectUri,
        }),
      })
    } catch (fetchError) {
      console.error('Network error during auth:', fetchError)
      throw new Error(`Network error: Could not connect to server. Please try again.`)
    }

    if (!backendResponse.ok) {
      let errorMessage = 'Backend authentication failed'
      try {
        const errorData = await backendResponse.json()
        errorMessage = errorData.error || errorData.detail || errorMessage
      } catch (e) {
        errorMessage = `Server error (${backendResponse.status})`
      }
      throw new Error(errorMessage)
    }

    const data = await backendResponse.json()
    
    // Store token and user
    token.value = data.token
    user.value = data.user
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('user_data', JSON.stringify(data.user))
    
    // Store Facebook access token for features like invite friends
    if (data.facebook_access_token) {
      facebookAccessToken.value = data.facebook_access_token
      localStorage.setItem('fb_access_token', data.facebook_access_token)
    }
    
    console.log('Login successful:', data)
    
    // Clean URL (remove code and state params)
    window.history.replaceState({}, document.title, window.location.pathname)
    
    return {
      success: true,
      user: data.user,
      isNewUser: data.is_new_user,
      facebookData: data.facebook_data,
    }

  } catch (err) {
    console.error('Facebook callback error:', err)
    error.value = err.message
    
    // Clean URL even on error
    window.history.replaceState({}, document.title, window.location.pathname)
    
    return {
      success: false,
      error: err.message,
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * Check if current URL is a Facebook callback
 */
const isFacebookCallback = () => {
  return window.location.pathname === '/auth/facebook/callback' && 
         (window.location.search.includes('code=') || window.location.search.includes('error='))
}

/**
 * Mock login for development without Facebook App ID
 */
const mockLogin = async (provider) => {
  isLoading.value = true
  error.value = null

  try {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500))

    // Mock user data
    const mockUser = {
      id: 1,
      username: `${provider}_user_123`,
      email: 'user@example.com',
      first_name: 'Demo',
      last_name: 'User',
      social_provider: provider,
      is_verified: true,
      is_onboarded: false, // New users need to complete onboarding
      is_profile_complete: false,
    }

    const mockToken = 'mock_token_' + Date.now()

    token.value = mockToken
    user.value = mockUser
    localStorage.setItem('auth_token', mockToken)
    localStorage.setItem('user_data', JSON.stringify(mockUser))

    return {
      success: true,
      user: mockUser,
      isNewUser: true,
      isMock: true,
    }

  } catch (err) {
    error.value = err.message
    return {
      success: false,
      error: err.message,
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * Main login function - uses real or mock based on configuration
 */
const login = async (provider) => {
  if (provider === 'facebook' && FACEBOOK_APP_ID) {
    // Try real Facebook login
    const result = await loginWithFacebook()
    
    // If Facebook login failed for any reason, fall back to mock
    if (!result.success) {
      console.warn('Facebook login failed, falling back to mock login for development:', result.error)
      return mockLogin(provider)
    }
    
    return result
  } else {
    // Use mock login if no Facebook App ID configured
    console.warn('Facebook App ID not configured, using mock login')
    return mockLogin(provider)
  }
}

/**
 * Login as a guest using a pre-seeded mock user
 * Calls the backend guest login endpoint
 */
const loginAsGuest = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await fetch(`${API_URL}/auth/guest/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      let errorMessage = 'Guest login failed'
      try {
        const errorData = await response.json()
        errorMessage = errorData.error || errorData.detail || errorMessage
      } catch (e) {
        errorMessage = `Server error (${response.status})`
      }
      throw new Error(errorMessage)
    }

    const data = await response.json()

    // Store token and user
    token.value = data.token
    user.value = data.user
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('user_data', JSON.stringify(data.user))

    return {
      success: true,
      user: data.user,
      isNewUser: data.is_new_user,
      isGuest: true,
    }

  } catch (err) {
    console.error('Guest login error:', err)
    error.value = err.message
    return {
      success: false,
      error: err.message,
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * Logout - clear auth state
 */
const logout = async () => {
  try {
    // Call backend logout if we have a token
    if (token.value) {
      await fetch(`${API_URL}/auth/logout/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token.value}`,
          'Content-Type': 'application/json',
        },
      }).catch(() => {})  // Ignore errors
    }

    // Logout from Facebook if SDK is loaded
    if (window.FB) {
      window.FB.logout(() => {})
    }
  } finally {
    // Clear local state
    token.value = null
    user.value = null
    facebookAccessToken.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('fb_access_token')
  }
}

/**
 * Validate existing token and fetch user data
 */
const validateToken = async () => {
  if (!token.value) return false

  try {
    const response = await fetch(`${API_URL}/auth/validate/`, {
      headers: {
        'Authorization': `Token ${token.value}`,
      },
    })

    if (response.ok) {
      const data = await response.json()
      
      // Merge server data with saved data to preserve is_onboarded status
      const savedUser = loadSavedUser()
      const mergedUser = {
        ...savedUser,
        ...data.user,
        // Preserve is_onboarded if it was true locally (in case backend doesn't track it)
        is_onboarded: data.user.is_onboarded || savedUser?.is_onboarded || false,
      }
      
      user.value = mergedUser
      localStorage.setItem('user_data', JSON.stringify(mergedUser))
      return true
    } else {
      // Token is invalid, clear it
      logout()
      return false
    }
  } catch (err) {
    console.error('Token validation error:', err)
    // On network error, still use cached user data if available
    if (user.value) {
      return true
    }
    return false
  }
}

/**
 * Update user language preference
 */
const updateLanguage = async (language) => {
  if (!token.value) return

  try {
    await fetch(`${API_URL}/auth/language/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ language }),
    })
  } catch (err) {
    console.error('Failed to update language:', err)
  }
}

/**
 * Composable export
 */
export function useAuth() {
  return {
    // State
    user,
    token,
    facebookAccessToken,
    isLoading,
    error,
    isAuthenticated,
    facebookSDKLoaded,
    
    // Actions
    login,
    loginWithFacebook,
    loginAsGuest,
    handleFacebookCallback,
    isFacebookCallback,
    mockLogin,
    logout,
    validateToken,
    updateLanguage,
    initFacebookSDK,
    
    // Config
    hasFacebookConfig: computed(() => !!FACEBOOK_APP_ID),
    apiUrl: API_URL,
  }
}
