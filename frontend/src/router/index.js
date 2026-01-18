/**
 * Vue Router configuration for Nomi
 * Provides URL-based navigation with history support
 */
import { createRouter, createWebHistory } from 'vue-router'
import { defineComponent, h } from 'vue'

// Empty component for routes (App.vue handles rendering)
const EmptyView = defineComponent({
  name: 'EmptyView',
  render: () => null
})

// Route names as constants for type safety
export const ROUTES = {
  LOGIN: 'login',
  LANGUAGE: 'language',
  ONBOARDING: 'onboarding',
  LOOKING_FOR: 'lookingFor',
  DISCOVERY: 'discovery',
  MATCHES: 'matches',
  CHAT: 'chat',
  PROFILE: 'profile',
  AUTH_CALLBACK: 'authCallback',
}

// Route definitions
const routes = [
  {
    path: '/',
    name: ROUTES.LOGIN,
    component: EmptyView,
    meta: { requiresAuth: false, title: 'Welcome' }
  },
  {
    path: '/auth/facebook/callback',
    name: ROUTES.AUTH_CALLBACK,
    component: EmptyView,
    meta: { requiresAuth: false, title: 'Logging in...' }
  },
  {
    path: '/language',
    redirect: '/onboarding'  // Hebrew only - skip language selection
  },
  {
    path: '/onboarding',
    name: ROUTES.ONBOARDING,
    component: EmptyView,
    meta: { requiresAuth: true, title: 'The Deets' }
  },
  {
    path: '/looking-for',
    name: ROUTES.LOOKING_FOR,
    component: EmptyView,
    meta: { requiresAuth: true, title: 'Looking For' }
  },
  {
    path: '/discovery',
    name: ROUTES.DISCOVERY,
    component: EmptyView,
    meta: { requiresAuth: true, requiresOnboarding: true, title: 'Discover' }
  },
  {
    path: '/matches',
    name: ROUTES.MATCHES,
    component: EmptyView,
    meta: { requiresAuth: true, requiresOnboarding: true, title: 'Matches' }
  },
  {
    path: '/chat/:matchId?',
    name: ROUTES.CHAT,
    component: EmptyView,
    meta: { requiresAuth: true, requiresOnboarding: true, title: 'Chat' }
  },
  {
    path: '/profile',
    name: ROUTES.PROFILE,
    component: EmptyView,
    meta: { requiresAuth: true, title: 'Profile' }
  },
  // Catch-all redirect to login
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  const isAuthenticated = !!token
  
  // Get stored onboarding status (will be updated by app)
  const userDataStr = localStorage.getItem('user_data')
  let isOnboarded = false
  try {
    const userData = userDataStr ? JSON.parse(userDataStr) : null
    isOnboarded = userData?.is_onboarded || false
  } catch (e) {
    // Ignore parse errors
  }
  
  // Handle auth callback - always allow
  if (to.name === ROUTES.AUTH_CALLBACK) {
    next()
    return
  }
  
  // If route requires auth but user is not authenticated
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: ROUTES.LOGIN })
    return
  }
  
  // If route requires onboarding but user hasn't completed it
  if (to.meta.requiresOnboarding && !isOnboarded && isAuthenticated) {
    next({ name: ROUTES.ONBOARDING })
    return
  }
  
  // If user is authenticated and tries to go to login, redirect to discovery
  if (to.name === ROUTES.LOGIN && isAuthenticated) {
    if (isOnboarded) {
      next({ name: ROUTES.DISCOVERY })
    } else {
      next({ name: ROUTES.ONBOARDING })
    }
    return
  }
  
  next()
})

// Update document title based on route
router.afterEach((to) => {
  document.title = `${to.meta.title || 'Nomi'} | Nomi`
})

export default router
