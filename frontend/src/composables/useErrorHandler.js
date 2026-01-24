/**
 * useErrorHandler Composable - Error handling with Sentry integration
 * Reports errors to Sentry and provides navigation to main page on critical errors
 */

import * as Sentry from '@sentry/vue'
import { useRouter } from 'vue-router'
import { ROUTES } from '../router'

// Check if Sentry is initialized
let sentryInitialized = false

/**
 * Initialize Sentry with Vue integration
 * Should be called once during app startup
 */
export function initSentry(app, router) {
  const dsn = import.meta.env.VITE_SENTRY_DSN
  
  if (!dsn) {
    console.warn('[Sentry] No DSN configured. Error reporting disabled.')
    return
  }
  
  try {
    Sentry.init({
      app,
      dsn,
      integrations: [
        Sentry.browserTracingIntegration({ router }),
        Sentry.replayIntegration(),
      ],
      // Set tracesSampleRate to 1.0 to capture 100% of transactions for performance monitoring.
      tracesSampleRate: import.meta.env.PROD ? 0.2 : 1.0,
      // Capture Replay for 10% of all sessions, plus 100% of sessions with errors
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
      // Environment
      environment: import.meta.env.MODE,
      // Only send errors in production by default
      enabled: import.meta.env.PROD || import.meta.env.VITE_SENTRY_ENABLED === 'true',
    })
    
    sentryInitialized = true
    console.log('[Sentry] Initialized successfully')
  } catch (err) {
    console.error('[Sentry] Failed to initialize:', err)
  }
}

/**
 * Report an error to Sentry with additional context
 */
export function reportError(error, context = {}) {
  // Always log to console for debugging
  console.error('[Error]', error, context)
  
  if (!sentryInitialized) {
    return
  }
  
  try {
    // Add extra context to the error
    Sentry.withScope((scope) => {
      // Add context as tags and extra data
      if (context.source) {
        scope.setTag('error_source', context.source)
      }
      if (context.action) {
        scope.setTag('action', context.action)
      }
      if (context.userId) {
        scope.setUser({ id: context.userId })
      }
      
      // Add any extra data
      Object.entries(context).forEach(([key, value]) => {
        if (!['source', 'action', 'userId'].includes(key)) {
          scope.setExtra(key, value)
        }
      })
      
      // Capture the error
      if (error instanceof Error) {
        Sentry.captureException(error)
      } else {
        Sentry.captureMessage(String(error), 'error')
      }
    })
  } catch (sentryError) {
    console.error('[Sentry] Failed to report error:', sentryError)
  }
}

/**
 * useErrorHandler composable for Vue components
 */
export function useErrorHandler() {
  const router = useRouter()
  
  /**
   * Handle a critical error - report to Sentry and redirect to main page
   * @param {Error|string} error - The error to handle
   * @param {Object} context - Additional context for the error
   * @param {boolean} redirect - Whether to redirect to login page (default: true)
   */
  const handleCriticalError = (error, context = {}, redirect = true) => {
    reportError(error, {
      ...context,
      isCritical: true,
    })
    
    if (redirect) {
      // Clear auth state on critical errors
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')
      
      // Navigate to login page
      router.push({ name: ROUTES.LOGIN })
    }
  }
  
  /**
   * Handle a non-critical error - report to Sentry but don't redirect
   * @param {Error|string} error - The error to handle
   * @param {Object} context - Additional context for the error
   */
  const handleError = (error, context = {}) => {
    reportError(error, context)
  }
  
  /**
   * Wrap an async function with error handling
   * @param {Function} fn - The async function to wrap
   * @param {Object} options - Options for error handling
   * @returns {Function} Wrapped function
   */
  const withErrorHandling = (fn, options = {}) => {
    const { 
      source = 'unknown',
      critical = false,
      redirect = true,
      onError = null,
    } = options
    
    return async (...args) => {
      try {
        return await fn(...args)
      } catch (error) {
        const context = { source, args: args.length > 0 ? args : undefined }
        
        if (critical) {
          handleCriticalError(error, context, redirect)
        } else {
          handleError(error, context)
        }
        
        if (onError) {
          onError(error)
        }
        
        return null
      }
    }
  }
  
  return {
    handleError,
    handleCriticalError,
    withErrorHandling,
    reportError,
  }
}

export default {
  initSentry,
  reportError,
  useErrorHandler,
}
