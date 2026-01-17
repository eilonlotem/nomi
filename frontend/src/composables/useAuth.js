import { ref, computed } from 'vue'

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Facebook App ID - set this in .env file
const FACEBOOK_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID || ''

// Auth state
const user = ref(null)
const token = ref(localStorage.getItem('auth_token') || null)
const isLoading = ref(false)
const error = ref(null)
const isAuthenticated = computed(() => !!token.value && !!user.value)
const facebookSDKLoaded = ref(false)

/**
 * Initialize Facebook SDK with timeout
 */
const initFacebookSDK = () => {
  return new Promise((resolve, reject) => {
    if (facebookSDKLoaded.value) {
      resolve()
      return
    }

    // Set a timeout in case SDK fails to load
    const timeout = setTimeout(() => {
      reject(new Error('Facebook SDK load timeout'))
    }, 5000)

    // Load Facebook SDK
    window.fbAsyncInit = function() {
      clearTimeout(timeout)
      window.FB.init({
        appId: FACEBOOK_APP_ID,
        cookie: true,
        xfbml: true,
        version: 'v18.0'
      })
      facebookSDKLoaded.value = true
      resolve()
    }

    // Load the SDK script
    if (!document.getElementById('facebook-jssdk')) {
      const script = document.createElement('script')
      script.id = 'facebook-jssdk'
      script.src = 'https://connect.facebook.net/en_US/sdk.js'
      script.async = true
      script.defer = true
      script.onerror = () => {
        clearTimeout(timeout)
        reject(new Error('Facebook SDK failed to load'))
      }
      document.head.appendChild(script)
    } else {
      clearTimeout(timeout)
      resolve()
    }
  })
}

/**
 * Check if we're on HTTPS (required for Facebook login)
 */
const isHttps = () => {
  return window.location.protocol === 'https:' || window.location.hostname === 'localhost'
}

/**
 * Login with Facebook
 * Opens Facebook login popup and sends token to backend
 */
const loginWithFacebook = async () => {
  isLoading.value = true
  error.value = null

  try {
    // Check if we're on HTTP (not localhost) - Facebook requires HTTPS
    if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost') {
      throw new Error('Facebook login requires HTTPS. Please use HTTPS or localhost for development.')
    }

    // Initialize SDK if not already done
    await initFacebookSDK()

    // Check if FB SDK is available
    if (!window.FB) {
      throw new Error('Facebook SDK not loaded')
    }

    // Open Facebook login dialog
    const authResponse = await new Promise((resolve, reject) => {
      window.FB.login((response) => {
        if (response.authResponse) {
          resolve(response.authResponse)
        } else {
          // Check if it's the HTTPS error
          if (window.location.protocol === 'http:') {
            reject(new Error('Facebook requires HTTPS. Using mock login for development.'))
          } else {
            reject(new Error('Facebook login cancelled or failed'))
          }
        }
      }, {
        scope: 'email,public_profile,user_birthday,user_gender',
        return_scopes: true
      })
    })

    console.log('Facebook auth response:', authResponse)

    // Send access token to backend for validation and user creation
    const backendResponse = await fetch(`${API_URL}/auth/facebook/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        access_token: authResponse.accessToken,
      }),
    })

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json()
      throw new Error(errorData.error || 'Backend authentication failed')
    }

    const data = await backendResponse.json()
    
    // Store token and user
    token.value = data.token
    user.value = data.user
    localStorage.setItem('auth_token', data.token)
    
    console.log('Login successful:', data)
    
    return {
      success: true,
      user: data.user,
      isNewUser: data.is_new_user,
      facebookData: data.facebook_data,
    }

  } catch (err) {
    console.error('Facebook login error:', err)
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
    }

    const mockToken = 'mock_token_' + Date.now()

    token.value = mockToken
    user.value = mockUser
    localStorage.setItem('auth_token', mockToken)

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
    localStorage.removeItem('auth_token')
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
      user.value = data.user
      return true
    } else {
      // Token is invalid, clear it
      logout()
      return false
    }
  } catch (err) {
    console.error('Token validation error:', err)
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
    isLoading,
    error,
    isAuthenticated,
    facebookSDKLoaded,
    
    // Actions
    login,
    loginWithFacebook,
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
