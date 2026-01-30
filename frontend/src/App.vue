<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ROUTES } from './router'
import { useI18n } from './composables/useI18n'
import { useAuth } from './composables/useAuth'
import { useErrorHandler } from './composables/useErrorHandler'
import { profileApi, matchingApi, chatApi, userApi, inviteApi, clearCache, getPhotoUrl } from './services/api'

const { t, locale, isRTL, dir, setLocale, getLanguages } = useI18n()

const { 
  user, 
  isLoading: authLoading, 
  error: authError, 
  isAuthenticated,
  facebookAccessToken,
  login, 
  loginAsGuest,
  logout, 
  validateToken,
  updateLanguage,
  hasFacebookConfig,
  isFacebookCallback,
  handleFacebookCallback,
} = useAuth()

const { handleCriticalError, handleError, reportError } = useErrorHandler()

// App loading state for smoother transitions
const appLoading = ref(true)

// Global error state for user feedback
const globalError = ref(null)

// Get all available languages
const availableLanguages = getLanguages()

// Router
const router = useRouter()
const route = useRoute()

// Current view computed from route
const currentView = computed(() => {
  const routeName = route.name
  // Map route names to view names for backward compatibility
  const routeToView = {
    [ROUTES.LOGIN]: 'login',
    [ROUTES.AUTH_CALLBACK]: 'login',
    [ROUTES.LANGUAGE]: 'language',
    [ROUTES.ONBOARDING]: 'onboarding',
    [ROUTES.LOOKING_FOR]: 'onboarding-preferences',
    [ROUTES.DISCOVERY]: 'discovery',
    [ROUTES.MATCHES]: 'matches',
    [ROUTES.CHAT]: 'chat',
    [ROUTES.PROFILE]: 'profile',
  }
  return routeToView[routeName] || 'login'
})

// Navigate to a view (wrapper for router.push)
const navigateTo = (view, params = {}) => {
  const viewToRoute = {
    'login': ROUTES.LOGIN,
    'language': ROUTES.LANGUAGE,
    'onboarding': ROUTES.ONBOARDING,
    'onboarding-preferences': ROUTES.LOOKING_FOR,
    'discovery': ROUTES.DISCOVERY,
    'matches': ROUTES.MATCHES,
    'chat': ROUTES.CHAT,
    'profile': ROUTES.PROFILE,
  }
  const routeName = viewToRoute[view] || ROUTES.LOGIN
  router.push({ name: routeName, params })
}

// Onboarding stage
const onboardingStage = ref(1) // 1 = identity tags, 2 = looking for preferences

// Logged in user
const loggedInWith = ref(null) // 'facebook' or 'instagram'

// Login error message
const loginError = ref(null)

// Selected disability tags
const selectedTags = ref([])

// Accessibility settings
const a11ySettings = ref({
  textSize: 'normal', // 'normal', 'large', 'xl'
  reducedMotion: false,
  highContrast: false,
  darkMode: true, // Dark mode enabled by default
  screenReaderMode: false, // Optimizes for screen readers
  showEmojis: true, // Toggle emoji visibility
})

// Save accessibility settings to localStorage
const saveA11ySettings = () => {
  localStorage.setItem('nomi-a11y-settings', JSON.stringify(a11ySettings.value))
}

// Load accessibility settings from localStorage
const loadA11ySettings = () => {
  const saved = localStorage.getItem('nomi-a11y-settings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      Object.assign(a11ySettings.value, parsed)
    } catch (e) {
      console.warn('Failed to load accessibility settings:', e)
    }
  }
}

// Watch for changes and save
watch(a11ySettings, saveA11ySettings, { deep: true })
const showA11yPanel = ref(false)

// Current mood/energy
const currentMood = ref('open')

const moodOptions = [
  { id: 'lowEnergy', emoji: '🌙' },
  { id: 'open', emoji: '🌸' },
  { id: 'chatty', emoji: '💬' },
  { id: 'adventurous', emoji: '✨' },
]

// Vibrant interest tag color palette - cycles through diverse colors
const interestColorClasses = [
  'bg-rose-light text-rose border-rose/30',
  'bg-teal-light text-teal border-teal/30',
  'bg-violet-light text-violet border-violet/30',
  'bg-amber-light text-amber border-amber/30',
  'bg-indigo-light text-indigo border-indigo/30',
  'bg-emerald-light text-emerald border-emerald/30',
]

// User profile data (editable)
const userProfile = ref({
  name: 'Alex',
  age: 29,
  location: 'Tel Aviv',
  photo: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop',
  photos: [], // Array of uploaded photos { id, image, is_primary, order }
  bio: '',
  tags: [],
  tagVisibilities: {},
  interests: ['Music', 'Reading', 'Hiking'],
  relationshipIntent: '',
  opennessTags: [],
  promptId: 'laughMost',
  promptAnswer: '',
  // Ask Me About It - celebration prompt
  askMePromptId: '',
  askMeAnswer: '',
  // Time Preferences
  preferredTimes: [], // 'morning', 'afternoon', 'evening', 'night', 'flexible'
  responsePace: '', // 'quick', 'moderate', 'slow', 'variable'
  datePace: '', // 'ready', 'slow', 'virtual', 'flexible'
  timeNotes: '',
  lookingFor: {
    genders: [], // 'male', 'female', 'nonbinary', 'everyone'
    ageRange: { min: 18, max: 50 },
    maxDistance: 50, // km
    location: '', // City/area
  },
})

// Photo upload state
const isUploadingPhoto = ref(false)
const photoUploadError = ref(null)

// Profile saving state
const isSavingProfile = ref(false)

// Handle photo upload
const handlePhotoUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    photoUploadError.value = 'Please select an image file'
    return
  }
  
  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    photoUploadError.value = 'Image must be less than 5MB'
    return
  }
  
  isUploadingPhoto.value = true
  photoUploadError.value = null
  
  try {
    const photo = await profileApi.uploadPhoto(file)
    userProfile.value.photos = [...userProfile.value.photos, photo]
    
    // If this is the first photo and no picture_url, use it as main photo
    if (photo.is_primary || !userProfile.value.photo) {
      userProfile.value.photo = photo.image
    }
  } catch (err) {
    photoUploadError.value = err.message || 'Failed to upload photo'
  } finally {
    isUploadingPhoto.value = false
    // Reset file input
    event.target.value = ''
  }
}

// Delete photo
const deletePhoto = async (photoId) => {
  try {
    await profileApi.deletePhoto(photoId)
    userProfile.value.photos = userProfile.value.photos.filter(p => p.id !== photoId)
    
    // If we deleted the primary photo, update the main photo
    const primaryPhoto = userProfile.value.photos.find(p => p.is_primary)
    if (primaryPhoto) {
      userProfile.value.photo = primaryPhoto.image
    }
  } catch (err) {
    console.error('Failed to delete photo:', err)
  }
}

// Set photo as primary
const setPrimaryPhoto = async (photoId) => {
  try {
    await profileApi.setPrimaryPhoto(photoId)
    userProfile.value.photos = userProfile.value.photos.map(p => ({
      ...p,
      is_primary: p.id === photoId
    }))
    
    const primaryPhoto = userProfile.value.photos.find(p => p.id === photoId)
    if (primaryPhoto) {
      userProfile.value.photo = primaryPhoto.image
    }
  } catch (err) {
    console.error('Failed to set primary photo:', err)
  }
}

// Get primary photo URL for profile editing
const getPrimaryPhotoUrl = () => {
  // First check if there's a primary photo in the photos array
  const primaryPhoto = userProfile.value.photos?.find(p => p.is_primary)
  if (primaryPhoto) {
    return getPhotoUrl(primaryPhoto)
  }
  // Fall back to the main photo field
  if (userProfile.value.photo) {
    return getPhotoUrl(userProfile.value.photo)
  }
  return ''
}

// Photo carousel for discovery cards
const currentPhotoIndex = ref(0)

// Get all photos for a profile (including picture_url and uploaded photos)
const getAllPhotos = (profile) => {
  if (!profile) return []
  
  const photos = []
  
  // First, add all uploaded photos from the photos array
  const uploadedPhotos = profile.photos || []
  for (const photo of uploadedPhotos) {
    const url = getPhotoUrl(photo)
    if (url && !photos.includes(url)) {
      photos.push(url)
    }
  }
  
  // If no photos yet, add main photo (from picture_url or primary photo)
  if (photos.length === 0) {
    if (profile.photo) {
      photos.push(getPhotoUrl(profile.photo))
    } else if (profile.picture_url) {
      photos.push(getPhotoUrl(profile.picture_url))
    } else if (profile.primary_photo) {
      photos.push(getPhotoUrl(profile.primary_photo))
    }
  }
  
  return photos
}

// Navigate to next photo
const nextPhoto = () => {
  const photos = getAllPhotos(currentProfile.value)
  if (currentPhotoIndex.value < photos.length - 1) {
    currentPhotoIndex.value++
  }
}

// Navigate to previous photo
const prevPhoto = () => {
  if (currentPhotoIndex.value > 0) {
    currentPhotoIndex.value--
  }
}

// Looking for options
const genderOptions = [
  { id: 'male', emoji: '👨' },
  { id: 'female', emoji: '👩' },
  { id: 'nonbinary', emoji: '🧑' },
  { id: 'everyone', emoji: '💫' },
]

const relationshipIntentOptions = [
  { id: 'relationship', emoji: '💞' },
  { id: 'friendship', emoji: '🤝' },
  { id: 'open', emoji: '🌈' },
  { id: 'slow', emoji: '🌿' },
  { id: 'unsure', emoji: '🤔' },
]

const opennessOptions = [
  { id: 'openToCaregiver', emoji: '🤝' },
  { id: 'openToMobility', emoji: '🦽' },
  { id: 'openToMentalHealth', emoji: '💚' },
  { id: 'openToAll', emoji: '🌍' },
  { id: 'notSure', emoji: '❓' },
  { id: 'meetThenDecide', emoji: '💬' },
  { id: 'understandsDisability', emoji: '🫶' },
]

// Ask Me About It prompts
const askMePrompts = [
  { id: 'coolestThing', emoji: '✨' },
  { id: 'superpower', emoji: '💪' },
  { id: 'wishPeopleKnew', emoji: '💭' },
  { id: 'proudOf', emoji: '🏆' },
  { id: 'dontLetStop', emoji: '🚀' },
  { id: 'loveAboutCommunity', emoji: '💜' },
]

// Time preference options
const timeOptions = [
  { id: 'morning', emoji: '🌅' },
  { id: 'afternoon', emoji: '☀️' },
  { id: 'evening', emoji: '🌆' },
  { id: 'night', emoji: '🌙' },
  { id: 'flexible', emoji: '🤷' },
]

const responsePaceOptions = [
  { id: 'quick', emoji: '⚡' },
  { id: 'moderate', emoji: '🕐' },
  { id: 'slow', emoji: '🐢' },
  { id: 'variable', emoji: '🔋' },
]

const datePaceOptions = [
  { id: 'ready', emoji: '🎯' },
  { id: 'slow', emoji: '💬' },
  { id: 'virtual', emoji: '📱' },
  { id: 'flexible', emoji: '🌈' },
]

// Toggle time preference
const toggleTime = (timeId) => {
  const times = userProfile.value.preferredTimes || []
  const index = times.indexOf(timeId)
  if (index > -1) {
    times.splice(index, 1)
  } else {
    times.push(timeId)
  }
  userProfile.value.preferredTimes = times
}

const normalizeGenderList = (genders = []) => {
  const map = { men: 'male', women: 'female' }
  const normalized = (genders || [])
    .map(g => map[g] || g)
    .filter(Boolean)
  if (normalized.includes('everyone')) {
    return ['everyone']
  }
  return [...new Set(normalized)]
}


// Age range validation
const ageRangeError = ref('')

// Validate age range (show error but don't modify values while typing)
const validateAgeRange = () => {
  const range = userProfile.value.lookingFor.ageRange
  const min = Number(range.min) || 0
  const max = Number(range.max) || 0
  
  // Check for invalid range and show error
  if (min > 0 && max > 0 && min > max) {
    ageRangeError.value = t('lookingFor.ageRangeError')
  } else {
    ageRangeError.value = ''
  }
}

// Normalize age range on blur (when user finishes editing)
const normalizeAgeRange = () => {
  const range = userProfile.value.lookingFor.ageRange
  const min = Math.max(18, Math.min(99, Number(range.min) || 18))
  const max = Math.max(18, Math.min(99, Number(range.max) || 50))
  
  range.min = min
  range.max = max
  
  // Re-validate after normalization
  validateAgeRange()
}

watch(
  () => [userProfile.value.lookingFor.ageRange.min, userProfile.value.lookingFor.ageRange.max],
  validateAgeRange,
)

// Toggle looking for options
const toggleGender = (genderId) => {
  if (genderId === 'everyone') {
    // If selecting "everyone", clear other selections and just use everyone
    userProfile.value.lookingFor.genders = ['everyone']
  } else {
    // Remove "everyone" if it was selected
    const genders = userProfile.value.lookingFor.genders.filter(g => g !== 'everyone')
    const index = genders.indexOf(genderId)
    if (index > -1) {
      genders.splice(index, 1)
    } else {
      genders.push(genderId)
    }
    userProfile.value.lookingFor.genders = genders
  }
}

const setRelationshipIntent = (intentId) => {
  userProfile.value.relationshipIntent = intentId
}

const toggleOpennessTag = (tagId) => {
  const tags = userProfile.value.opennessTags || []

  if (tagId === 'openToAll') {
    userProfile.value.opennessTags = ['openToAll']
    return
  }

  if (tagId === 'notSure') {
    userProfile.value.opennessTags = ['notSure']
    return
  }

  const filtered = tags.filter(t => t !== 'openToAll' && t !== 'notSure')
  const index = filtered.indexOf(tagId)
  if (index > -1) {
    filtered.splice(index, 1)
  } else {
    filtered.push(tagId)
  }
  userProfile.value.opennessTags = filtered
}

// Available profile prompts
const profilePromptOptions = ['laughMost', 'perfectSunday', 'convinced']

// Mock profile data for discovery
const currentProfileIndex = ref(0)

// Reset photo index when profile changes
watch(currentProfileIndex, () => {
  currentPhotoIndex.value = 0
})

// Discovery profiles from backend only
const discoveryProfiles = ref([])
const noMoreProfiles = ref(false)

// Swipe hint visibility (shows for 2 seconds then hides)
const showSwipeHint = ref(true)
let swipeHintTimeout = null

// Show hint for 2 seconds when entering discovery view
watch(() => currentView.value, (newView) => {
  if (newView === 'discovery') {
    showSwipeHint.value = true
    if (swipeHintTimeout) clearTimeout(swipeHintTimeout)
    swipeHintTimeout = setTimeout(() => {
      showSwipeHint.value = false
    }, 10000)
  }
}, { immediate: true })

// Progressive disclosure - reveal levels for discovery cards
const profileRevealLevel = ref('essential') // 'essential' | 'curious' | 'deep-dive'

const cycleRevealLevel = () => {
  if (profileRevealLevel.value === 'essential') {
    profileRevealLevel.value = 'curious'
  } else if (profileRevealLevel.value === 'curious') {
    profileRevealLevel.value = 'deep-dive'
  } else {
    profileRevealLevel.value = 'essential'
  }
}

// Reset reveal level when moving to next profile
watch(currentProfileIndex, () => {
  profileRevealLevel.value = 'essential'
  // Reset photo scroll offset when changing profiles
  photoScrollOffset.value = 0
  // Reset scroll position
  if (discoveryDetailsScroll.value) {
    discoveryDetailsScroll.value.scrollTop = 0
  }
})

// Handle discovery page scroll to hide photo
const handleDiscoveryScroll = () => {
  if (!discoveryDetailsScroll.value || !discoveryPhotoCarousel.value) return
  
  const scrollTop = discoveryDetailsScroll.value.scrollTop
  const scrollHeight = discoveryDetailsScroll.value.scrollHeight
  const clientHeight = discoveryDetailsScroll.value.clientHeight
  
  // Calculate scroll percentage (0 to 1)
  const maxScroll = Math.max(1, scrollHeight - clientHeight)
  const scrollPercent = Math.min(scrollTop / maxScroll, 1)
  
  // Get photo carousel height
  const photoHeight = discoveryPhotoCarousel.value.offsetHeight
  
  // Hide up to 70% of the photo (max offset is 70% of photo height) for more detail space
  const maxOffset = photoHeight * 0.7
  photoScrollOffset.value = scrollPercent * maxOffset
}

// Match breakdown visibility
const showMatchBreakdown = ref(false)

// Discovery page scroll tracking for photo hiding
const discoveryDetailsScroll = ref(null)
const discoveryPhotoCarousel = ref(null)
const photoScrollOffset = ref(0)

// Undo functionality for swipes
const lastSwipeAction = ref(null)
const showUndoToast = ref(false)
let undoTimeout = null
const UNDO_DURATION = 4000 // 4 seconds to undo

const executeSwipe = async (action, profile) => {
  if (action === 'like') {
    const profileId = profile.user_id || profile.id
    const result = await matchingApi.swipe(profileId, 'like')
    if (result.is_match) {
      matchNotification.value = {
        name: profile.name,
        photo: profile.photo || profile.picture_url
      }
    }
  } else {
    const profileId = profile.user_id || profile.id
    await matchingApi.swipe(profileId, 'pass')
  }
}

const undoSwipe = () => {
  if (lastSwipeAction.value && undoTimeout) {
    clearTimeout(undoTimeout)
    // Restore the profile
    currentProfileIndex.value = Math.max(0, currentProfileIndex.value - 1)
    showUndoToast.value = false
    lastSwipeAction.value = null
  }
}

// Current profile - uses backend data only, normalized for template
const currentProfile = computed(() => {
  const profile = discoveryProfiles.value[currentProfileIndex.value]
  if (!profile) return null
  
  // Normalize backend profile format to match expected template format
  const primaryPhoto = profile.primary_photo?.url || profile.primary_photo?.image || profile.picture_url || 
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=500&fit=crop'
  
  return {
    ...profile,
    id: profile.user_id || profile.id,
    name: profile.display_name || 'User',
    age: profile.age || profile.user_age || 25,
    photo: primaryPhoto,
    distance: profile.distance || Math.floor(Math.random() * 20) + 1,
    bio: profile.bio || '',
    tags: (profile.disability_tags || []).map(t => typeof t === 'string' ? t : t.code),
    interests: (profile.interests || []).map(i => typeof i === 'string' ? i : i.name),
    mood: profile.current_mood || 'open',
    compatibility: profile.compatibility || 75,
    promptId: profile.prompt_id || 'laughMost',
    promptAnswer: profile.prompt_answer || '',
    relationshipIntent: profile.relationship_intent || '',
    opennessTags: profile.openness_tags || [],
    // Ask Me About It
    askMePromptId: profile.ask_me_prompt_id || '',
    askMeAnswer: profile.ask_me_answer || '',
    // Time Preferences
    preferredTimes: profile.preferred_times || [],
    responsePace: profile.response_pace || '',
    datePace: profile.date_pace || '',
    // Bot indicator
    isBot: profile.is_bot || false,
  }
})

// Shared tags with current profile
const sharedTags = computed(() => {
  if (!currentProfile.value) return []
  const profileTags = currentProfile.value.tags || []
  // Handle both array of strings and array of objects (already normalized above)
  return profileTags.filter(tag => selectedTags.value.includes(tag))
})

// Match animation state
const showMatchAnimation = ref(false)
const matchedProfile = ref(null)
const selectedMatch = ref(null)

// Disconnect/unmatch state
const showDisconnectConfirm = ref(false)
const isDisconnecting = ref(false)

// Handle disconnect from match
const handleDisconnect = async () => {
  if (!selectedMatch.value || isDisconnecting.value) return
  
  isDisconnecting.value = true
  try {
    await matchingApi.unmatch(selectedMatch.value.id)
    
    // Remove match from local state
    matches.value = matches.value.filter(m => m.id !== selectedMatch.value.id)
    
    // Clear chat state
    selectedMatch.value = null
    currentConversation.value = null
    chatMessages.value = []
    
    // Close confirmation dialog
    showDisconnectConfirm.value = false
    
    // Navigate back to matches
    navigateTo('matches')
  } catch (err) {
    console.error('Failed to disconnect:', err)
  } finally {
    isDisconnecting.value = false
  }
}

// View profile overlay state
const viewingProfile = ref(null)
const viewingProfilePhotoIndex = ref(0)
const viewingProfileImageError = ref(false)
const viewingProfileData = computed(() => {
  const profile = viewingProfile.value
  if (!profile) return null
  return {
    raw: profile,
    name: profile.name || profile.display_name || '',
    age: profile.age || profile.user_age || null,
    city: profile.city || '',
    mood: profile.mood || profile.current_mood || '',
    bio: profile.bio || '',
    askMePromptId: profile.askMePromptId || profile.ask_me_prompt_id || '',
    askMeAnswer: profile.askMeAnswer || profile.ask_me_answer || '',
    tags: profile.tags || profile.disability_tags || [],
    interests: profile.interests || [],
    relationshipIntent: profile.relationshipIntent || profile.relationship_intent || '',
    opennessTags: profile.opennessTags || profile.openness_tags || [],
    responsePace: profile.responsePace || profile.response_pace || '',
    datePace: profile.datePace || profile.date_pace || '',
  }
})

// Open user profile view
const openProfileView = (profile) => {
  viewingProfile.value = profile
  viewingProfilePhotoIndex.value = 0
  viewingProfileImageError.value = false
}

// Close profile view
const closeProfileView = () => {
  viewingProfile.value = null
}

// Navigate photos in profile view
const nextViewingPhoto = () => {
  const photos = getAllPhotos(viewingProfile.value)
  if (viewingProfilePhotoIndex.value < photos.length - 1) {
    viewingProfilePhotoIndex.value++
  }
}

const prevViewingPhoto = () => {
  if (viewingProfilePhotoIndex.value > 0) {
    viewingProfilePhotoIndex.value--
  }
}

// Matches and conversations from backend
const matches = ref([])
const conversations = ref([])

// Invite friends state
const showInviteFriendsModal = ref(false)
const facebookFriends = ref([])
const inviteFriendsLoading = ref(false)
const inviteFriendsError = ref(null)
const invitationStats = ref({ total_sent: 0, accepted: 0, pending: 0 })

// Mock chat data
// Chat state
const currentConversation = ref(null)
const chatMessages = ref([])
const showChatSidebar = ref(true)

const aiSuggestions = ref([])
const isLoadingSuggestions = ref(false)
const aiSummary = ref('')
const showSummaryModal = ref(false)
const isLoadingSummary = ref(false)
const showSuggestions = ref(false)
const chatScrollContainer = ref(null)

const saveChatSettings = () => {
  localStorage.setItem(
    'nomi-chat-settings',
    JSON.stringify({ showSuggestions: showSuggestions.value })
  )
}

const loadChatSettings = () => {
  const saved = localStorage.getItem('nomi-chat-settings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      if (typeof parsed.showSuggestions === 'boolean') {
        showSuggestions.value = parsed.showSuggestions
      }
    } catch (error) {
      console.warn('Failed to load chat settings:', error)
    }
  }
}

watch(showSuggestions, saveChatSettings)

watch(showSuggestions, async (isShown) => {
  if (isShown && currentView.value === 'chat') {
    await nextTick()
    await scrollChatToBottom('smooth')
  }
})

watch(currentView, async (view) => {
  if (view !== 'chat') return
  await scrollChatToBottom()
})

const scrollChatToBottom = async (behavior = 'auto') => {
  await nextTick()
  const container = chatScrollContainer.value
  if (!container) return
  const top = container.scrollHeight
  if (behavior === 'smooth') {
    container.scrollTo({ top, behavior })
    return
  }
  container.scrollTop = top
}

const isChatNearBottom = (threshold = 120) => {
  const container = chatScrollContainer.value
  if (!container) return true
  return container.scrollHeight - container.scrollTop - container.clientHeight < threshold
}

const chatPartner = ref({
  name: '',
  photo: '',
  isOnline: true,
  isBot: false,
})

// Legacy mockChat for compatibility (will be replaced with chatMessages)
const mockChat = computed(() => ({
  matchName: chatPartner.value.name,
  matchPhoto: chatPartner.value.photo,
  isOnline: chatPartner.value.isOnline,
  isBot: chatPartner.value.isBot,
  messages: chatMessages.value.map(msg => ({
    id: msg.id,
    sender: msg.is_mine ? 'me' : 'them',
    text: { en: msg.content, he: msg.content, es: msg.content, fr: msg.content, ar: msg.content },
    time: new Date(msg.sent_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
    sentAtMs: msg.sent_at ? new Date(msg.sent_at).getTime() : null,
    reaction: null,
    isRead: msg.is_read,
    // Voice message fields
    messageType: msg.message_type || 'text',
    audioUrl: msg.audio_url,
    audioDuration: msg.audio_duration || 0,
    isUploading: msg._uploading || false,
  })),
}))

const TIMESTAMP_GAP_MINUTES = 15

const shouldShowTimestamp = (index) => {
  const messages = mockChat.value.messages
  if (index === 0) return false
  const current = messages[index]
  const previous = messages[index - 1]
  if (!current?.sentAtMs || !previous?.sentAtMs) return false
  return (current.sentAtMs - previous.sentAtMs) > TIMESTAMP_GAP_MINUTES * 60 * 1000
}

const getMessageBubbleClasses = (message) => {
  const base = 'relative max-w-[85%] rounded-2xl px-4 py-3 shadow-soft'
  const isMine = message.sender === 'me'
  if (message.messageType === 'voice') {
    return [
      base,
      isMine
        ? 'bg-primary/10 text-text-deep border border-primary/20 rounded-br-sm'
        : 'bg-surface text-text-deep border border-border rounded-bl-sm',
    ]
  }
  return [
    base,
    isMine
      ? 'bg-primary text-white rounded-br-sm'
      : 'bg-surface text-text-deep border border-border rounded-bl-sm',
  ]
}

// Voice playback state
const playingAudioId = ref(null)
const audioPlayer = ref(null)

const playVoiceMessage = (messageId, audioUrl) => {
  // Stop current audio if playing
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value = null
  }
  
  if (playingAudioId.value === messageId) {
    // Was playing this message, now stopped
    playingAudioId.value = null
    return
  }
  
  // Play new audio
  audioPlayer.value = new Audio(audioUrl)
  playingAudioId.value = messageId
  
  audioPlayer.value.onended = () => {
    playingAudioId.value = null
    audioPlayer.value = null
  }
  
  audioPlayer.value.onerror = () => {
    playingAudioId.value = null
    audioPlayer.value = null
  }
  
  audioPlayer.value.play()
}

const formatVoiceDuration = (seconds) => {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const newMessage = ref('')

// Voice recording state
const isRecording = ref(false)
const recordingDuration = ref(0)
const recordingTimer = ref(null)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const isUploadingVoice = ref(false)

// Get best supported audio MIME type
const getSupportedMimeType = () => {
  const types = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
    'audio/mpeg',
    ''  // Empty string = browser default
  ]
  for (const type of types) {
    if (type === '' || MediaRecorder.isTypeSupported(type)) {
      return type
    }
  }
  return ''
}

// Voice recording error state
const voiceRecordingError = ref(null)

// Voice recording functions
const startRecording = async () => {
  voiceRecordingError.value = null
  
  // Check if MediaRecorder is supported
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    voiceRecordingError.value = 'Voice recording is not supported in this browser'
    console.error('MediaDevices API not supported')
    return
  }
  
  if (typeof MediaRecorder === 'undefined') {
    voiceRecordingError.value = 'Voice recording is not supported in this browser'
    console.error('MediaRecorder API not supported')
    return
  }
  
  try {
    // Request microphone with a reasonable timeout
    let stream
    try {
      // Create a promise race with a timeout
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Permission timeout')), 10000)
      })
      
      stream = await Promise.race([
        navigator.mediaDevices.getUserMedia({ audio: true }),
        timeoutPromise
      ])
    } catch (permError) {
      console.error('Permission error:', permError)
      if (permError.message === 'Permission timeout') {
        voiceRecordingError.value = 'Microphone permission timed out. Please try again.'
      } else {
        throw permError
      }
      return
    }
    
    // Get the best supported MIME type
    const mimeType = getSupportedMimeType()
    const options = mimeType ? { mimeType } : {}
    
    console.log('Starting recording with MIME type:', mimeType || 'browser default')
    
    try {
      mediaRecorder.value = new MediaRecorder(stream, options)
    } catch (recorderError) {
      // If the preferred MIME type fails, try without options
      console.warn('MediaRecorder creation failed with options, trying default:', recorderError)
      mediaRecorder.value = new MediaRecorder(stream)
    }
    
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    
    mediaRecorder.value.onstop = async () => {
      const actualMimeType = mediaRecorder.value?.mimeType || mimeType || 'audio/webm'
      const audioBlob = new Blob(audioChunks.value, { type: actualMimeType })
      
      // Stop all tracks
      stream.getTracks().forEach(track => track.stop())
      
      // Only upload if we have audio data
      if (audioBlob.size > 0) {
        await uploadVoiceMessage(audioBlob, recordingDuration.value)
      } else {
        console.warn('No audio data recorded')
        voiceRecordingError.value = 'No audio recorded'
      }
    }
    
    mediaRecorder.value.onerror = (event) => {
      console.error('MediaRecorder error:', event.error)
      voiceRecordingError.value = 'Recording failed'
      cancelRecording()
    }
    
    mediaRecorder.value.start(1000) // Collect data every second
    isRecording.value = true
    recordingDuration.value = 0
    
    // Start timer
    recordingTimer.value = setInterval(() => {
      recordingDuration.value++
      // Max recording time: 2 minutes
      if (recordingDuration.value >= 120) {
        stopRecording()
      }
    }, 1000)
    
    console.log('Recording started successfully')
    
  } catch (error) {
    console.error('Failed to start recording:', error)
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      voiceRecordingError.value = 'Microphone access denied. Please allow microphone access.'
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      voiceRecordingError.value = 'No microphone found'
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      voiceRecordingError.value = 'Microphone is in use by another app'
    } else if (error.name === 'OverconstrainedError') {
      voiceRecordingError.value = 'Microphone configuration error'
    } else {
      voiceRecordingError.value = 'Failed to start recording'
    }
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
    mediaRecorder.value.stop()
    isRecording.value = false
  }
}

const cancelRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
    
    // Stop the recorder but don't upload
    mediaRecorder.value.onstop = () => {
      const stream = mediaRecorder.value.stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
    mediaRecorder.value.stop()
    isRecording.value = false
    audioChunks.value = []
    recordingDuration.value = 0
  }
}

const uploadVoiceMessage = async (audioBlob, duration) => {
  if (!currentConversation.value) {
    console.error('No current conversation - cannot upload voice message')
    voiceRecordingError.value = 'No active conversation'
    return
  }
  
  console.log('Uploading voice message to conversation:', currentConversation.value)
  isUploadingVoice.value = true
  voiceRecordingError.value = null
  
  // Add optimistic message
  const tempId = -Date.now()
  const optimisticMsg = {
    id: tempId,
    is_mine: true,
    message_type: 'voice',
    content: '🎤 Voice message',
    audio_url: null,
    audio_duration: duration,
    sent_at: new Date().toISOString(),
    is_read: false,
    _uploading: true,
  }
  chatMessages.value = [...chatMessages.value, optimisticMsg]
  await scrollChatToBottom('smooth')
  
  try {
    const serverMsg = await chatApi.sendVoiceMessage(currentConversation.value, audioBlob, duration)
    
    // Replace optimistic message with server response
    chatMessages.value = chatMessages.value.map(m => 
      m.id === tempId ? serverMsg : m
    )
    
    if (serverMsg.id > lastSeenMessageId.value) {
      lastSeenMessageId.value = serverMsg.id
    }
  } catch (error) {
    console.error('Failed to upload voice message:', error)
    voiceRecordingError.value = 'Failed to send voice message'
    // Remove failed message
    chatMessages.value = chatMessages.value.filter(m => m.id !== tempId)
  } finally {
    isUploadingVoice.value = false
  }
}

const formatRecordingTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Message reactions
const reactions = [
  { emoji: '💜', label: 'Love' },
  { emoji: '🤗', label: 'Hug' },
  { emoji: '💪', label: 'Strength' },
  { emoji: '🌟', label: 'Shine' },
]

// Tag definitions with gradient colors (fallback when backend is unavailable)
const tagGradients = {
  difficultySeeing: 'from-emerald-500 to-teal-400',
  partialVision: 'from-emerald-500 to-teal-400',
  visionAids: 'from-emerald-500 to-teal-400',
  lightSensitivity: 'from-emerald-500 to-teal-400',
  difficultyHearing: 'from-amber-500 to-orange-400',
  partialHearing: 'from-amber-500 to-orange-400',
  hearingAids: 'from-amber-500 to-orange-400',
  noisyConversations: 'from-amber-500 to-orange-400',
  mobilityDifficulty: 'from-indigo-500 to-blue-400',
  wheelchairUser: 'from-indigo-500 to-blue-400',
  shortDistances: 'from-indigo-500 to-blue-400',
  needsAccessibility: 'from-indigo-500 to-blue-400',
  speechDifficulty: 'from-purple-500 to-pink-400',
  alternativeCommunication: 'from-purple-500 to-pink-400',
  needsTimeToSpeak: 'from-purple-500 to-pink-400',
  processingDifficulty: 'from-violet-500 to-purple-400',
  sensoryOverload: 'from-violet-500 to-purple-400',
  slowClearPace: 'from-violet-500 to-purple-400',
  calmSafeSpace: 'from-violet-500 to-purple-400',
}

const fallbackDisabilityTags = [
  {
    code: 'difficultySeeing',
    icon: '👁️',
    name_en: 'Difficulty seeing',
    name_he: 'מתקשה לראות',
    disclosure_level: 'functional',
    category: 'vision',
  },
  {
    code: 'partialVision',
    icon: '👓',
    name_en: 'Partial vision',
    name_he: 'רואה באופן חלקי',
    disclosure_level: 'functional',
    category: 'vision',
  },
  {
    code: 'visionAids',
    icon: '🦯',
    name_en: 'Use vision aids',
    name_he: 'נעזר/ת בעזרים לראייה',
    disclosure_level: 'functional',
    category: 'vision',
  },
  {
    code: 'lightSensitivity',
    icon: '🌞',
    name_en: 'Light sensitivity',
    name_he: 'רגישות לאור',
    disclosure_level: 'functional',
    category: 'vision',
  },
  {
    code: 'difficultyHearing',
    icon: '🦻',
    name_en: 'Difficulty hearing',
    name_he: 'מתקשה לשמוע',
    disclosure_level: 'functional',
    category: 'hearing',
  },
  {
    code: 'partialHearing',
    icon: '👂',
    name_en: 'Partial hearing',
    name_he: 'שומע/ת באופן חלקי',
    disclosure_level: 'functional',
    category: 'hearing',
  },
  {
    code: 'hearingAids',
    icon: '🎧',
    name_en: 'Use hearing aids',
    name_he: 'נעזר/ת בעזרים לשמיעה',
    disclosure_level: 'functional',
    category: 'hearing',
  },
  {
    code: 'noisyConversations',
    icon: '💬',
    name_en: 'Hard to follow group conversations',
    name_he: 'מתקשה בשיחות עם הרבה אנשים',
    disclosure_level: 'functional',
    category: 'hearing',
  },
  {
    code: 'mobilityDifficulty',
    icon: '🚶',
    name_en: 'Mobility challenges',
    name_he: 'קושי בהתניידות',
    disclosure_level: 'functional',
    category: 'mobility',
  },
  {
    code: 'wheelchairUser',
    icon: '♿',
    name_en: 'Wheelchair user',
    name_he: 'מתנייד/ת בכיסא גלגלים',
    disclosure_level: 'functional',
    category: 'mobility',
  },
  {
    code: 'shortDistances',
    icon: '👣',
    name_en: 'Can walk short distances',
    name_he: 'הולך/ת למרחקים קצרים',
    disclosure_level: 'functional',
    category: 'mobility',
  },
  {
    code: 'needsAccessibility',
    icon: '🧩',
    name_en: 'Need physical accommodations',
    name_he: 'זקוק/ה להתאמות פיזיות',
    disclosure_level: 'functional',
    category: 'mobility',
  },
  {
    code: 'speechDifficulty',
    icon: '🗣️',
    name_en: 'Speech difficulties',
    name_he: 'קושי בדיבור',
    disclosure_level: 'functional',
    category: 'communication',
  },
  {
    code: 'alternativeCommunication',
    icon: '🤟',
    name_en: 'Use alternative communication',
    name_he: 'מתקשר/ת בדרכים חלופיות',
    disclosure_level: 'functional',
    category: 'communication',
  },
  {
    code: 'needsTimeToSpeak',
    icon: '⏳',
    name_en: 'Need extra time to express myself',
    name_he: 'צריך/ה זמן להתנסח',
    disclosure_level: 'functional',
    category: 'communication',
  },
  {
    code: 'processingDifficulty',
    icon: '🧠',
    name_en: 'Info processing challenges',
    name_he: 'קושי בעיבוד מידע',
    disclosure_level: 'functional',
    category: 'cognitive_emotional',
  },
  {
    code: 'sensoryOverload',
    icon: '🌊',
    name_en: 'Sensitive to overload/stimuli',
    name_he: 'רגישות לעומס או גירויים',
    disclosure_level: 'functional',
    category: 'cognitive_emotional',
  },
  {
    code: 'slowClearPace',
    icon: '🐢',
    name_en: 'Need a slow, clear pace',
    name_he: 'זקוק/ה לקצב איטי וברור',
    disclosure_level: 'functional',
    category: 'cognitive_emotional',
  },
  {
    code: 'calmSafeSpace',
    icon: '🌿',
    name_en: 'Need a calm, safe space',
    name_he: 'צריך/ה מרחב רגוע ובטוח',
    disclosure_level: 'functional',
    category: 'cognitive_emotional',
  },
]


// Icebreaker prompts
const icebreakers = computed(() => [
  { id: 'comfortShow', text: t('icebreakerPrompts.comfortShow') },
  { id: 'idealDay', text: t('icebreakerPrompts.idealDay') },
  { id: 'proudOf', text: t('icebreakerPrompts.proudOf') },
])

const showIcebreakers = ref(false)

const showShortcuts = ref(false)
const savedShortcuts = ref([])
const isLoadingShortcuts = ref(false)
const shortcutsError = ref(null)
const shortcutsLoaded = ref(false)
const newShortcutTitle = ref('')
const newShortcutContent = ref('')

const savedShortcutItems = computed(() => savedShortcuts.value.map((shortcut) => ({
  ...shortcut,
  title: shortcut.title || t('shortcuts.untitled'),
  content: shortcut.content || '',
})))

// Text size class based on settings
const textSizeClass = computed(() => {
  switch (a11ySettings.value.textSize) {
    case 'large': return 'text-lg'
    case 'xl': return 'text-xl'
    default: return 'text-base'
  }
})

// Helper to get localized content
const getLocalized = (obj, fallback = '') => {
  if (!obj) return fallback
  if (typeof obj === 'string') return obj
  // Handle arrays (e.g., interests from backend) - return as-is
  if (Array.isArray(obj)) return obj
  // Handle localized objects {en: '...', he: '...'}
  return obj[locale.value] || obj.en || fallback
}

// Helper to translate interest names
const translateInterest = (interest) => {
  if (!interest) return ''
  const key = typeof interest === 'string' ? interest : interest.name
  // Try to get translated interest, fall back to original
  const translated = t(`interests.${key}`)
  // If translation key not found (returns the key itself), use original
  return translated.startsWith('interests.') ? key : translated
}

// Helper to generate accessible alt text for profile photos
const getProfilePhotoAlt = (profile, photoIndex, totalPhotos) => {
  if (!profile) return ''
  const name = profile.name || ''
  const age = profile.age || ''
  const distance = profile.distance ? `${profile.distance} ${t('discovery.distance', { km: '' }).trim()}` : ''
  
  // Get translated disability tags for screen readers
  const tags = (profile.tags || [])
    .map(tagId => getTagLabel(tagId))
    .filter(tag => tag)
    .join(', ')
  
  // Format: "Name, Age, Distance. Photo X of Y. Tags"
  let alt = `${name}, ${age}`
  if (distance) alt += `, ${distance}`
  if (totalPhotos > 1) alt += `. ${t('a11y.photoOf', { current: photoIndex + 1, total: totalPhotos })}`
  if (tags) alt += `. ${tags}`
  
  return alt
}

// Mobile keyboard detection
const isKeyboardOpen = ref(false)
const initialViewportHeight = ref(0)

onMounted(() => {
  initialViewportHeight.value = window.visualViewport?.height || window.innerHeight
  
  const handleResize = () => {
    const currentHeight = window.visualViewport?.height || window.innerHeight
    isKeyboardOpen.value = currentHeight < initialViewportHeight.value * 0.75
  }
  
  window.visualViewport?.addEventListener('resize', handleResize)
  window.addEventListener('resize', handleResize)
  
  onUnmounted(() => {
    window.visualViewport?.removeEventListener('resize', handleResize)
    window.removeEventListener('resize', handleResize)
    document.removeEventListener('keydown', handleKeyboardNavigation)
  })
})

watch(isKeyboardOpen, (isOpen) => {
  if (isOpen) {
    showIcebreakers.value = false
    showShortcuts.value = false
  }
})

// Swipe gestures for discovery
// Enhanced swipe state
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchStartTime = ref(0)
const cardOffset = ref(0)
const cardRotation = ref(0)
const isSwiping = ref(false)
const isAnimating = ref(false)
const swipeDirection = ref(null) // 'left', 'right', or null
const cardOpacity = ref(1)

// Swipe configuration
const SWIPE_THRESHOLD = 80 // Distance needed to trigger action
const VELOCITY_THRESHOLD = 0.5 // Pixels per ms for quick swipe
const MAX_ROTATION = 15 // Max rotation degrees
const RESISTANCE = 0.8 // Resistance when swiping

const handleTouchStart = (e) => {
  if (isAnimating.value) return
  const touch = e.touches ? e.touches[0] : e
  touchStartX.value = touch.clientX
  touchStartY.value = touch.clientY
  touchStartTime.value = Date.now()
  isSwiping.value = true
  swipeDirection.value = null
}

const handleTouchMove = (e) => {
  if (!isSwiping.value || isAnimating.value) return
  
  const touch = e.touches ? e.touches[0] : e
  const deltaX = touch.clientX - touchStartX.value
  const deltaY = touch.clientY - touchStartY.value
  
  // Only handle horizontal swipes (prevent scroll hijacking)
  if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaX) < 20) {
    return
  }
  
  // Prevent default to stop scrolling while swiping horizontally
  if (Math.abs(deltaX) > 10) {
    e.preventDefault()
  }
  
  // Apply resistance at edges
  const resistance = Math.abs(deltaX) > 150 ? RESISTANCE * 0.5 : RESISTANCE
  cardOffset.value = deltaX * resistance
  
  // Calculate rotation based on offset (more natural feel)
  cardRotation.value = (deltaX / 20) * (MAX_ROTATION / 10)
  cardRotation.value = Math.max(-MAX_ROTATION, Math.min(MAX_ROTATION, cardRotation.value))
  
  // Determine swipe direction for indicators
  if (deltaX > 40) {
    swipeDirection.value = 'right'
  } else if (deltaX < -40) {
    swipeDirection.value = 'left'
  } else {
    swipeDirection.value = null
  }
  
  // Fade out card slightly as it moves
  const progress = Math.min(Math.abs(deltaX) / 200, 1)
  cardOpacity.value = 1 - (progress * 0.2)
}

const handleTouchEnd = (e) => {
  if (!isSwiping.value || isAnimating.value) return
  isSwiping.value = false
  
  const touch = e.changedTouches ? e.changedTouches[0] : e
  const deltaX = touch.clientX - touchStartX.value
  const deltaY = touch.clientY - touchStartY.value
  const deltaTime = Date.now() - touchStartTime.value
  const velocity = Math.abs(deltaX) / deltaTime
  
  // Check if swipe was fast enough or far enough
  const isQuickSwipe = velocity > VELOCITY_THRESHOLD && Math.abs(deltaX) > 30
  const isFarEnough = Math.abs(cardOffset.value) > SWIPE_THRESHOLD
  
  if (isQuickSwipe || isFarEnough) {
    // Complete the swipe animation
    animateSwipeOut(deltaX > 0 ? 'right' : 'left')
    return
  }
  
  // Snap back to center with spring animation
  animateSnapBack()
}

const animateSwipeOut = (direction) => {
  isAnimating.value = true
  const targetX = direction === 'right' ? window.innerWidth : -window.innerWidth
  const targetRotation = direction === 'right' ? 30 : -30
  
  // Animate out
  const startX = cardOffset.value
  const startRotation = cardRotation.value
  const startOpacity = cardOpacity.value
  const duration = 300
  const startTime = Date.now()
  
  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    
    cardOffset.value = startX + (targetX - startX) * eased
    cardRotation.value = startRotation + (targetRotation - startRotation) * eased
    cardOpacity.value = startOpacity - (startOpacity * eased)
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      // Complete action
      if (direction === 'right') {
        connectProfile()
      } else {
        passProfile()
      }
      // Reset values
      setTimeout(() => {
        cardOffset.value = 0
        cardRotation.value = 0
        cardOpacity.value = 1
        swipeDirection.value = null
        isAnimating.value = false
      }, 50)
    }
  }
  
  requestAnimationFrame(animate)
}

const animateSnapBack = () => {
  isAnimating.value = true
  const startX = cardOffset.value
  const startRotation = cardRotation.value
  const startOpacity = cardOpacity.value
  const duration = 400
  const startTime = Date.now()
  
  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // Spring ease (overshoot slightly)
    const eased = 1 - Math.pow(1 - progress, 3) * Math.cos(progress * Math.PI * 0.5)
    
    cardOffset.value = startX * (1 - eased)
    cardRotation.value = startRotation * (1 - eased)
    cardOpacity.value = startOpacity + (1 - startOpacity) * eased
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      cardOffset.value = 0
      cardRotation.value = 0
      cardOpacity.value = 1
      swipeDirection.value = null
      isAnimating.value = false
    }
  }
  
  requestAnimationFrame(animate)
}

// Mouse support for desktop
const handleMouseDown = (e) => {
  handleTouchStart(e)
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (e) => {
  if (!isSwiping.value) return
  handleTouchMove(e)
}

const handleMouseUp = (e) => {
  handleTouchEnd(e)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

// Actions
const selectLanguage = async (lang) => {
  setLocale(lang)
  
  // Update language preference in backend
  if (isAuthenticated.value) {
    try {
      await updateLanguage(lang)
    } catch (err) {
      console.warn('Could not update language preference:', err.message)
    }
  }
  
  navigateTo('onboarding')
}

const toggleTag = (tagCode) => {
  const index = selectedTags.value.indexOf(tagCode)
  if (index === -1) {
    selectedTags.value.push(tagCode)
    ensureTagVisibility(tagCode)
  } else {
    selectedTags.value.splice(index, 1)
    delete userProfile.value.tagVisibilities[tagCode]
  }
}

const toggleProfileTag = (tagCode) => {
  const index = userProfile.value.tags.indexOf(tagCode)
  if (index === -1) {
    userProfile.value.tags.push(tagCode)
    ensureTagVisibility(tagCode)
  } else {
    userProfile.value.tags.splice(index, 1)
    delete userProfile.value.tagVisibilities[tagCode]
  }
  selectedTags.value = [...userProfile.value.tags]
}

const goToDiscovery = async () => {
  userProfile.value.tags = [...selectedTags.value]
  if (isAuthenticated.value) {
    await saveProfile()
  }
  
  navigateTo('discovery')
  
  // Fetch fresh discovery profiles based on new preferences
  if (isAuthenticated.value) {
    currentProfileIndex.value = 0
    await fetchDiscoveryProfiles()
  }
}

const passProfile = async () => {
  if (!currentProfile.value) return
  
  const profile = { ...currentProfile.value }
  
  // Record swipe in backend immediately (no delay - fixes swipes not being saved)
  if (isAuthenticated.value) {
    try {
      const profileId = profile.user_id || profile.id
      await matchingApi.swipe(profileId, 'pass')
    } catch (err) {
      console.warn('Could not record swipe:', err.message)
    }
  }
  
  // Move to next profile
  const profiles = discoveryProfiles.value.length > 0 ? discoveryProfiles.value : mockProfiles
  if (currentProfileIndex.value < profiles.length - 1) {
    currentProfileIndex.value++
  } else {
    noMoreProfiles.value = true
    if (isAuthenticated.value) {
      await fetchDiscoveryProfiles()
    }
  }
}

const connectProfile = async () => {
  // Record like in backend if authenticated
  if (isAuthenticated.value && currentProfile.value) {
    try {
      // Use user_id for backend profiles, id for mock
      const profileId = currentProfile.value.user_id || currentProfile.value.id
      const result = await matchingApi.swipe(profileId, 'like')
      if (result.is_match) {
        // It's a real match from backend!
        matchedProfile.value = {
          ...currentProfile.value,
          matchData: result.match,
        }
        showMatchAnimation.value = true
        
        // Refresh matches list
        await fetchMatches()
        
        // Advance to next profile so we don't show the matched profile again
        advanceToNextProfile()
        return
      }
      
      // Like recorded but no match - still advance to next profile
      advanceToNextProfile()
      return
    } catch (err) {
      console.warn('Could not record like:', err.message)
    }
  }
  
  // Fallback to mock match animation (for demo purposes)
  matchedProfile.value = currentProfile.value
  showMatchAnimation.value = true
}

// Helper to advance to next discovery profile
const advanceToNextProfile = async () => {
  const profiles = discoveryProfiles.value.length > 0 ? discoveryProfiles.value : mockProfiles
  if (currentProfileIndex.value < profiles.length - 1) {
    currentProfileIndex.value++
  } else {
    // No more profiles in current batch
    noMoreProfiles.value = true
    // Refresh from backend to get new profiles (excluding matched/swiped ones)
    if (isAuthenticated.value) {
      await fetchDiscoveryProfiles()
    }
  }
}

// Fetch discovery profiles from backend
const fetchDiscoveryProfiles = async () => {
  if (!isAuthenticated.value) return
  
  try {
    clearCache('/discover')
    const profiles = await matchingApi.discover()
    if (profiles && profiles.length > 0) {
      discoveryProfiles.value = profiles
      currentProfileIndex.value = 0
      noMoreProfiles.value = false
    } else {
      // Empty state is OK - user has swiped through all profiles
      noMoreProfiles.value = true
    }
  } catch (err) {
    // Report error to Sentry
    handleError(err, { source: 'fetchDiscoveryProfiles', action: 'discover' })
    
    // Check if this is an auth error (401/403) - redirect to login
    if (err.message?.includes('401') || err.message?.includes('403') || err.message?.includes('Unauthorized')) {
      handleCriticalError(err, { source: 'fetchDiscoveryProfiles', action: 'authError' }, true)
      return
    }
    
    // For other errors, set empty state but don't redirect
    noMoreProfiles.value = true
  }
}

// Fetch user's matches
const fetchMatches = async () => {
  if (!isAuthenticated.value) return
  
  try {
    // Clear cache to get fresh data
    clearCache('/matches')
    const result = await matchingApi.getMatches()
    // Handle paginated or direct array response
    if (Array.isArray(result)) {
      matches.value = result
    } else if (result?.results && Array.isArray(result.results)) {
      matches.value = result.results
    } else {
      // Empty state is OK
      matches.value = []
    }
  } catch (err) {
    // Report error to Sentry
    handleError(err, { source: 'fetchMatches', action: 'getMatches' })
    
    // Check if this is an auth error - redirect to login
    if (err.message?.includes('401') || err.message?.includes('403') || err.message?.includes('Unauthorized')) {
      handleCriticalError(err, { source: 'fetchMatches', action: 'authError' }, true)
      return
    }
    
    // For other errors, set empty state
    matches.value = []
  }
}

// Fetch user's conversations  
const fetchConversations = async () => {
  if (!isAuthenticated.value) return
  
  try {
    const result = await chatApi.getConversations()
    conversations.value = result.results || result || []
  } catch (err) {
    // Report error to Sentry
    handleError(err, { source: 'fetchConversations', action: 'getConversations' })
    
    // Check if this is an auth error - redirect to login
    if (err.message?.includes('401') || err.message?.includes('403') || err.message?.includes('Unauthorized')) {
      handleCriticalError(err, { source: 'fetchConversations', action: 'authError' }, true)
      return
    }
    
    // For other errors, set empty state
    conversations.value = []
  }
}

const fetchShortcuts = async () => {
  if (!isAuthenticated.value) return
  isLoadingShortcuts.value = true
  shortcutsError.value = null
  
  try {
    const result = await chatApi.getShortcuts()
    savedShortcuts.value = result?.results || result || []
  } catch (err) {
    console.error('Failed to fetch shortcuts:', err)
    shortcutsError.value = t('shortcuts.loadError')
    savedShortcuts.value = []
  } finally {
    shortcutsLoaded.value = true
    isLoadingShortcuts.value = false
  }
}

const ensureShortcutsLoaded = async () => {
  if (!isAuthenticated.value) return
  if (shortcutsLoaded.value || isLoadingShortcuts.value) return
  await fetchShortcuts()
}

const closeMatchAndChat = async () => {
  showMatchAnimation.value = false
  
  // Get the matched profile data
  const profile = matchedProfile.value
  if (!profile) {
    navigateTo('discovery')
    return
  }
  
  // Set up chat partner from the matched profile
  chatPartner.value = {
    name: profile.name || profile.display_name || 'Match',
    photo: profile.photo || profile.picture_url || '',
    isOnline: true,
    isBot: profile.isBot || profile.is_bot || false,
  }
  
  // Get conversation ID from the match data
  if (profile.matchData?.conversation_id) {
    currentConversation.value = profile.matchData.conversation_id
  } else if (profile.matchData?.id) {
    // Try to find the conversation from the matches list
    await fetchMatches()
    const match = matches.value.find(m => m.id === profile.matchData.id)
    if (match?.conversation_id) {
      currentConversation.value = match.conversation_id
    }
  }
  
  // Initialize chat state and load messages
  chatMessages.value = []
  lastSeenMessageId.value = 0
  if (currentConversation.value) {
    await refreshMessages()
  }
  await ensureShortcutsLoaded()
  
  navigateTo('chat')
  await scrollChatToBottom()
}

const keepDiscovering = async () => {
  showMatchAnimation.value = false
  matchedProfile.value = null
  
  // Refresh discovery profiles to ensure we don't show already-matched profiles
  if (isAuthenticated.value) {
    await fetchDiscoveryProfiles()
  }
}

const goBack = () => {
  // Use browser history when possible
  if (window.history.length > 1) {
    router.back()
  } else {
    // Fallback logic for direct URL access
    if (currentView.value === 'onboarding') {
      navigateTo('login')
      loggedInWith.value = null
    } else if (currentView.value === 'onboarding-preferences') {
      navigateTo('onboarding')
    } else if (currentView.value === 'discovery') {
      navigateTo('profile')
    } else if (currentView.value === 'matches') {
      navigateTo('discovery')
    } else if (currentView.value === 'chat') {
      navigateTo('matches')
    } else if (currentView.value === 'profile') {
      navigateTo('discovery')
    } else {
      navigateTo('discovery')
    }
  }
}

const goToPreferences = () => {
  navigateTo('onboarding-preferences')
}

const goToProfile = () => {
  navigateTo('profile')
}

const handleLogout = async () => {
  await logout()
  // Reset app state
  navigateTo('login')
  matches.value = []
  conversations.value = []
  chatMessages.value = []
  savedShortcuts.value = []
  shortcutsLoaded.value = false
  showShortcuts.value = false
  discoveryProfiles.value = []
  currentProfileIndex.value = 0
}

// Invite Friends Functions
const openInviteFriends = async () => {
  showInviteFriendsModal.value = true
  await fetchFacebookFriends()
  await fetchInvitationStats()
}

const closeInviteFriends = () => {
  showInviteFriendsModal.value = false
  inviteFriendsError.value = null
}

const fetchFacebookFriends = async () => {
  if (!facebookAccessToken.value) {
    inviteFriendsError.value = t('inviteFriends.loginRequired')
    return
  }

  inviteFriendsLoading.value = true
  inviteFriendsError.value = null

  try {
    const response = await inviteApi.getFacebookFriends(facebookAccessToken.value)
    facebookFriends.value = response.friends || []
  } catch (err) {
    console.error('Failed to fetch Facebook friends:', err)
    inviteFriendsError.value = err.message
  } finally {
    inviteFriendsLoading.value = false
  }
}

const fetchInvitationStats = async () => {
  try {
    const stats = await inviteApi.getInvitationStats()
    invitationStats.value = stats
  } catch (err) {
    console.error('Failed to fetch invitation stats:', err)
  }
}

const sendInvitation = async (friend) => {
  try {
    await inviteApi.sendInvitation(friend.id, friend.name)
    // Update the local state to show as invited
    const friendIndex = facebookFriends.value.findIndex(f => f.id === friend.id)
    if (friendIndex !== -1) {
      facebookFriends.value[friendIndex].already_invited = true
    }
    // Update stats
    invitationStats.value.total_sent++
    invitationStats.value.pending++
  } catch (err) {
    console.error('Failed to send invitation:', err)
    alert(t('inviteFriends.inviteError'))
  }
}

const shareViaFacebook = () => {
  // Open Facebook share dialog for inviting friends who aren't shown in the friends list
  const shareUrl = encodeURIComponent(window.location.origin)
  const shareText = encodeURIComponent(t('inviteFriends.shareMessage'))
  const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${shareUrl}&quote=${shareText}`
  window.open(facebookShareUrl, '_blank', 'width=600,height=400')
}

const handleCleanup = async () => {
  if (!confirm(t('profile.cleanupConfirm'))) return
  
  try {
    await matchingApi.cleanup()
    // Reset local state
    matches.value = []
    conversations.value = []
    chatMessages.value = []
    currentProfileIndex.value = 0
    noMoreProfiles.value = false
    // Refresh discovery profiles
    clearCache('/discover')
    await fetchDiscoveryProfiles()
    alert(t('profile.cleanupSuccess'))
  } catch (err) {
    console.error('Cleanup failed:', err)
    alert(t('profile.cleanupError'))
  }
}

const goToMatches = async () => {
  navigateTo('matches')
  // Refresh matches from backend
  if (isAuthenticated.value) {
    await fetchMatches()
  }
}

// Get the other user's profile from a match
const getMatchProfile = (match) => {
  // Backend returns other_profile which is the profile of the other user
  if (match.other_profile) {
    return {
      ...match.other_profile,
      name: match.other_profile.display_name || match.other_profile.name || match.other_user?.first_name || 'Unknown',
    }
  }
  
  // Fallback to other_user if available
  if (match.other_user) {
    return {
      ...match.other_user,
      name: match.other_user.first_name || match.other_user.username || 'Unknown',
    }
  }
  
  // Legacy fallback for user1/user2 structure
  const currentUserId = userProfile.value?.user_id || userProfile.value?.id
  if (match.user1_profile && match.user1_profile.user_id !== currentUserId) {
    return match.user1_profile
  }
  if (match.user2_profile && match.user2_profile.user_id !== currentUserId) {
    return match.user2_profile
  }
  
  return { name: 'Unknown', bio: '' }
}

// Get the current chat partner's profile
const getChatPartnerProfile = () => {
  if (!selectedMatch.value) {
    // Fallback to mockChat data if no match selected
    return {
      name: mockChat.matchName,
      photo: mockChat.matchPhoto,
      picture_url: mockChat.matchPhoto,
    }
  }
  return getMatchProfile(selectedMatch.value)
}

// Format match date
const formatMatchDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return t('chat.today') || 'Today'
  } else if (diffDays === 1) {
    return t('chat.yesterday') || 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Open chat with a match
const openChat = async (match) => {
  const profile = getMatchProfile(match)
  selectedMatch.value = match
  matchedProfile.value = profile
  aiSuggestions.value = []
  aiSummary.value = ''
  showSummaryModal.value = false
  
  // Set up chat partner info
  chatPartner.value = {
    name: profile.name || profile.display_name || profile.first_name || 'Unknown',
    photo: profile.picture_url || '',
    isOnline: true,
    isBot: profile.is_bot || false,
  }
  
  // Get conversation ID from match
  currentConversation.value = match.conversation_id || null
  chatMessages.value = []
  lastSeenMessageId.value = 0
  
  navigateTo('chat')

  // Load messages
  if (currentConversation.value && isAuthenticated.value) {
    await refreshMessages()
    await scrollChatToBottom()
  }

  if (currentConversation.value) {
    fetchSuggestions()
  }
  
  await ensureShortcutsLoaded()
}

// =============================================================================
// CHAT SYSTEM - Clean refactored implementation
// =============================================================================

// Track the last message ID we've seen to detect new messages
const lastSeenMessageId = ref(0)

// Load all messages from server (full refresh)
const loadMessages = async () => {
  if (!currentConversation.value) return []
  
  try {
    const response = await chatApi.getMessages(currentConversation.value)
    let messages = []
    
    if (Array.isArray(response)) {
      messages = response
    } else if (response?.results) {
      messages = response.results
    }
    
    return messages
  } catch (error) {
    console.error('Failed to load messages:', error)
    return []
  }
}

// Refresh messages from server (replaces all messages)
const refreshMessages = async () => {
  const messages = await loadMessages()
  if (messages.length > 0) {
    chatMessages.value = messages
    // Track the latest message ID
    const maxId = Math.max(...messages.map(m => m.id || 0))
    lastSeenMessageId.value = maxId
    if (currentView.value === 'chat') {
      await scrollChatToBottom()
    }
  }
}

// Check for new messages only (append new ones)
const checkForNewMessages = async () => {
  if (!currentConversation.value) return
  
  const shouldAutoScroll = isChatNearBottom()
  const messages = await loadMessages()
  if (messages.length === 0) return
  
  // Find messages newer than what we've seen
  const newMessages = messages.filter(m => m.id > lastSeenMessageId.value)
  
  if (newMessages.length > 0) {
    // Append new messages
    chatMessages.value = [...chatMessages.value, ...newMessages]
    // Update last seen
    const maxId = Math.max(...newMessages.map(m => m.id))
    lastSeenMessageId.value = maxId
    fetchSuggestions()
    if (shouldAutoScroll) {
      await scrollChatToBottom('smooth')
    }
  }
}

// Polling system
let pollingTimer = null

const startPolling = () => {
  stopPolling() // Clear any existing
  pollingTimer = setInterval(checkForNewMessages, 2500)
}

const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}


const fetchSuggestions = async (forceRefresh = false) => {
  if (!currentConversation.value) return
  isLoadingSuggestions.value = true
  try {
    const response = await chatApi.getSuggestions(
      currentConversation.value,
      locale.value,
      forceRefresh
    )
    aiSuggestions.value = response?.suggestions || []
  } catch (error) {
    aiSuggestions.value = []
  } finally {
    isLoadingSuggestions.value = false
  }
}

const fetchSummary = async () => {
  if (!currentConversation.value) return
  isLoadingSummary.value = true
  try {
    const response = await chatApi.getSummary(currentConversation.value, locale.value)
    aiSummary.value = response?.summary ? response.summary : t('chat.summaryUnavailable')
  } catch (error) {
    aiSummary.value = t('chat.summaryUnavailable')
  } finally {
    isLoadingSummary.value = false
  }
}

const openSummary = async () => {
  showSummaryModal.value = true
  await fetchSummary()
}

const sendSuggestedMessage = async (text) => {
  if (!text) return
  newMessage.value = text
  await sendMessage(text)
}

// Send a message
const sendMessage = async (overrideText = null) => {
  const rawText = (typeof overrideText === 'string' || typeof overrideText === 'number')
    ? String(overrideText)
    : newMessage.value
  const text = rawText.trim()
  if (!text || !currentConversation.value) return
  
  // Clear input immediately
  newMessage.value = ''
  
  // Add optimistic message with negative temp ID
  const tempId = -Date.now()
  const optimisticMsg = {
    id: tempId,
    content: text,
    is_mine: true,
    sent_at: new Date().toISOString(),
    is_read: false,
  }
  chatMessages.value = [...chatMessages.value, optimisticMsg]
  await scrollChatToBottom('smooth')
  
  try {
    // Send to server
    const serverMsg = await chatApi.sendMessage(currentConversation.value, text)
    
    // Replace optimistic message with server response
    chatMessages.value = chatMessages.value.map(m => 
      m.id === tempId ? serverMsg : m
    )
    
    // Update last seen ID
    if (serverMsg.id > lastSeenMessageId.value) {
      lastSeenMessageId.value = serverMsg.id
    }
    
    // Check for AI response after a short delay
    setTimeout(checkForNewMessages, 2000)
    fetchSuggestions()
    
  } catch (error) {
    console.error('Failed to send:', error)
    // Mark as failed (keep the message visible)
    chatMessages.value = chatMessages.value.map(m => 
      m.id === tempId ? { ...m, _failed: true } : m
    )
  }
}

// Send icebreaker
const sendIcebreaker = async (prompt) => {
  if (!currentConversation.value) return
  
  const tempId = -Date.now()
  const optimisticMsg = {
    id: tempId,
    content: prompt.text,
    is_mine: true,
    sent_at: new Date().toISOString(),
    is_read: false,
    isIcebreaker: true,
  }
  chatMessages.value = [...chatMessages.value, optimisticMsg]
  showIcebreakers.value = false
  
  try {
    const serverMsg = await chatApi.sendMessage(currentConversation.value, prompt.text, 'icebreaker')
    chatMessages.value = chatMessages.value.map(m => 
      m.id === tempId ? serverMsg : m
    )
    if (serverMsg.id > lastSeenMessageId.value) {
      lastSeenMessageId.value = serverMsg.id
    }
    setTimeout(checkForNewMessages, 2000)
    fetchSuggestions()
  } catch (error) {
    console.error('Failed to send icebreaker:', error)
    chatMessages.value = chatMessages.value.map(m => 
      m.id === tempId ? { ...m, _failed: true } : m
    )
  }
}

const useShortcut = (content) => {
  if (!content) return
  const separator = newMessage.value.trim().length ? '\n' : ''
  newMessage.value = `${newMessage.value}${separator}${content}`
  showShortcuts.value = false
}

const saveShortcut = async (title, content) => {
  if (!isAuthenticated.value) return
  shortcutsError.value = null

  const normalizedTitle = (title || '').trim()
  const normalizedContent = (content || '').trim()
  if (!normalizedTitle || !normalizedContent) {
    shortcutsError.value = t('shortcuts.validationError')
    return
  }

  try {
    const created = await chatApi.saveShortcut({
      title: normalizedTitle,
      content: normalizedContent,
    })
    savedShortcuts.value = [created, ...savedShortcuts.value]
    newShortcutTitle.value = ''
    newShortcutContent.value = ''
  } catch (error) {
    console.error('Failed to save shortcut:', error)
    shortcutsError.value = t('shortcuts.saveError')
  }
}

const removeShortcut = async (shortcutId) => {
  if (!isAuthenticated.value) return
  shortcutsError.value = null
  
  try {
    await chatApi.deleteShortcut(shortcutId)
    savedShortcuts.value = savedShortcuts.value.filter(s => s.id !== shortcutId)
  } catch (error) {
    console.error('Failed to remove shortcut:', error)
    shortcutsError.value = t('shortcuts.removeError')
  }
}

const toggleIcebreakers = () => {
  showIcebreakers.value = !showIcebreakers.value
  if (showIcebreakers.value) {
    showShortcuts.value = false
    showSuggestions.value = false
  }
}

const toggleShortcuts = async () => {
  showShortcuts.value = !showShortcuts.value
  if (showShortcuts.value) {
    showIcebreakers.value = false
    showSuggestions.value = false
    await ensureShortcutsLoaded()
  }
}

const toggleSuggestions = () => {
  showSuggestions.value = !showSuggestions.value
  if (showSuggestions.value) {
    showIcebreakers.value = false
    showShortcuts.value = false
    fetchSuggestions()
  }
}

// Watch for view changes to start/stop polling
watch(() => currentView.value, (newView, oldView) => {
  if (newView === 'chat') {
    startPolling()
  } else if (oldView === 'chat') {
    stopPolling()
  }
}, { immediate: true })

const toggleReaction = (messageId, emoji) => {
  const msg = chatMessages.value.find(m => m.id === messageId)
  if (msg) {
    msg.reaction = msg.reaction === emoji ? null : emoji
  }
}

const showReactionMenu = ref(null)

const toggleReactionMenu = (messageId) => {
  showReactionMenu.value = showReactionMenu.value === messageId ? null : messageId
}

const addInterest = () => {
  const interest = prompt(t('profile.addInterest'))
  if (interest && interest.trim()) {
    userProfile.value.interests.push(interest.trim())
  }
}

const removeInterest = (index) => {
  userProfile.value.interests.splice(index, 1)
}

const saveProfile = async () => {
  // Prevent double-click
  if (isSavingProfile.value) return
  
  isSavingProfile.value = true
  
  try {
    // Save profile to backend if authenticated
    if (isAuthenticated.value) {
      // Find tag IDs from codes
      const tagIds = backendTags.value
        .filter(t => selectedTags.value.includes(t.code))
        .map(t => t.id)

      const tagVisibilityPayload = Object.entries(userProfile.value.tagVisibilities)
        .map(([code, data]) => {
          const tag = availableTagByCode.value[code]
          if (!tag?.id) return null
          return {
            tag_id: tag.id,
            visibility: data.visibility,
            allowed_viewer_ids: data.allowedViewerIds || [],
          }
        })
        .filter(Boolean)
      
      await profileApi.updateProfile({
        display_name: userProfile.value.name,
        bio: userProfile.value.bio,
        city: userProfile.value.location,
        disability_tag_ids: tagIds,
        disability_tag_visibilities: tagVisibilityPayload,
        prompt_id: userProfile.value.promptId,
        prompt_answer: userProfile.value.promptAnswer,
        // Time Preferences
        preferred_times: userProfile.value.preferredTimes || [],
        response_pace: userProfile.value.responsePace,
        date_pace: userProfile.value.datePace,
        time_notes: userProfile.value.timeNotes,
        relationship_intent: userProfile.value.relationshipIntent || '',
        openness_tags: userProfile.value.opennessTags || [],
      })
      
      // Save looking for preferences
      // Normalize age range before saving (in case user didn't blur)
      normalizeAgeRange()
      
      const genders = normalizeGenderList(userProfile.value.lookingFor.genders)
      await profileApi.updateLookingFor({
        genders: genders.length ? genders : ['everyone'],
        min_age: userProfile.value.lookingFor.ageRange.min,
        max_age: userProfile.value.lookingFor.ageRange.max,
        max_distance: userProfile.value.lookingFor.maxDistance,
        preferred_location: userProfile.value.lookingFor.location,
      })
      
      // Mark onboarding as complete
      await userApi.completeOnboarding()
      
      console.log('Profile saved to backend')
    }
    
    // Always update local user state for navigation guard (even if API fails)
    if (user.value) {
      user.value.is_onboarded = true
      localStorage.setItem('user_data', JSON.stringify(user.value))
    }
    
    navigateTo('discovery')
    
    // Fetch fresh discovery profiles based on updated preferences
    if (isAuthenticated.value) {
      currentProfileIndex.value = 0
      await fetchDiscoveryProfiles()
    }
  } catch (err) {
    // Report profile save error (non-critical)
    handleError(err, { source: 'completeOnboarding', action: 'saveProfile' })
  } finally {
    isSavingProfile.value = false
  }
}

// Social login handler
const handleSocialLogin = async (provider) => {
  loginError.value = null
  
  try {
    const result = await login(provider)
    
    // If redirecting to OAuth provider, stop here (page will navigate away)
    if (result.redirecting) {
      return
    }
    
    if (result.success) {
      loggedInWith.value = provider
      
      // Update user profile with data from social login
      if (result.facebookData) {
        userProfile.value.name = result.facebookData.name || userProfile.value.name
        if (result.facebookData.picture_url) {
          userProfile.value.photo = result.facebookData.picture_url
        }
      }
      
      // Check if user has already completed onboarding
      if (user.value?.is_onboarded) {
        // Skip onboarding, go directly to discovery
        navigateTo('discovery')
        // Fetch discovery data
        await fetchDiscoveryProfiles()
        await fetchMatches()
        await fetchShortcuts()
      } else {
        // Navigate directly to onboarding (Hebrew only)
        navigateTo('onboarding')
      }
    } else {
      // Report login failure
      handleError(new Error(result.error || 'Login failed'), { 
        source: 'handleSocialLogin', 
        action: 'login',
        provider,
      })
      loginError.value = result.error || 'Login failed. Please try again.'
    }
  } catch (err) {
    // Critical login error - report but don't redirect (user is already on login page)
    handleError(err, { source: 'handleSocialLogin', action: 'unexpectedError', provider })
    loginError.value = 'An unexpected error occurred. Please try again.'
  }
}

const handleGuestLogin = async () => {
  loginError.value = null
  
  try {
    const result = await loginAsGuest()
    
    if (result.success) {
      loggedInWith.value = 'guest'
      
      // Guest user (mock_maya) is already onboarded with a complete profile
      // Go directly to discovery
      navigateTo('discovery')
      await fetchDiscoveryProfiles()
      await fetchMatches()
      await fetchShortcuts()
    } else {
      // Report guest login failure
      handleError(new Error(result.error || 'Guest login failed'), { 
        source: 'handleGuestLogin', 
        action: 'loginAsGuest',
      })
      loginError.value = result.error || 'Guest login failed. Please try again.'
    }
  } catch (err) {
    // Critical login error - report but don't redirect
    handleError(err, { source: 'handleGuestLogin', action: 'unexpectedError' })
    loginError.value = 'An unexpected error occurred. Please try again.'
  }
}

// Backend data state
const backendTags = ref([])
const backendProfiles = ref([])
const useBackendData = ref(false)

const availableDisabilityTags = computed(() => {
  const sourceTags = useBackendData.value && backendTags.value.length
    ? backendTags.value
    : fallbackDisabilityTags
  return sourceTags.map(tag => {
    const code = tag.code || tag.id
    const fallbackTag = fallbackDisabilityTags.find(t => t.code === code)
    return {
      ...tag,
      code,
      icon: tag.icon || fallbackTag?.icon || '🏷️',
      gradient: tag.gradient || tagGradients[code] || 'from-indigo-500 to-blue-400',
      disclosure_level: tag.disclosure_level || fallbackTag?.disclosure_level || 'functional',
      category: tag.category || fallbackTag?.category || 'cognitive_emotional',
    }
  })
})

const availableTagByCode = computed(() => {
  const map = {}
  availableDisabilityTags.value.forEach(tag => {
    map[tag.code] = tag
  })
  return map
})

const tagCategoryOrder = {
  functional: ['vision', 'hearing', 'mobility', 'communication', 'cognitive_emotional'],
}

const groupTagsByCategory = (tags, order) => {
  return order
    .map(category => ({
      category,
      tags: tags.filter(tag => tag.category === category),
    }))
    .filter(group => group.tags.length)
}

const functionalTagGroups = computed(() => {
  const tags = availableDisabilityTags.value.filter(tag => tag.disclosure_level === 'functional')
  return groupTagsByCategory(tags, tagCategoryOrder.functional)
})

const getTagLabel = (tagOrCode) => {
  const tag = typeof tagOrCode === 'string'
    ? availableTagByCode.value[tagOrCode]
    : tagOrCode
  if (!tag) {
    return typeof tagOrCode === 'string' ? t(`tags.${tagOrCode}`) : ''
  }
  const localeKey = `name_${locale.value}`
  return tag[localeKey] || tag.name_en || tag.name_he || tag.code
}

const getTagIcon = (tagOrCode) => {
  const tag = typeof tagOrCode === 'string'
    ? availableTagByCode.value[tagOrCode]
    : tagOrCode
  return tag?.icon || '🏷️'
}

const tagVisibilityOptions = computed(() => [
  { id: 'public', label: t('tagVisibility.public') },
  { id: 'matches', label: t('tagVisibility.matches') },
  { id: 'specific', label: t('tagVisibility.specific') },
  { id: 'hidden', label: t('tagVisibility.hidden') },
])

const getDefaultTagVisibility = () => {
  return 'public'
}

const ensureTagVisibility = (tagCode) => {
  if (!userProfile.value.tagVisibilities[tagCode]) {
    userProfile.value.tagVisibilities[tagCode] = {
      visibility: getDefaultTagVisibility(tagCode),
      allowedViewerIds: [],
    }
  }
}

const setTagVisibility = (tagCode, visibility) => {
  ensureTagVisibility(tagCode)
  userProfile.value.tagVisibilities[tagCode].visibility = visibility
  if (visibility !== 'specific') {
    userProfile.value.tagVisibilities[tagCode].allowedViewerIds = []
  }
}

// Fetch initial data from backend
// Optimized parallel data fetching
const initializeApp = async () => {
  appLoading.value = true
  globalError.value = null
  
  try {
    // Start fetching tags immediately (doesn't require auth)
    const tagsPromise = profileApi.getTags().catch((err) => {
      handleError(err, { source: 'initializeApp', action: 'fetchTags' })
      return null
    })
    
    // Validate token
    let isValid = false
    try {
      isValid = await validateToken()
    } catch (err) {
      // Token validation failed - report but don't redirect yet
      handleError(err, { source: 'initializeApp', action: 'validateToken' })
    }
    
    if (isValid && user.value) {
      loggedInWith.value = user.value.social_provider || 'facebook'
      
      // Set language from user preferences
      if (user.value.preferred_language) {
        setLocale(user.value.preferred_language)
      }
      
      // Fetch profile, tags, discovery profiles, matches, and conversations in parallel
      // Track which requests fail for error reporting
      let profileError = null
      let discoverError = null
      let matchesError = null
      let conversationsError = null
      let shortcutsLoadError = null
      
      const [profile, tagsResponse, discoverResponse, matchesResponse, conversationsResponse, shortcutsResponse] = await Promise.all([
        profileApi.getMyProfile().catch((err) => {
          profileError = err
          return null
        }),
        tagsPromise,
        matchingApi.discover().catch((err) => {
          discoverError = err
          return []
        }),
        matchingApi.getMatches().catch((err) => {
          matchesError = err
          return { results: [] }
        }),
        chatApi.getConversations().catch((err) => {
          conversationsError = err
          return { results: [] }
        }),
        chatApi.getShortcuts().catch((err) => {
          shortcutsLoadError = err
          return []
        }),
      ])
      
      // Report non-critical errors
      if (profileError) {
        handleError(profileError, { source: 'initializeApp', action: 'fetchProfile' })
      }
      if (discoverError) {
        handleError(discoverError, { source: 'initializeApp', action: 'fetchDiscover' })
      }
      if (matchesError) {
        handleError(matchesError, { source: 'initializeApp', action: 'fetchMatches' })
      }
      if (conversationsError) {
        handleError(conversationsError, { source: 'initializeApp', action: 'fetchConversations' })
      }
      if (shortcutsLoadError) {
        handleError(shortcutsLoadError, { source: 'initializeApp', action: 'fetchShortcuts' })
      }
      
      // Check for critical failure - if profile fetch failed and we have no data
      if (profileError && !profile) {
        // Report as critical error and redirect to login
        handleCriticalError(
          new Error('Failed to load user profile'),
          { 
            source: 'initializeApp', 
            action: 'criticalProfileFailure',
            originalError: profileError.message,
          },
          true // redirect to login
        )
        return
      }
      
      // Process tags
      if (tagsResponse && (tagsResponse.results || tagsResponse.length)) {
        backendTags.value = tagsResponse.results || tagsResponse
        useBackendData.value = true
      }
      
      // Process discovery profiles (empty state is OK)
      if (discoverResponse && discoverResponse.length > 0) {
        discoveryProfiles.value = discoverResponse
        noMoreProfiles.value = false
      } else {
        noMoreProfiles.value = true
      }
      
      // Process matches (empty state is OK)
      matches.value = matchesResponse?.results || matchesResponse || []
      
      // Process conversations (empty state is OK)
      conversations.value = conversationsResponse?.results || conversationsResponse || []
      
      // Process shortcuts (empty state is OK)
      savedShortcuts.value = shortcutsResponse?.results || shortcutsResponse || []
      shortcutsLoaded.value = true
      
      // Process profile
      if (profile) {
        const visibilityMap = {}
        ;(profile.disability_tag_visibilities || []).forEach(entry => {
          if (entry.tag?.code) {
            visibilityMap[entry.tag.code] = {
              visibility: entry.visibility || 'public',
              allowedViewerIds: entry.allowed_viewer_ids || [],
            }
          }
        })

        userProfile.value = {
          ...userProfile.value,
          name: profile.display_name || userProfile.value.name,
          bio: profile.bio || '',
          location: profile.city || userProfile.value.location,
          tags: (profile.disability_tags || []).map(t => t.code),
          tagVisibilities: visibilityMap,
          interests: (profile.interests || []).map(i => i.name),
          relationshipIntent: profile.relationship_intent || '',
          opennessTags: profile.openness_tags || [],
          promptId: profile.prompt_id || userProfile.value.promptId,
          promptAnswer: profile.prompt_answer || '',
          age: profile.age || userProfile.value.age,
          photo: profile.picture_url || userProfile.value.photo,
          // Ask Me About It
          askMePromptId: profile.ask_me_prompt_id || '',
          askMeAnswer: profile.ask_me_answer || '',
          // Time Preferences
          preferredTimes: profile.preferred_times || [],
          responsePace: profile.response_pace || '',
          datePace: profile.date_pace || '',
          timeNotes: profile.time_notes || '',
          // Photos
          photos: profile.photos || [],
        }
        selectedTags.value = [...userProfile.value.tags]
        selectedTags.value.forEach(tagCode => ensureTagVisibility(tagCode))
        currentMood.value = profile.current_mood || 'open'
        
        // Load looking for preferences
        if (profile.looking_for) {
          userProfile.value.lookingFor = {
            genders: normalizeGenderList(profile.looking_for.genders || []),
            ageRange: {
              min: profile.looking_for.min_age || 18,
              max: profile.looking_for.max_age || 50,
            },
            maxDistance: profile.looking_for.max_distance || 50,
            location: profile.looking_for.preferred_location || '',
          }
        }
      }
      
      // Skip onboarding if user has already completed it
      if (user.value.is_onboarded) {
        navigateTo('discovery')
      } else {
        navigateTo('onboarding')
      }
    } else {
      // Not authenticated, just fetch tags
      const tagsResponse = await tagsPromise
      if (tagsResponse && (tagsResponse.results || tagsResponse.length)) {
        backendTags.value = tagsResponse.results || tagsResponse
        useBackendData.value = true
      }
    }
  } catch (err) {
    // Critical error during initialization - report and redirect to login
    handleCriticalError(err, { 
      source: 'initializeApp', 
      action: 'unexpectedError',
    }, true)
  } finally {
    appLoading.value = false
  }
}

// Keyboard navigation handler for discovery and profile save
const handleKeyboardNavigation = (event) => {
  // Handle Cmd+S / Ctrl+S for saving profile
  if ((event.metaKey || event.ctrlKey) && event.key === 's') {
    event.preventDefault()
    if (currentView.value === 'profile' || currentView.value === 'preferences') {
      saveProfile()
    }
    return
  }
  
  // Only handle arrow key events when on discovery page
  if (currentView.value !== 'discovery' || !currentProfile.value) return
  
  // Don't handle if user is typing in an input
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return
  
  switch (event.key) {
    case 'ArrowLeft':
      // RTL: Left arrow = Like (in RTL, left is like)
      // LTR: Left arrow = Pass
      event.preventDefault()
      if (dir.value === 'rtl') {
        connectProfile()
      } else {
        passProfile()
      }
      break
    case 'ArrowRight':
      // RTL: Right arrow = Pass
      // LTR: Right arrow = Like
      event.preventDefault()
      if (dir.value === 'rtl') {
        passProfile()
      } else {
        connectProfile()
      }
      break
    case ' ':
      // Space = Undo (if available)
      event.preventDefault()
      // Undo functionality - go back to previous profile if possible
      if (currentProfileIndex.value > 0) {
        currentProfileIndex.value--
      }
      break
    case 'Escape':
      // Escape = Go back
      event.preventDefault()
      goBack()
      break
    case 'Enter':
      // Enter = Open profile detail view
      event.preventDefault()
      openProfileView(currentProfile.value)
      break
  }
}

// Check for existing auth on mount
onMounted(async () => {
  // Add keyboard navigation listener
  document.addEventListener('keydown', handleKeyboardNavigation)
  
  // Load saved accessibility settings
  loadA11ySettings()
  loadChatSettings()
  
  try {
    // Check if this is a Facebook OAuth callback
    if (isFacebookCallback()) {
      console.log('Handling Facebook OAuth callback...')
      appLoading.value = true
      
      const result = await handleFacebookCallback()
      
      if (result.success) {
        loggedInWith.value = 'facebook'
        
        // Update user profile with data from social login
        if (result.facebookData) {
          userProfile.value.name = result.facebookData.name || userProfile.value.name
          if (result.facebookData.picture_url) {
            userProfile.value.photo = result.facebookData.picture_url
          }
        }
        
        // Navigate based on onboarding status
        if (user.value?.is_onboarded) {
          navigateTo('discovery')
        } else {
          navigateTo('onboarding')
        }
        
        // Continue with normal initialization to load profile data
        await initializeApp()
      } else {
        // Callback failed - report and show login with error
        handleError(new Error(result.error || 'Facebook callback failed'), {
          source: 'onMounted',
          action: 'handleFacebookCallback',
        })
        loginError.value = result.error || 'Facebook login failed. Please try again.'
        appLoading.value = false
      }
    } else {
      // Normal initialization
      await initializeApp()
    }
  } catch (err) {
    // Critical error during mount - report and redirect to login
    handleCriticalError(err, { source: 'onMounted', action: 'initialization' }, true)
  }
})

// Generate constellation points for match animation
const constellationPoints = computed(() => {
  const points = []
  for (let i = 0; i < 20; i++) {
    points.push({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      delay: Math.random() * 2,
    })
  }
  return points
})
</script>

<template>
  <div 
    :dir="dir"
    :class="[
      'min-h-screen-safe font-sans text-text-deep relative overflow-x-hidden bg-background',
      currentView === 'discovery' ? 'overflow-hidden h-[100svh]' : '',
      textSizeClass,
      a11ySettings.highContrast ? 'high-contrast' : '',
      a11ySettings.darkMode ? 'dark-mode' : '',
      a11ySettings.reducedMotion ? 'reduce-motion' : '',
    ]"
  >
    <!-- App Loading State -->
    <Transition name="fade">
      <div v-if="appLoading" class="fixed inset-0 z-[100] bg-background flex items-center justify-center">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center animate-pulse">
            <span class="text-3xl">💜</span>
          </div>
          <p class="text-text-muted text-lg font-medium">{{ t('auth.connecting') }}</p>
        </div>
      </div>
    </Transition>

    <!-- Minimal background for a ChatGPT-like feel -->

    <!-- Accessibility Quick Settings Button -->
    <button
      v-if="!isKeyboardOpen"
      @click="showA11yPanel = !showA11yPanel"
      class="fixed bottom-20 xs:bottom-24 end-3 xs:end-4 z-50 bg-surface rounded-full shadow-card flex items-center gap-1.5 px-3 py-2 active:scale-95 transition-transform touch-manipulation group"
      :aria-label="t('a11y.title')"
      :title="t('a11y.title')"
    >
      <span class="text-lg">⚙️</span>
      <span class="text-xs font-medium text-text-deep hidden xs:inline">{{ t('a11y.title') }}</span>
    </button>

    <!-- Accessibility Panel -->
    <Transition name="slide-up">
      <div 
        v-if="showA11yPanel"
        class="fixed bottom-32 xs:bottom-40 end-3 xs:end-4 z-50 bg-surface rounded-2xl shadow-card p-4 w-[calc(100vw-24px)] xs:w-72 max-w-[320px] max-h-[60vh] overflow-y-auto"
        role="dialog"
        aria-modal="true"
        :aria-label="t('a11y.title')"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-text-deep flex items-center gap-2">
            <span>⚙️</span>
            {{ t('a11y.title') }}
          </h3>
          <button
            @click="showA11yPanel = false"
            class="text-text-muted hover:text-text-deep p-1"
            :aria-label="t('cancel')"
          >✕</button>
        </div>
        
        <!-- Text Size -->
        <div class="mb-4">
          <label class="text-sm text-text-muted block mb-2">
            {{ t('a11y.textSize') }}
          </label>
          <div class="flex gap-2">
            <button
              v-for="size in ['normal', 'large', 'xl']"
              :key="size"
              @click="a11ySettings.textSize = size"
              :class="[
                'flex-1 py-3 rounded-lg text-sm font-medium transition-colors touch-manipulation active:scale-95 min-h-[48px]',
                a11ySettings.textSize === size 
                  ? 'bg-primary text-white' 
                  : 'bg-background text-text-muted border border-border'
              ]"
              :aria-pressed="a11ySettings.textSize === size"
            >
              {{ size === 'normal' ? 'A' : size === 'large' ? 'A+' : 'A++' }}
            </button>
          </div>
        </div>

        <!-- High Contrast -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation min-h-[48px]">
          <div>
            <span class="text-sm block">{{ t('a11y.highContrast') }}</span>
            <span class="text-[10px] text-text-muted">{{ t('a11y.highContrastDesc') }}</span>
          </div>
          <button
            @click="a11ySettings.highContrast = !a11ySettings.highContrast"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative shrink-0',
              a11ySettings.highContrast ? 'bg-primary' : 'bg-border'
            ]"
            role="switch"
            :aria-checked="a11ySettings.highContrast"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.highContrast ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>

        <!-- Dark Mode -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation min-h-[48px]">
          <div>
            <span class="text-sm block">{{ t('a11y.darkMode') }}</span>
            <span class="text-[10px] text-text-muted">{{ t('a11y.darkModeDesc') }}</span>
          </div>
          <button
            @click="a11ySettings.darkMode = !a11ySettings.darkMode"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative shrink-0',
              a11ySettings.darkMode ? 'bg-primary' : 'bg-border'
            ]"
            role="switch"
            :aria-checked="a11ySettings.darkMode"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.darkMode ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>

        <!-- Reduced Motion -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation min-h-[48px]">
          <div>
            <span class="text-sm block">{{ t('a11y.reducedMotion') }}</span>
            <span class="text-[10px] text-text-muted">{{ t('a11y.reducedMotionDesc') }}</span>
          </div>
          <button
            @click="a11ySettings.reducedMotion = !a11ySettings.reducedMotion"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative shrink-0',
              a11ySettings.reducedMotion ? 'bg-primary' : 'bg-border'
            ]"
            role="switch"
            :aria-checked="a11ySettings.reducedMotion"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.reducedMotion ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>
        
        <!-- Screen Reader Mode -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation min-h-[48px]">
          <div>
            <span class="text-sm block">{{ t('a11y.screenReaderMode') }}</span>
            <span class="text-[10px] text-text-muted">{{ t('a11y.screenReaderModeDesc') }}</span>
          </div>
          <button
            @click="a11ySettings.screenReaderMode = !a11ySettings.screenReaderMode"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative shrink-0',
              a11ySettings.screenReaderMode ? 'bg-primary' : 'bg-border'
            ]"
            role="switch"
            :aria-checked="a11ySettings.screenReaderMode"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.screenReaderMode ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>
        
        <!-- Show Emojis Toggle -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation min-h-[48px]">
          <div>
            <span class="text-sm block">{{ t('a11y.showEmojis') }}</span>
            <span class="text-[10px] text-text-muted">{{ t('a11y.showEmojisDesc') }}</span>
          </div>
          <button
            @click="a11ySettings.showEmojis = !a11ySettings.showEmojis"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative shrink-0',
              a11ySettings.showEmojis ? 'bg-primary' : 'bg-border'
            ]"
            role="switch"
            :aria-checked="a11ySettings.showEmojis"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.showEmojis ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>
        
        <!-- Keyboard Shortcuts Info -->
        <div class="mt-4 pt-4 border-t border-border">
          <p class="text-xs text-text-muted mb-2 font-medium">{{ t('a11y.keyboardShortcuts') }}</p>
          <ul class="text-[10px] text-text-muted space-y-1">
            <li>← / → : {{ t('a11y.arrowKeysHint') }}</li>
            <li>Space : {{ t('a11y.spaceHint') }}</li>
            <li>⌘S / Ctrl+S : {{ t('a11y.saveHint') }}</li>
            <li>Enter : {{ t('a11y.enterHint') }}</li>
          </ul>
        </div>
      </div>
    </Transition>

    <!-- Login View (First Screen) -->
    <div 
      v-if="currentView === 'login'" 
      class="min-h-screen-safe flex flex-col items-center justify-center px-5 xs:px-8 py-10 xs:py-14 relative z-10"
    >
      <div class="text-center animate-slide-up w-full max-w-sm">
        <!-- Unique Organic Logo -->
        <div class="mb-8 xs:mb-10 relative">
          <!-- Animated glow rings -->
          <div class="absolute inset-0 w-28 xs:w-36 h-28 xs:h-36 mx-auto animate-breathe">
            <div class="absolute inset-0 bg-gradient-to-br from-primary/30 to-accent/20 rounded-blob animate-blob"></div>
          </div>
          <div class="absolute inset-2 w-24 xs:w-32 h-24 xs:h-32 mx-auto animate-breathe" style="animation-delay: -1s;">
            <div class="absolute inset-0 bg-gradient-to-br from-secondary/20 to-coral/20 rounded-blob-2 animate-blob-reverse"></div>
          </div>
          
          <!-- Main logo -->
          <div class="relative w-28 xs:w-36 h-28 xs:h-36 mx-auto flex items-center justify-center">
            <div class="absolute inset-0 bg-gradient-to-br from-primary via-coral to-accent rounded-[32px] rotate-3 animate-float shadow-glow"></div>
            <div class="absolute inset-[3px] bg-surface-warm rounded-[30px] rotate-3"></div>
            <span class="relative text-5xl xs:text-6xl animate-float" style="animation-delay: -0.5s;">🧡</span>
          </div>
        </div>
        
        <!-- Distinctive Typography -->
        <h1 class="font-display text-6xl xs:text-7xl font-semibold text-gradient mb-2 tracking-tight">
          {{ t('appName') }}
        </h1>
        <p class="text-lg xs:text-xl text-text-deep font-medium mb-1">{{ t('tagline') }}</p>
        
        <!-- Warm tagline with hand-drawn feel -->
        <p class="text-sm xs:text-base text-text-muted mb-12 xs:mb-14 flex items-center justify-center gap-2">
          <span class="inline-block animate-wiggle" style="animation-delay: 0s;">✿</span>
          <span class="italic">{{ t('motto') }}</span>
          <span class="inline-block animate-wiggle" style="animation-delay: 0.2s;">✿</span>
        </p>
        
        <!-- Login prompt -->
        <p class="text-sm xs:text-base text-text-muted mb-6 animate-slide-up stagger-2 font-medium">
          {{ t('auth.readyToFind') }}
        </p>

        <!-- Error Message -->
        <div 
          v-if="loginError" 
          class="mb-4 p-4 bg-red-50 border border-red-200 rounded-[16px] text-red-600 text-sm animate-slide-up"
        >
          {{ loginError }}
        </div>

        <!-- Social Login Button -->
        <div class="flex flex-col gap-4 animate-slide-up stagger-3">
          <!-- Facebook -->
          <button
            @click="handleSocialLogin('facebook')"
            :disabled="authLoading"
            class="group relative flex items-center justify-center gap-3 w-full py-5 bg-[#1877F2] text-white rounded-[20px] font-semibold shadow-soft overflow-hidden touch-manipulation active:scale-[0.98] transition-all duration-300 text-base xs:text-lg disabled:opacity-60 disabled:cursor-not-allowed"
            aria-label="Continue with Facebook"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            <!-- Loading spinner -->
            <svg v-if="authLoading && loggedInWith === null" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            <span>{{ authLoading ? t('auth.connecting') : t('auth.loginWithFacebook') }}</span>
          </button>
          
          <!-- Guest Login -->
          <button
            @click="handleGuestLogin"
            :disabled="authLoading"
            class="group relative flex items-center justify-center gap-3 w-full py-5 bg-gradient-to-r from-primary to-secondary text-white rounded-[20px] font-semibold shadow-soft overflow-hidden touch-manipulation active:scale-[0.98] transition-all duration-300 text-base xs:text-lg disabled:opacity-60 disabled:cursor-not-allowed"
            :aria-label="t('auth.loginAsGuest')"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            <!-- Loading spinner -->
            <svg v-if="authLoading && loggedInWith === 'guest'" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <!-- Guest icon -->
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>{{ authLoading && loggedInWith === 'guest' ? t('auth.connecting') : t('auth.loginAsGuest') }}</span>
          </button>
        </div>

        <!-- Dev mode indicator -->
        <div v-if="!hasFacebookConfig" class="mt-4 text-center">
          <span class="inline-flex items-center gap-1 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
            <span>⚠️</span> {{ t('auth.devMode') }}
          </span>
        </div>

        <!-- Organic divider -->
        <div class="my-8 flex items-center gap-4 animate-slide-up stagger-4">
          <div class="flex-1 h-[2px] bg-gradient-to-r from-transparent via-border to-transparent"></div>
          <span class="text-text-light text-xs font-medium">{{ t('auth.inclusive') }}</span>
          <div class="flex-1 h-[2px] bg-gradient-to-r from-transparent via-border to-transparent"></div>
        </div>

        <!-- Terms with warm styling -->
        <p class="text-xs xs:text-sm text-text-muted animate-slide-up stagger-5 leading-relaxed">
          {{ t('auth.termsText') }}
          <a href="/terms.html" target="_blank" class="text-primary font-medium hover:underline">{{ t('auth.terms') }}</a> 
          {{ t('auth.and') }}
          <a href="/privacy.html" target="_blank" class="text-primary font-medium hover:underline">{{ t('auth.privacyPolicy') }}</a>
        </p>
        
        <!-- About Us link -->
        <p class="mt-4 animate-slide-up stagger-5">
          <a href="/about.html" target="_blank" class="text-primary font-medium hover:underline text-sm">
            {{ t('auth.aboutUs') }} →
          </a>
        </p>
      </div>
    </div>

    <!-- Language Selection View -->
    <div 
      v-else-if="currentView === 'language'" 
      class="min-h-screen-safe flex flex-col relative z-10"
    >
      <!-- Organic Header -->
      <header class="sticky top-0 z-20 glass border-b border-border/50 header-safe">
        <div class="flex items-center justify-between px-4 xs:px-5 py-3 xs:py-4">
          <button
            @click="goBack"
            class="btn-icon"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <h1 class="font-display text-lg xs:text-xl font-semibold text-text-deep">{{ t('languageSelection.title') }}</h1>
          
          <div class="w-12"></div>
        </div>
      </header>

      <!-- Content -->
      <main class="flex-1 flex flex-col items-center justify-center px-5 xs:px-8 py-10">
        <div class="text-center animate-slide-up w-full max-w-sm">
          <!-- Logged in indicator with organic style -->
          <div class="mb-8 inline-flex items-center gap-3 bg-surface-warm px-5 py-3 rounded-full shadow-soft animate-bounce-soft">
            <div 
              :class="[
                'w-9 h-9 rounded-full flex items-center justify-center text-white shadow-soft',
                loggedInWith === 'facebook' ? 'bg-[#1877F2]' : 'bg-gradient-to-r from-[#F77737] via-[#E1306C] to-[#833AB4]'
              ]"
            >
              <svg v-if="loggedInWith === 'facebook'" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
              </svg>
            </div>
            <span class="text-sm font-medium text-text-deep">
              {{ loggedInWith === 'facebook' ? 'Connected' : 'Connected' }}
            </span>
            <span class="text-secondary">✓</span>
          </div>

          <!-- Globe icon with organic styling -->
          <div class="relative w-20 xs:w-24 h-20 xs:h-24 mx-auto mb-6">
            <div class="absolute inset-0 bg-gradient-to-br from-secondary/30 to-lavender/30 rounded-blob animate-blob"></div>
            <div class="relative w-full h-full flex items-center justify-center">
              <span class="text-4xl xs:text-5xl animate-float">🌍</span>
            </div>
          </div>
          
          <h2 class="font-display text-2xl xs:text-3xl font-semibold text-text-deep mb-2">
            {{ t('languageSelection.title') }}
          </h2>
          <p class="text-sm xs:text-base text-text-muted mb-10">
            {{ t('languageSelection.subtitle') }}
          </p>
          
          <!-- Language Buttons with unique organic style -->
          <div class="space-y-3">
            <button
              v-for="(lang, index) in availableLanguages"
              :key="lang.code"
              @click="selectLanguage(lang.code)"
              :class="[
                'group relative w-full py-4 xs:py-5 px-5 rounded-[20px] font-semibold transition-all duration-300 animate-slide-up touch-manipulation active:scale-[0.98]',
                index === 0 
                  ? 'bg-primary text-white shadow-button' 
                  : 'bg-surface-warm text-text-deep shadow-soft hover:shadow-card',
                `stagger-${index + 1}`
              ]"
              :aria-label="`${t('a11y.switchLanguage')} - ${lang.name}`"
            >
              <span class="flex items-center justify-center gap-4">
                <span class="text-2xl xs:text-3xl">{{ lang.flag }}</span>
                <span class="text-base xs:text-lg">{{ lang.nativeName }}</span>
              </span>
              <!-- Decorative arrow -->
              <span class="absolute end-5 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:translate-x-1">
                <svg class="w-5 h-5 flip-rtl" :class="index === 0 ? 'text-white/70' : 'text-primary'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </span>
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- Onboarding View -->
    <div 
      v-else-if="currentView === 'onboarding'" 
      class="min-h-screen-safe flex flex-col relative z-10"
    >
      <!-- Organic Header -->
      <header class="sticky top-0 z-20 glass border-b border-border/50 header-safe">
        <div class="flex items-center justify-between px-4 xs:px-5 py-3 xs:py-4">
          <button
            @click="goBack"
            class="btn-icon"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <div class="text-center">
            <h1 class="font-display text-lg xs:text-xl font-semibold text-text-deep">{{ t('onboarding.title') }}</h1>
            <p class="text-[10px] xs:text-xs text-text-muted">Step 1 of 2</p>
          </div>
          
          <button
            @click="goToDiscovery"
            class="text-primary font-semibold px-3 py-2 min-h-[48px] touch-manipulation active:opacity-70"
          >
            {{ t('skip') }}
          </button>
        </div>
      </header>
      
      <!-- Content -->
      <main class="flex-1 px-4 xs:px-5 py-6 xs:py-8 overflow-auto momentum-scroll">
        <div class="max-w-md mx-auto">
          <!-- Header with organic icon -->
          <div class="text-center mb-8 animate-slide-up">
            <div class="relative w-16 xs:w-20 h-16 xs:h-20 mx-auto mb-4">
              <div class="absolute inset-0 bg-gradient-to-br from-primary/30 to-accent/30 rounded-blob animate-blob"></div>
              <div class="relative w-full h-full flex items-center justify-center">
                <span class="text-3xl xs:text-4xl animate-float">✨</span>
              </div>
            </div>
            <h2 class="font-display text-xl xs:text-2xl font-semibold text-text-deep mb-2">
              {{ t('onboarding.subtitle') }}
            </h2>
            <p class="text-sm xs:text-base text-text-muted px-2 leading-relaxed">
              {{ t('onboarding.description') }}
            </p>
          </div>
          
          <!-- Tags Grid with unique organic styling -->
          <div class="space-y-6 mb-8">
            <div>
              <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-1">
                {{ t('onboarding.functionalTagsTitle') }}
              </h3>
              <p class="text-xs xs:text-sm text-text-muted mb-3">
                {{ t('onboarding.functionalTagsHint') }}
              </p>
              <div v-for="group in functionalTagGroups" :key="group.category" class="mb-4">
                <h4 class="text-xs uppercase tracking-wide text-text-muted mb-2">
                  {{ t(`tagCategories.${group.category}`) }}
                </h4>
                <div class="grid grid-cols-2 gap-3">
                  <button
                    v-for="(tag, index) in group.tags"
                    :key="tag.code"
                    @click="toggleTag(tag.code)"
                    :class="[
                      'group relative rounded-[18px] transition-all duration-300 animate-scale-in touch-manipulation active:scale-[0.97] overflow-hidden',
                      selectedTags.includes(tag.code) 
                        ? 'shadow-card' 
                        : 'shadow-soft hover:shadow-card',
                      `stagger-${(index % 8) + 1}`
                    ]"
                    :aria-pressed="selectedTags.includes(tag.code)"
                  >
                    <!-- Gradient background when selected -->
                    <div 
                      :class="[
                        'absolute inset-0 transition-opacity duration-300',
                        selectedTags.includes(tag.code) ? 'opacity-100' : 'opacity-0'
                      ]"
                      :style="`background: linear-gradient(135deg, ${tag.gradient.includes('pink') ? '#FAE5E0' : tag.gradient.includes('green') ? '#D8EBE2' : tag.gradient.includes('amber') ? '#FEF3C7' : '#E0E7FF'}, #fff)`"
                    ></div>
                    
                    <div 
                      :class="[
                        'relative flex items-center gap-3 px-4 py-4 min-h-[60px] transition-all',
                        selectedTags.includes(tag.code) ? '' : 'bg-surface-warm'
                      ]"
                    >
                      <span class="text-xl xs:text-2xl">{{ tag.icon }}</span>
                      <span 
                        :class="[
                          'flex-1 text-sm font-semibold leading-tight text-start',
                          selectedTags.includes(tag.code) ? 'text-text-deep' : 'text-text-muted'
                        ]"
                      >
                        {{ getTagLabel(tag) }}
                      </span>
                      <span 
                        v-if="selectedTags.includes(tag.code)"
                        class="text-primary text-lg animate-bounce-soft"
                      >
                        ✓
                      </span>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            <div v-if="selectedTags.length" class="card p-4 xs:p-5 animate-slide-up">
              <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
                <span>🔒</span> {{ t('tagVisibility.title') }}
              </h3>
              <p class="text-xs xs:text-sm text-text-muted mb-4">
                {{ t('tagVisibility.subtitle') }}
              </p>
              <div class="space-y-4">
                <div v-for="tagCode in selectedTags" :key="tagCode" class="bg-surface rounded-xl p-3 border border-border">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-lg">{{ getTagIcon(tagCode) }}</span>
                    <span class="text-sm font-semibold text-text-deep flex-1">{{ getTagLabel(tagCode) }}</span>
                    <select
                      :value="userProfile.tagVisibilities[tagCode]?.visibility || getDefaultTagVisibility(tagCode)"
                      @change="setTagVisibility(tagCode, $event.target.value)"
                      class="text-xs bg-background border border-border rounded-full px-2 py-1"
                      :aria-label="t('tagVisibility.selectAria', { tag: getTagLabel(tagCode) })"
                    >
                      <option v-for="option in tagVisibilityOptions" :key="option.id" :value="option.id">
                        {{ option.label }}
                      </option>
                    </select>
                  </div>

                  <div v-if="userProfile.tagVisibilities[tagCode]?.visibility === 'specific'" class="mt-2">
                    <p class="text-xs text-text-muted mb-2">{{ t('tagVisibility.choosePeople') }}</p>
                    <div v-if="matches.length" class="flex flex-wrap gap-2">
                      <label
                        v-for="match in matches"
                        :key="match.id"
                        class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border border-border bg-background text-xs"
                      >
                        <input
                          type="checkbox"
                          class="accent-primary"
                          :value="match.other_user?.id"
                          v-model="userProfile.tagVisibilities[tagCode].allowedViewerIds"
                        />
                        <span>{{ match.other_profile?.display_name || match.other_user?.username }}</span>
                      </label>
                    </div>
                    <p v-else class="text-xs text-text-muted">{{ t('tagVisibility.noMatches') }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Selected Count - organic pill -->
          <div 
            v-if="selectedTags.length > 0" 
            class="text-center mb-4 animate-slide-up"
          >
            <span class="inline-flex items-center gap-2 px-4 py-2 bg-secondary-light text-secondary rounded-full text-sm font-medium">
              <span>✓</span>
              {{ t('onboarding.selectedCount', { count: selectedTags.length }) }}
            </span>
          </div>
        </div>
      </main>
      
      <!-- Bottom CTA with organic style -->
      <div class="sticky bottom-0 glass border-t border-border/50 p-4 xs:p-5 bottom-bar-safe">
        <button
          @click="goToPreferences"
          class="w-full bg-primary text-white text-base xs:text-lg py-4 xs:py-5 rounded-[20px] font-semibold shadow-button touch-manipulation active:scale-[0.98] transition-all duration-300"
          :disabled="selectedTags.length === 0"
          :class="{ 'opacity-50 grayscale': selectedTags.length === 0 }"
        >
          {{ t('next') }} →
        </button>
      </div>
    </div>

    <!-- Onboarding Preferences View (Stage 2) -->
    <div 
      v-else-if="currentView === 'onboarding-preferences'" 
      class="min-h-screen-safe flex flex-col relative z-10"
    >
      <!-- Organic Header -->
      <header class="sticky top-0 z-20 glass border-b border-border/50 header-safe">
        <div class="flex items-center justify-between px-4 xs:px-5 py-3 xs:py-4">
          <button
            @click="goBack"
            class="btn-icon"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <div class="text-center">
            <h1 class="font-display text-lg xs:text-xl font-semibold text-text-deep">{{ t('lookingFor.title') }}</h1>
            <p class="text-[10px] xs:text-xs text-text-muted">{{ t('lookingFor.step') }}</p>
          </div>
          
          <button
            @click="goToDiscovery"
            class="text-primary font-medium px-2 xs:px-3 py-2 min-h-[48px] touch-manipulation active:opacity-70"
          >
            {{ t('skip') }}
          </button>
        </div>
      </header>
      
      <!-- Content -->
      <main class="flex-1 px-3 xs:px-4 py-4 xs:py-6 overflow-auto bg-background momentum-scroll">
        <div class="max-w-lg mx-auto space-y-5 xs:space-y-6">
          
          <!-- Intro -->
          <div class="text-center animate-slide-up">
            <div class="w-14 xs:w-16 h-14 xs:h-16 mx-auto bg-gradient-to-br from-pink-400 to-rose-500 rounded-xl xs:rounded-2xl flex items-center justify-center mb-3 xs:mb-4 shadow-card">
              <span class="text-2xl xs:text-3xl">💝</span>
            </div>
            <h2 class="text-lg xs:text-xl font-semibold text-text-deep mb-2">
              {{ t('lookingFor.subtitle') }}
            </h2>
            <p class="text-sm xs:text-base text-text-muted px-2">
              {{ t('lookingFor.description') }}
            </p>
          </div>

          <!-- What I'm looking for (Intent) -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-1">
            <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
              <span>🎯</span> {{ t('intent.title') }}
            </h3>
            <p class="text-xs xs:text-sm text-text-muted mb-3">
              {{ t('intent.subtitle') }}
            </p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="intent in relationshipIntentOptions"
                :key="intent.id"
                @click="setRelationshipIntent(intent.id)"
                :class="[
                  'flex items-center gap-2 px-3 xs:px-4 py-2 xs:py-2.5 rounded-full transition-all touch-manipulation active:scale-95',
                  userProfile.relationshipIntent === intent.id
                    ? 'bg-primary text-white shadow-button'
                    : 'bg-surface border-2 border-border text-text-muted hover:border-primary/50'
                ]"
              >
                <span class="text-base">{{ intent.emoji }}</span>
                <span class="text-xs xs:text-sm font-medium">{{ t(`intent.options.${intent.id}`) }}</span>
                <span v-if="userProfile.relationshipIntent === intent.id" class="text-sm">✓</span>
              </button>
            </div>
          </div>

          <!-- Openness Tags -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-1">
            <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
              <span>🤗</span> {{ t('openness.title') }}
            </h3>
            <p class="text-xs xs:text-sm text-text-muted mb-3">
              {{ t('openness.subtitle') }}
            </p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="option in opennessOptions"
                :key="option.id"
                @click="toggleOpennessTag(option.id)"
                :class="[
                  'flex items-center gap-2 px-3 xs:px-4 py-2 xs:py-2.5 rounded-full transition-all touch-manipulation active:scale-95',
                  userProfile.opennessTags.includes(option.id)
                    ? 'bg-secondary text-white shadow-button'
                    : 'bg-surface border-2 border-border text-text-muted hover:border-secondary/50'
                ]"
              >
                <span class="text-base">{{ option.emoji }}</span>
                <span class="text-xs xs:text-sm font-medium">{{ t(`openness.options.${option.id}`) }}</span>
                <span v-if="userProfile.opennessTags.includes(option.id)" class="text-sm">✓</span>
              </button>
            </div>
          </div>

          <!-- Who are you interested in? -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-1">
            <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
              <span>👥</span> {{ t('lookingFor.interestedIn') }}
            </h3>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="gender in genderOptions"
                :key="gender.id"
                @click="toggleGender(gender.id)"
                :class="[
                  'flex items-center gap-2 px-4 py-2.5 rounded-full transition-all touch-manipulation active:scale-95',
                  userProfile.lookingFor.genders.includes(gender.id)
                    ? 'bg-primary text-white shadow-button'
                    : 'bg-surface border-2 border-border text-text-muted hover:border-primary/50'
                ]"
              >
                <span class="text-base">{{ gender.emoji }}</span>
                <span class="text-sm font-medium">{{ t(`lookingFor.genders.${gender.id}`) }}</span>
              </button>
            </div>
          </div>

          <!-- Age Range -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-3">
            <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
              <span>🎂</span> {{ t('lookingFor.ageRange') }}
            </h3>
            <div class="flex items-center gap-4">
              <div class="flex-1">
                <label class="block text-xs text-text-muted mb-1.5">{{ t('lookingFor.minAge') }}</label>
                <input 
                  v-model.number="userProfile.lookingFor.ageRange.min"
                  type="number"
                  inputmode="numeric"
                  min="18"
                  max="99"
                  class="input-field text-center font-semibold text-lg"
                  @blur="normalizeAgeRange"
                />
              </div>
              <div class="text-text-muted text-2xl mt-5">–</div>
              <div class="flex-1">
                <label class="block text-xs text-text-muted mb-1.5">{{ t('lookingFor.maxAge') }}</label>
                <input 
                  v-model.number="userProfile.lookingFor.ageRange.max"
                  type="number"
                  inputmode="numeric"
                  min="18"
                  max="99"
                  class="input-field text-center font-semibold text-lg"
                  @blur="normalizeAgeRange"
                />
              </div>
            </div>
            <!-- Age Range Visual -->
            <div class="mt-3 flex items-center justify-center gap-2 text-sm text-text-muted">
              <span>{{ userProfile.lookingFor.ageRange.min }}</span>
              <div class="flex-1 h-2 bg-border rounded-full relative overflow-hidden">
                <div 
                  class="absolute h-full bg-gradient-to-r from-primary to-accent rounded-full"
                  :style="{
                    left: `${((userProfile.lookingFor.ageRange.min - 18) / 81) * 100}%`,
                    right: `${100 - ((userProfile.lookingFor.ageRange.max - 18) / 81) * 100}%`
                  }"
                ></div>
              </div>
              <span>{{ userProfile.lookingFor.ageRange.max }}</span>
            </div>
          </div>

          <!-- Location / Distance -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-4">
            <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
              <span>📍</span> {{ t('lookingFor.location') }}
            </h3>
            
            <!-- Location Input -->
            <div class="mb-4">
              <label class="block text-xs text-text-muted mb-1.5">{{ t('lookingFor.yourLocation') }}</label>
              <input 
                v-model="userProfile.lookingFor.location"
                type="text"
                class="input-field"
                :placeholder="t('lookingFor.locationPlaceholder')"
              />
            </div>
            
            <!-- Distance Slider - Accessible -->
            <div>
              <label :for="'distance-input-prefs'" class="text-xs text-text-muted block mb-2">{{ t('lookingFor.maxDistance') }}</label>
              
              <!-- Accessible distance control -->
              <div class="flex items-center gap-2 mb-2" role="group" :aria-label="t('a11y.distanceSlider', { km: userProfile.lookingFor.maxDistance })">
                <button
                  type="button"
                  @click="userProfile.lookingFor.maxDistance = Math.max(5, userProfile.lookingFor.maxDistance - 5)"
                  class="w-10 h-10 bg-surface border border-primary/30 rounded-full flex items-center justify-center text-primary font-bold touch-manipulation active:scale-90"
                  :aria-label="t('a11y.decreaseDistance')"
                >−</button>
                
                <input
                  id="distance-input-prefs"
                  v-model.number="userProfile.lookingFor.maxDistance"
                  type="number"
                  min="5"
                  max="200"
                  step="5"
                  class="w-16 text-center font-semibold text-primary bg-primary-light border border-primary/30 rounded-lg py-1"
                  @blur="userProfile.lookingFor.maxDistance = Math.min(200, Math.max(5, userProfile.lookingFor.maxDistance || 50))"
                />
                <span class="text-xs text-text-muted">{{ t('lookingFor.km') }}</span>
                
                <button
                  type="button"
                  @click="userProfile.lookingFor.maxDistance = Math.min(200, userProfile.lookingFor.maxDistance + 5)"
                  class="w-10 h-10 bg-surface border border-primary/30 rounded-full flex items-center justify-center text-primary font-bold touch-manipulation active:scale-90"
                  :aria-label="t('a11y.increaseDistance')"
                >+</button>
              </div>
              
              <input 
                v-model.number="userProfile.lookingFor.maxDistance"
                type="range"
                min="5"
                max="200"
                step="5"
                class="w-full h-2 bg-border rounded-full appearance-none cursor-pointer accent-primary"
                :aria-label="t('a11y.distanceSlider', { km: userProfile.lookingFor.maxDistance })"
              />
              <div class="flex justify-between text-[10px] text-text-muted mt-1">
                <span>5 {{ t('lookingFor.km') }}</span>
                <span>200 {{ t('lookingFor.km') }}</span>
              </div>
            </div>
          </div>

        </div>
      </main>
      
      <!-- Bottom CTA -->
      <div class="sticky bottom-0 bg-surface/90 backdrop-blur-lg border-t border-border p-3 xs:p-4 bottom-bar-safe">
        <button
          @click="goToDiscovery"
          class="w-full bg-primary text-white text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium shadow-button touch-manipulation active:scale-[0.98]"
        >
          {{ t('onboarding.continueBtn') }}
        </button>
      </div>
    </div>

    <!-- Discovery View -->
    <div 
      v-else-if="currentView === 'discovery'" 
      class="h-[100svh] flex flex-col relative z-10 overflow-hidden overscroll-none"
    >
      <!-- Header -->
      <header class="sticky top-0 z-20 bg-surface/90 backdrop-blur-lg header-safe">
        <div class="flex items-center justify-between px-2 xs:px-3 py-1 xs:py-1.5">
          <!-- Spacer for layout balance -->
          <div class="w-8 xs:w-9"></div>
          
          <div class="text-center">
            <h1 class="text-xs xs:text-sm font-semibold text-text-deep">{{ t('discovery.title') }}</h1>
            <p class="text-[8px] xs:text-[9px] text-text-muted">{{ t('discovery.subtitle') }}</p>
          </div>
          
          <div class="flex items-center gap-1">
            <button
              @click="goToMatches"
              class="w-8 h-8 xs:w-9 xs:h-9 rounded-xl bg-background shadow-soft touch-manipulation relative flex items-center justify-center"
              :aria-label="t('matches.title')"
            >
              <span class="text-sm xs:text-base">💬</span>
              <span 
                v-if="matches.length > 0"
                class="absolute -top-0.5 -right-0.5 w-3 h-3 xs:w-3.5 xs:h-3.5 bg-primary text-white text-[8px] xs:text-[9px] rounded-full flex items-center justify-center font-semibold"
              >
                {{ matches.length > 9 ? '9+' : matches.length }}
              </span>
            </button>
            <button
              @click="goToProfile"
              class="w-8 h-8 xs:w-9 xs:h-9 rounded-xl bg-background shadow-soft touch-manipulation overflow-hidden p-0"
              :aria-label="t('nav.profile')"
            >
              <img 
                v-if="getPrimaryPhotoUrl()"
                :src="getPrimaryPhotoUrl()"
                :alt="t('nav.profile')"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-sm xs:text-base">👤</span>
            </button>
          </div>
        </div>
      </header>
      
      <!-- Profile Card -->
      <main class="flex-1 min-h-0 px-0 xs:px-1 py-0 xs:py-1 flex flex-col items-center overflow-hidden relative overscroll-none">
        <!-- Accessible swipe hint for all users (auto-hides after 10 seconds) -->
        <Transition name="fade">
          <div 
            v-if="showSwipeHint"
            class="absolute -top-1 inset-x-0 sm:inset-x-auto sm:left-0 sm:right-0 flex justify-center z-[5] pointer-events-none"
          >
            <div 
              class="text-center text-text-deep text-xs bg-surface/95 backdrop-blur-sm px-4 sm:px-6 py-2 rounded-none sm:rounded-full border-y sm:border border-primary/20 shadow-soft w-full sm:w-auto sm:max-w-[90vw]"
              role="status"
              aria-live="polite"
            >
              <span class="font-medium">{{ t('discovery.accessibleHint') }}</span>
              <span class="block text-[10px] text-text-muted mt-0.5">{{ t('discovery.keyboardHint') }}</span>
            </div>
          </div>
        </Transition>
        
        <div 
          v-if="currentProfile"
          :key="currentProfile.id || currentProfile.user_id || currentProfileIndex"
          class="card w-full max-w-full relative swipeable no-context-menu select-none flex flex-col h-full max-h-full rounded-none"
          :class="{ 'transition-none': isSwiping, 'transition-all duration-300': !isSwiping && !isAnimating }"
          :style="{ 
            transform: `translateX(${cardOffset}px) rotate(${cardRotation}deg)`,
            opacity: cardOpacity,
            cursor: isSwiping ? 'grabbing' : 'grab'
          }"
          @touchstart.passive="handleTouchStart"
          @touchmove="handleTouchMove"
          @touchend="handleTouchEnd"
          @mousedown="handleMouseDown"
        >
          <!-- Swipe Overlay - Like -->
          <div 
            class="absolute inset-0 z-20 flex items-center justify-center rounded-3xl pointer-events-none transition-opacity duration-200"
            :class="swipeDirection === 'right' ? 'opacity-100' : 'opacity-0'"
            :style="{ background: 'linear-gradient(135deg, rgba(129, 178, 154, 0.9), rgba(129, 178, 154, 0.7))' }"
          >
            <div class="text-center text-white">
              <div class="text-6xl mb-2 animate-bounce-soft">💚</div>
              <div class="text-2xl font-bold uppercase tracking-wider">{{ t('discovery.connectBtn') }}</div>
            </div>
          </div>
          
          <!-- Swipe Overlay - Pass -->
          <div 
            class="absolute inset-0 z-20 flex items-center justify-center rounded-3xl pointer-events-none transition-opacity duration-200"
            :class="swipeDirection === 'left' ? 'opacity-100' : 'opacity-0'"
            :style="{ background: 'linear-gradient(135deg, rgba(224, 122, 95, 0.9), rgba(224, 122, 95, 0.7))' }"
          >
            <div class="text-center text-white">
              <div class="text-6xl mb-2 animate-wiggle">✕</div>
              <div class="text-2xl font-bold uppercase tracking-wider">{{ t('discovery.passBtn') }}</div>
            </div>
          </div>

          <!-- Compatibility Badge - Clickable for breakdown -->
          <button 
            @click.stop="showMatchBreakdown = !showMatchBreakdown"
            class="absolute top-4 end-4 z-10 flex items-center gap-1.5 xs:gap-2 px-2.5 xs:px-3 py-1 xs:py-1.5 bg-surface/90 backdrop-blur-sm rounded-full shadow-soft transition-all hover:scale-105 active:scale-95"
            :class="swipeDirection ? 'opacity-0' : 'opacity-100'"
            :aria-expanded="showMatchBreakdown"
            :aria-label="t('discovery.compatibility') + ' ' + currentProfile.compatibility + '%'"
          >
            <span class="text-base xs:text-lg">💫</span>
            <span class="text-xs xs:text-sm font-semibold text-primary">{{ currentProfile.compatibility }}%</span>
            <span class="text-[10px] text-text-muted">▾</span>
          </button>
          
          <!-- Match Breakdown Popup -->
          <Transition name="fade">
            <div 
              v-if="showMatchBreakdown"
              class="absolute top-16 end-4 z-20 w-64 bg-surface rounded-xl shadow-lg border border-border p-4"
              @click.stop
            >
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-text-deep">{{ t('discovery.whyMatch') }}</h4>
                <button @click="showMatchBreakdown = false" class="text-text-muted hover:text-text-deep">✕</button>
              </div>
              
              <ul class="space-y-2 text-xs">
                <li v-if="sharedTags.length > 0" class="flex items-center gap-2">
                  <span class="w-6 h-6 bg-primary-light rounded-full flex items-center justify-center">✨</span>
                  <span class="flex-1">{{ sharedTags.length }} {{ t('discovery.sharedTags') }}</span>
                  <span class="font-semibold text-primary">+20%</span>
                </li>
                <li v-if="currentProfile.distance" class="flex items-center gap-2">
                  <span class="w-6 h-6 bg-emerald-light rounded-full flex items-center justify-center">📍</span>
                  <span class="flex-1">{{ t('discovery.nearby') }}</span>
                  <span class="font-semibold text-emerald">+15%</span>
                </li>
                <li class="flex items-center gap-2">
                  <span class="w-6 h-6 bg-amber-light rounded-full flex items-center justify-center">🎯</span>
                  <span class="flex-1">{{ t('discovery.sharedInterests') }}</span>
                  <span class="font-semibold text-amber">+15%</span>
                </li>
              </ul>
              
              <p class="text-[10px] text-text-muted mt-3 pt-2 border-t border-border">
                {{ t('discovery.matchDisclaimer') }}
              </p>
            </div>
          </Transition>

          <!-- Shared Tags Sparkles -->
          <div 
            v-if="sharedTags.length > 0"
            class="absolute top-4 start-4 z-10 flex items-center gap-1 px-2.5 xs:px-3 py-1 xs:py-1.5 bg-primary text-white rounded-full text-[10px] xs:text-xs font-medium shadow-soft transition-opacity"
            :class="swipeDirection ? 'opacity-0' : 'opacity-100'"
          >
            <span>✨</span>
            {{ sharedTags.length }} {{ t('discovery.shared') }}
          </div>

          <!-- Scrollable Content Area (Photo + Details) -->
          <div 
            ref="discoveryDetailsScroll"
            class="flex-1 min-h-0 overflow-y-auto momentum-scroll"
          >
            <!-- Photo Carousel -->
            <div 
              ref="discoveryPhotoCarousel"
              class="relative aspect-[5/4] xs:aspect-[4/3] sm:aspect-[3/2] overflow-hidden"
            >
              <!-- Photo indicators -->
              <div 
                v-if="getAllPhotos(currentProfile).length > 1"
                class="absolute top-2 inset-x-2 z-20 flex gap-1"
              >
                <div 
                  v-for="(photo, index) in getAllPhotos(currentProfile)"
                  :key="index"
                  class="flex-1 h-0.5 rounded-full transition-all"
                  :class="index === currentPhotoIndex ? 'bg-white' : 'bg-white/40'"
                ></div>
              </div>
              
              <!-- Tap zones for photo navigation -->
              <div 
                v-if="getAllPhotos(currentProfile).length > 1"
                class="absolute inset-0 z-10 flex"
              >
                <div 
                  class="w-1/3 h-full cursor-pointer" 
                  @click.stop="prevPhoto"
                ></div>
                <div class="w-1/3 h-full"></div>
                <div 
                  class="w-1/3 h-full cursor-pointer" 
                  @click.stop="nextPhoto"
                ></div>
              </div>
              
              <img 
                :src="getAllPhotos(currentProfile)[currentPhotoIndex] || getPhotoUrl(currentProfile.photo || currentProfile.picture_url)" 
                :alt="getProfilePhotoAlt(currentProfile, currentPhotoIndex, getAllPhotos(currentProfile).length)"
                class="w-full h-full object-cover"
                loading="lazy"
                role="img"
              />
              <!-- Gradient Overlay -->
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none"></div>
              
              <!-- Bot Badge -->
              <div 
                v-if="currentProfile.isBot"
                class="absolute top-3 start-3 z-20 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gradient-to-r from-cyan-500/90 to-blue-500/90 backdrop-blur-sm border border-white/20 shadow-lg"
                :aria-label="t('bot.badge')"
              >
                <svg class="w-3.5 h-3.5 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zm-3 10a2 2 0 100 4 2 2 0 000-4zm6 0a2 2 0 100 4 2 2 0 000-4z"/>
                </svg>
                <span class="text-[10px] xs:text-xs font-semibold text-white tracking-wide">{{ t('bot.badge') }}</span>
              </div>

              <!-- Profile Info -->
              <div class="absolute bottom-0 inset-x-0 p-3 xs:p-4 text-white">
                <h2 class="text-lg xs:text-xl font-bold mb-0.5 flex items-center gap-2">
                  {{ currentProfile.name }}, {{ currentProfile.age }}
                </h2>
                <p class="text-[10px] xs:text-xs text-white/80 mb-1.5 xs:mb-2">
                  📍 {{ t('discovery.distance', { km: currentProfile.distance }) }}
                </p>

                <div v-if="currentProfile.relationshipIntent" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/25 backdrop-blur-md text-white text-[10px] xs:text-xs font-semibold border border-white/30 mb-1.5 xs:mb-2">
                  <span>🎯</span>
                  <span>{{ t(`intent.options.${currentProfile.relationshipIntent}`) }}</span>
                </div>
                
                <!-- Tags -->
                <div class="flex flex-wrap gap-1 xs:gap-1.5">
                  <span 
                    v-for="tagId in currentProfile.tags" 
                    :key="tagId"
                    :class="[
                      'inline-flex items-center gap-1 xs:gap-1.5 px-2 xs:px-2.5 py-0.5 xs:py-1 rounded-full text-[10px] xs:text-xs font-semibold transition-all',
                      sharedTags.includes(tagId) 
                        ? 'bg-primary text-white shadow-md' 
                        : 'bg-white/25 backdrop-blur-md text-white border border-white/30'
                    ]"
                  >
                    <span>{{ getTagIcon(tagId) }}</span>
                    <span>{{ getTagLabel(tagId) }}</span>
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Bio & Prompt - Progressive Disclosure -->
            <div class="p-3 xs:p-4 sm:p-5 pb-2 space-y-2.5 xs:space-y-3">
            <!-- LAYER 1: Essential - Always visible -->
            <!-- Profile Prompt (headline/hook) -->
            <div class="bg-gradient-to-br from-primary-light via-peach/40 to-accent/20 rounded-xl p-3 xs:p-4 mb-3 xs:mb-4 border border-primary/25 shadow-sm">
              <p class="text-xs xs:text-sm font-bold text-primary uppercase tracking-wider mb-1.5">
                {{ t(`profilePrompts.${currentProfile.promptId}`) }}
              </p>
              <p class="text-sm xs:text-base text-text-deep font-medium leading-relaxed">
                "{{ getLocalized(currentProfile.promptAnswer) }}"
              </p>
            </div>

            <!-- Bio -->
            <div>
              <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-2">
                {{ t('profile.about') }}
              </h3>
              <p class="text-sm xs:text-base text-text-deep leading-relaxed mb-3 xs:mb-4">
                {{ getLocalized(currentProfile.bio) }}
              </p>
            
              <!-- Interests -->
              <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-2">
                {{ t('profile.interests') }}
              </h3>
              <div class="flex flex-wrap gap-1.5 xs:gap-2">
                <span 
                  v-for="(interest, idx) in getLocalized(currentProfile.interests, [])"
                  :key="interest"
                  :class="[
                    'px-2.5 xs:px-3 py-1 xs:py-1.5 rounded-full text-xs xs:text-sm font-medium border transition-transform hover:scale-105',
                    interestColorClasses[idx % interestColorClasses.length]
                  ]"
                >
                  {{ translateInterest(interest) }}
                </span>
              </div>
            </div>
            
            <!-- Time Preferences -->
            <div v-if="currentProfile.responsePace || currentProfile.datePace || (currentProfile.preferredTimes && currentProfile.preferredTimes.length > 0)" class="mt-4 xs:mt-5">
              <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <span class="text-sm">🕐</span>
                {{ t('timePreferences.title') }}
              </h3>
              <div class="flex flex-wrap gap-1.5">
                <!-- Preferred Times -->
                <span 
                  v-for="time in (currentProfile.preferredTimes || [])"
                  :key="time"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-light text-indigo border border-indigo/20 rounded-full text-xs font-medium"
                >
                  <span>{{ timeOptions.find(t => t.id === time)?.emoji }}</span>
                  <span>{{ t(`timePreferences.times.${time}`) }}</span>
                </span>
                <!-- Response Pace -->
                <span 
                  v-if="currentProfile.responsePace"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-light text-amber border border-amber/20 rounded-full text-xs font-medium"
                >
                  <span>{{ responsePaceOptions.find(p => p.id === currentProfile.responsePace)?.emoji }}</span>
                  <span>{{ t(`timePreferences.responsePaceOptions.${currentProfile.responsePace}`) }}</span>
                </span>
                <!-- Date Pace -->
                <span 
                  v-if="currentProfile.datePace"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-light text-emerald border border-emerald/20 rounded-full text-xs font-medium"
                >
                  <span>{{ datePaceOptions.find(p => p.id === currentProfile.datePace)?.emoji }}</span>
                  <span>{{ t(`timePreferences.datePaceOptions.${currentProfile.datePace}`) }}</span>
                </span>
              </div>
            </div>
            </div>
          </div>
        </div>
        
        <!-- No More Profiles -->
        <div 
          v-else
          class="text-center p-6 xs:p-8 animate-slide-up"
        >
          <div class="w-16 xs:w-20 h-16 xs:h-20 mx-auto bg-gradient-to-br from-primary-light to-accent/20 rounded-full flex items-center justify-center mb-4">
            <span class="text-3xl xs:text-4xl">💫</span>
          </div>
          <h2 class="text-lg xs:text-xl font-semibold text-text-deep mb-2">
            {{ t('discovery.noMoreProfiles') }}
          </h2>
          <p class="text-sm xs:text-base text-text-muted mb-4">
            {{ t('discovery.noMoreExplanation') }}
          </p>
          <!-- Action to adjust preferences -->
          <button
            @click="goToProfile"
            class="inline-flex items-center gap-2 px-4 py-2 bg-primary-light text-primary rounded-full text-sm font-medium hover:bg-primary hover:text-white transition-colors"
          >
            ⚙️ {{ t('lookingFor.title') }}
          </button>
        </div>
      </main>
      
      <!-- Action Buttons -->
      <div 
        v-if="currentProfile"
        class="sticky bottom-0 bg-surface/90 backdrop-blur-lg p-1 xs:p-1.5 bottom-bar-safe"
      >
        <div class="flex items-center justify-center gap-2 xs:gap-2.5">
          <!-- Pass Button -->
          <button
            @click="passProfile"
            class="w-8 h-8 xs:w-9 xs:h-9 bg-surface rounded-full shadow-card border-2 border-danger/20 flex items-center justify-center touch-manipulation active:scale-90 active:border-danger"
            :aria-label="t('a11y.passProfile')"
          >
            <svg class="w-3.5 h-3.5 xs:w-4 xs:h-4 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          
          <!-- Connect Button -->
          <button
            @click="connectProfile"
            class="w-10 h-10 xs:w-11 xs:h-11 bg-primary rounded-full shadow-button flex items-center justify-center touch-manipulation active:scale-90"
            :aria-label="t('a11y.connectProfile')"
          >
            <svg class="w-4.5 h-4.5 xs:w-5 xs:h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </button>
        </div>
        
        <!-- Undo Toast -->
        <Transition name="slide-up">
          <div 
            v-if="showUndoToast && lastSwipeAction"
            class="fixed bottom-28 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-4 py-3 bg-surface rounded-full shadow-lg border border-border"
            role="alert"
          >
            <span class="text-sm text-text-deep">
              {{ lastSwipeAction.type === 'pass' ? t('discovery.skipping') : t('discovery.connecting') }}
              <strong>{{ lastSwipeAction.profile.name }}</strong>...
            </span>
            <button 
              @click="undoSwipe"
              class="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded-full hover:bg-primary-dark transition-colors"
            >
              ↩ {{ t('discovery.undo') }}
            </button>
            <!-- Progress bar -->
            <div class="absolute bottom-0 left-4 right-4 h-0.5 bg-border rounded-full overflow-hidden">
              <div 
                class="h-full bg-primary animate-shrink-width"
                :style="{ animationDuration: UNDO_DURATION + 'ms' }"
              ></div>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Matches View -->
    <div 
      v-else-if="currentView === 'matches'" 
      class="min-h-screen-safe flex flex-col relative z-10"
    >
      <!-- Header -->
      <header class="sticky top-0 z-20 bg-surface/90 backdrop-blur-lg header-safe">
        <div class="flex items-center justify-between px-3 xs:px-4 py-2 xs:py-3">
          <button
            @click="goBack"
            class="btn-icon bg-background shadow-soft touch-manipulation"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 xs:w-6 xs:h-6 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <div class="text-center">
            <h1 class="text-base xs:text-lg font-semibold text-text-deep">{{ t('matches.title') }}</h1>
            <p class="text-[10px] xs:text-xs text-text-muted">{{ t('matches.subtitle') }}</p>
          </div>
          
          <button
            @click="goToProfile"
            class="btn-icon bg-background shadow-soft touch-manipulation overflow-hidden p-0"
            :aria-label="t('nav.profile')"
          >
            <img 
              v-if="getPrimaryPhotoUrl()"
              :src="getPrimaryPhotoUrl()"
              :alt="t('nav.profile')"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-lg">👤</span>
          </button>
        </div>
      </header>
      
      <!-- Matches List -->
      <main class="flex-1 px-3 xs:px-4 py-3 xs:py-6 overflow-y-auto">
        <!-- No matches state -->
        <div 
          v-if="matches.length === 0"
          class="flex flex-col items-center justify-center h-full text-center py-12"
        >
          <div class="w-24 h-24 rounded-full bg-surface flex items-center justify-center mb-6 shadow-soft">
            <span class="text-5xl">💕</span>
          </div>
          <h2 class="text-xl font-semibold text-text-deep mb-2">{{ t('matches.noMatches') }}</h2>
          <p class="text-text-muted max-w-xs">{{ t('matches.noMatchesDescription') }}</p>
          <button
            @click="navigateTo('discovery')"
            class="btn-primary mt-6"
          >
            {{ t('nav.discover') }}
          </button>
        </div>
        
        <!-- Matches grid -->
        <div v-else class="space-y-3">
          <div 
            v-for="match in matches" 
            :key="match.id"
            class="card p-3 xs:p-4 flex items-center gap-3 xs:gap-4 cursor-pointer hover:shadow-lg transition-shadow"
            @click="openChat(match)"
          >
            <!-- Avatar - clickable to view profile -->
            <div 
              class="relative flex-shrink-0"
              @click.stop="openProfileView(getMatchProfile(match))"
            >
              <div class="w-14 h-14 xs:w-16 xs:h-16 rounded-2xl overflow-hidden bg-surface shadow-soft ring-2 ring-transparent hover:ring-primary/50 transition-all">
                <img 
                  v-if="getMatchProfile(match).picture_url || getMatchProfile(match).primary_photo"
                  :src="getPhotoUrl(getMatchProfile(match).primary_photo || getMatchProfile(match).picture_url)"
                  :alt="getMatchProfile(match).name"
                  class="w-full h-full object-cover"
                  @error="$event.target.style.display = 'none'; $event.target.nextElementSibling.style.display = 'flex'"
                />
                <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/20 to-secondary/20">
                  <span class="text-2xl">{{ getMatchProfile(match).name?.charAt(0) || '?' }}</span>
                </div>
              </div>
              <!-- Online indicator -->
              <div class="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-secondary rounded-full border-2 border-surface"></div>
            </div>
            
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h3 class="font-semibold text-text-deep truncate">
                  {{ getMatchProfile(match).name }}
                </h3>
                <span v-if="getMatchProfile(match).age" class="text-xs text-text-muted">
                  {{ getMatchProfile(match).age }}
                </span>
              </div>
              <p class="text-sm text-text-muted truncate">
                {{ getMatchProfile(match).bio || t('matches.startChat') }}
              </p>
              <p class="text-xs text-text-muted/70 mt-1">
                {{ t('matches.matchedOn') }} {{ formatMatchDate(match.matched_at) }}
              </p>
            </div>
            
            <!-- Action -->
            <button
              class="btn-primary text-sm py-2 px-3 xs:px-4 flex-shrink-0"
              @click.stop="openChat(match)"
            >
              {{ t('matches.startChat') }}
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- Chat View -->
    <div 
      v-else-if="currentView === 'chat'" 
      class="h-[100svh] flex flex-col relative z-10 bg-background overflow-hidden overscroll-none"
    >
      <!-- Header -->
      <header class="sticky top-0 z-20 bg-surface border-b border-border shadow-soft header-safe">
        <div
          class="flex items-center gap-2 xs:gap-3 px-3 xs:px-4 py-2 xs:py-3"
          :class="{ 'py-1.5 xs:py-2': isKeyboardOpen }"
        >
          <button
            @click="goBack"
            class="btn-icon bg-background touch-manipulation"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 xs:w-6 xs:h-6 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <!-- Match Info - Clickable to view profile -->
          <div 
            class="flex items-center gap-2 xs:gap-3 flex-1 cursor-pointer hover:bg-primary-light/30 rounded-xl p-1 -m-1 transition-colors"
            @click="openProfileView(getChatPartnerProfile())"
          >
            <div class="relative">
              <img 
                :src="getPhotoUrl(getChatPartnerProfile().primary_photo || getChatPartnerProfile().picture_url || mockChat.matchPhoto)" 
                :alt="mockChat.matchName"
                class="w-10 xs:w-11 h-10 xs:h-11 rounded-full object-cover ring-2 ring-primary/20"
                :class="{ 'w-8 h-8 xs:w-9 xs:h-9': isKeyboardOpen }"
                @error="$event.target.src = getPhotoUrl(mockChat.matchPhoto) || ''"
              />
              <span 
                v-if="mockChat.isOnline && !mockChat.isBot"
                class="absolute -bottom-0.5 -end-0.5 w-3 xs:w-3.5 h-3 xs:h-3.5 bg-success rounded-full border-2 border-surface"
              ></span>
            </div>
            <div class="flex-1">
              <h1 class="text-sm xs:text-base font-semibold text-text-deep" :class="{ 'text-[13px] xs:text-sm': isKeyboardOpen }">
                {{ mockChat.matchName }}
              </h1>
              <p v-if="mockChat.isBot" class="text-[10px] xs:text-xs text-cyan-600 flex items-center gap-1" :class="{ 'text-[9px] xs:text-[10px]': isKeyboardOpen }">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zm-3 10a2 2 0 100 4 2 2 0 000-4zm6 0a2 2 0 100 4 2 2 0 000-4z"/>
                </svg>
                {{ t('bot.status') }}
              </p>
              <p v-else class="text-[10px] xs:text-xs text-success flex items-center gap-1" :class="{ 'text-[9px] xs:text-[10px]': isKeyboardOpen }">
                <span class="w-1.5 h-1.5 bg-success rounded-full animate-pulse"></span>
                {{ t('chat.online') }}
              </p>
            </div>
          </div>
          
          <!-- Sidebar Toggle (Desktop) -->
          <button
            @click="showChatSidebar = !showChatSidebar"
            class="btn-icon bg-background touch-manipulation hidden lg:flex"
            :aria-label="showChatSidebar ? t('chat.hideSidebar') : t('chat.showSidebar')"
            :title="showChatSidebar ? t('chat.hideSidebar') : t('chat.showSidebar')"
          >
            <svg class="w-5 h-5 text-text-deep" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h10"/>
            </svg>
          </button>

          <!-- Summary Button -->
          <button
            @click="openSummary"
            class="btn-icon bg-background touch-manipulation"
            :aria-label="t('chat.summaryAction')"
            :title="t('chat.summaryAction')"
          >
            <svg class="w-5 h-5 text-text-deep" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6M7 4h10a2 2 0 012 2v12a2 2 0 01-2 2H7a2 2 0 01-2-2V6a2 2 0 012-2z"/>
            </svg>
          </button>

          <!-- Disconnect Button -->
          <button
            @click="showDisconnectConfirm = true"
            class="btn-icon bg-background touch-manipulation text-danger/70 hover:text-danger hover:bg-danger/10"
            :aria-label="t('chat.disconnect')"
            :title="t('chat.disconnect')"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7a4 4 0 11-8 0 4 4 0 018 0zM9 14a6 6 0 00-6 6v1h12v-1a6 6 0 00-6-6zM21 12h-6"/>
            </svg>
          </button>
        </div>
      </header>
      
      <!-- Disconnect Confirmation Dialog -->
      <Transition name="fade">
        <div 
          v-if="showDisconnectConfirm"
          class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          @click.self="showDisconnectConfirm = false"
        >
          <div class="bg-surface rounded-2xl max-w-sm w-full p-6 shadow-2xl animate-scale-in text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-danger/10 rounded-full flex items-center justify-center">
              <span class="text-3xl">💔</span>
            </div>
            <h3 class="text-xl font-bold text-text-deep mb-2">{{ t('chat.disconnectTitle') }}</h3>
            <p class="text-text-muted mb-6">{{ t('chat.disconnectMessage') }}</p>
            
            <div class="flex gap-3">
              <button
                @click="showDisconnectConfirm = false"
                class="flex-1 btn-secondary py-3"
                :disabled="isDisconnecting"
              >
                {{ t('cancel') }}
              </button>
              <button
                @click="handleDisconnect"
                class="flex-1 bg-danger text-white font-semibold py-3 rounded-xl active:scale-[0.98] disabled:opacity-50"
                :disabled="isDisconnecting"
              >
                {{ isDisconnecting ? '...' : t('chat.disconnectConfirm') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
      
      <!-- Conversation Summary Modal -->
      <Transition name="fade">
        <div 
          v-if="showSummaryModal"
          class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          @click.self="showSummaryModal = false"
        >
          <div class="bg-surface rounded-2xl max-w-md w-full p-6 shadow-2xl animate-scale-in">
            <h3 class="text-lg font-semibold text-text-deep mb-2">
              {{ t('chat.summaryTitle') }}
            </h3>
            <p v-if="isLoadingSummary" class="text-text-muted text-sm">
              {{ t('chat.summaryLoading') }}
            </p>
            <p v-else class="text-text-muted text-sm whitespace-pre-wrap">
              {{ aiSummary }}
            </p>
            <div class="mt-5 flex justify-end">
              <button
                @click="showSummaryModal = false"
                class="btn-secondary px-4 py-2"
              >
                {{ t('done') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
      
      <div class="flex flex-1 min-h-0">
        <!-- Conversations Sidebar (Desktop) -->
        <aside 
          :class="[
            'hidden lg:flex-col w-72 border-e border-border bg-surface/90',
            showChatSidebar ? 'lg:flex' : 'lg:hidden'
          ]"
          :aria-label="t('chat.conversations')"
        >
          <div class="px-4 py-3 border-b border-border">
            <h2 class="text-xs font-semibold text-text-muted uppercase tracking-wide">
              {{ t('chat.conversations') }}
            </h2>
          </div>
          <div class="flex-1 overflow-y-auto">
            <button
              v-for="match in matches"
              :key="match.id"
              @click="openChat(match)"
              :class="[
                'w-full text-start px-4 py-3 flex items-center gap-3 border-b border-border/60 hover:bg-background/60 transition-colors',
                currentConversation === (match.conversation_id || null) ? 'bg-background/70' : ''
              ]"
            >
              <div class="relative shrink-0">
                <div class="w-9 h-9 rounded-full bg-border/60 border border-border/70 overflow-hidden">
                  <img 
                    v-if="getMatchProfile(match).picture_url || getMatchProfile(match).primary_photo"
                    :src="getPhotoUrl(getMatchProfile(match).primary_photo || getMatchProfile(match).picture_url)"
                    :alt="getMatchProfile(match).name"
                    class="w-full h-full object-cover"
                    @error="$event.target.style.display = 'none'; $event.target.nextElementSibling.style.display = 'flex'"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-xs text-text-muted">
                    {{ getMatchProfile(match).name?.charAt(0) || '?' }}
                  </div>
                </div>
                <!-- Bot indicator badge -->
                <div 
                  v-if="getMatchProfile(match).is_bot"
                  class="absolute -bottom-0.5 -end-0.5 w-4 h-4 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 border-2 border-surface flex items-center justify-center"
                  :title="t('bot.badge')"
                >
                  <svg class="w-2.5 h-2.5 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zm-3 10a2 2 0 100 4 2 2 0 000-4zm6 0a2 2 0 100 4 2 2 0 000-4z"/>
                  </svg>
                </div>
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-text-deep truncate">
                  {{ getMatchProfile(match).name || t('matches.startChat') }}
                </p>
                <p class="text-xs text-text-muted truncate">
                  {{ getMatchProfile(match).bio || t('matches.startChat') }}
                </p>
              </div>
            </button>
          </div>
        </aside>

        <div class="flex-1 flex flex-col min-h-0">
        <!-- Messages -->
        <main ref="chatScrollContainer" class="flex-1 px-3 xs:px-4 py-3 xs:py-4 overflow-y-auto overscroll-contain momentum-scroll hide-scrollbar">
          <div class="max-w-3xl mx-auto w-full space-y-4 pb-4">
            <!-- Date Separator -->
            <div class="text-center">
              <span class="inline-block px-3 xs:px-4 py-1 xs:py-1.5 bg-surface rounded-full text-[10px] xs:text-xs text-text-muted font-medium shadow-soft">
                {{ t('chat.today') }}
              </span>
            </div>
            
            <!-- Messages -->
            <div class="divide-y divide-border/60">
              <div 
                v-for="(message, index) in mockChat.messages" 
                :key="message.id"
                class="w-full"
              >
                <div 
                  :class="[
                    'flex w-full items-start gap-3 xs:gap-4 py-4 xs:py-5',
                    message.sender === 'me' ? 'justify-end' : 'justify-start'
                  ]"
                >
                  <div v-if="message.sender === 'them'" class="shrink-0 mt-0.5">
                    <div class="w-6 h-6 xs:w-7 xs:h-7 rounded-full bg-border/60 border border-border/70 flex items-center justify-center overflow-hidden">
                      <img 
                        v-if="getChatPartnerProfile().primary_photo || getChatPartnerProfile().picture_url || mockChat.matchPhoto"
                        :src="getPhotoUrl(getChatPartnerProfile().primary_photo || getChatPartnerProfile().picture_url || mockChat.matchPhoto)" 
                        :alt="mockChat.matchName"
                        class="w-full h-full object-cover"
                        @error="$event.target.style.display = 'none'; $event.target.nextElementSibling.style.display = 'flex'"
                      />
                      <span v-else class="text-[10px] xs:text-xs font-semibold text-text-muted">
                        {{ mockChat.matchName?.[0] || 'N' }}
                      </span>
                    </div>
                  </div>

                  <div :class="['flex-1 min-w-0', message.sender === 'me' ? 'text-right' : 'text-left']">
                    <div :class="['flex', message.sender === 'me' ? 'justify-end' : 'justify-start']">
                      <div 
                        :class="getMessageBubbleClasses(message)"
                        @click="message.sender === 'them' && message.messageType !== 'voice' && toggleReactionMenu(message.id)"
                      >
                      <!-- Icebreaker Label -->
                      <span 
                        v-if="message.isIcebreaker"
                        class="inline-flex mb-2 px-2 py-0.5 bg-border text-text-muted text-[9px] xs:text-[10px] font-medium rounded-full"
                      >
                        {{ t('chat.icebreaker') }}
                      </span>

                      <!-- Voice Message -->
                      <div v-if="message.messageType === 'voice'" class="flex items-center gap-3">
                        <!-- Play/Pause Button -->
                        <button
                          v-if="message.audioUrl && !message.isUploading"
                          @click.stop="playVoiceMessage(message.id, message.audioUrl)"
                          class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 touch-manipulation active:scale-90 transition-colors bg-surface border border-border text-text-muted hover:text-text-deep"
                          :aria-label="playingAudioId === message.id ? t('chat.pauseVoice') : t('chat.playVoice')"
                        >
                          <!-- Playing indicator -->
                          <svg v-if="playingAudioId === message.id" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <rect x="6" y="5" width="4" height="14" rx="1"/>
                            <rect x="14" y="5" width="4" height="14" rx="1"/>
                          </svg>
                          <!-- Play icon -->
                          <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z"/>
                          </svg>
                        </button>
                        
                        <!-- Uploading indicator -->
                        <div v-else-if="message.isUploading" class="w-10 h-10 flex items-center justify-center">
                          <svg class="w-5 h-5 animate-spin text-text-muted" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        </div>
                        
                        <!-- Waveform visualization (decorative) -->
                        <div class="flex items-center gap-0.5 flex-1">
                          <div 
                            v-for="i in 20" 
                            :key="i"
                            :class="[
                              'w-1 rounded-full transition-all duration-100 bg-border',
                              playingAudioId === message.id ? 'animate-pulse' : ''
                            ]"
                            :style="{ height: `${Math.random() * 16 + 8}px` }"
                          ></div>
                        </div>
                        
                        <!-- Duration -->
                        <span class="text-xs font-mono shrink-0 text-text-muted">
                          {{ formatVoiceDuration(message.audioDuration) }}
                        </span>
                      </div>

                      <!-- Text Message -->
                      <p
                        v-else
                        :class="[
                          'text-sm xs:text-base leading-relaxed whitespace-pre-wrap',
                          message.sender === 'me' ? 'text-white' : 'text-text-deep'
                        ]"
                      >
                        {{ getLocalized(message.text) }}
                      </p>
                      
                      <!-- Reaction -->
                      <span v-if="message.reaction" class="inline-flex mt-2 text-sm">{{ message.reaction }}</span>

                      <!-- Reaction Menu (Mobile tap) -->
                      <Transition name="scale">
                        <div 
                          v-if="showReactionMenu === message.id && message.sender === 'them'"
                          class="absolute -bottom-10 start-0 z-10"
                        >
                          <div class="flex gap-1 bg-surface rounded-full px-2 py-1.5 shadow-card border border-border">
                            <button 
                              v-for="reaction in reactions"
                              :key="reaction.emoji"
                              @click.stop="toggleReaction(message.id, reaction.emoji); showReactionMenu = null"
                              class="p-1.5 active:scale-125 transition-transform touch-manipulation"
                              :class="{ 'bg-primary-light rounded-full': message.reaction === reaction.emoji }"
                            >
                              {{ reaction.emoji }}
                            </button>
                          </div>
                        </div>
                      </Transition>
                      </div>
                    </div>

                    <p v-if="shouldShowTimestamp(index)" class="mt-2 text-[10px] xs:text-xs text-text-light">
                      {{ message.time }}
                    </p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </main>
        
        <!-- Smart Suggestions Panel -->
        <Transition name="slide-up">
          <div
            v-if="showSuggestions"
            class="bg-surface border-t border-border p-3 xs:p-4"
          >
            <div class="max-w-3xl mx-auto">
              <div class="flex items-center justify-between gap-3 mb-2">
                <h4 class="text-xs xs:text-sm font-semibold text-text-deep flex items-center gap-2">
                  <span>✨</span>
                  {{ t('chat.smartSuggestions') }}
                </h4>
                <button
                  @click="fetchSuggestions(true)"
                  class="text-[10px] xs:text-xs text-text-muted hover:text-text-deep border border-border rounded-full px-3 py-1.5 min-h-[36px] touch-manipulation active:scale-95 transition-colors"
                  :aria-label="t('chat.refreshSuggestions')"
                  :disabled="isLoadingSuggestions"
                >
                  {{ t('chat.refreshSuggestions') }}
                </button>
              </div>
              <div v-if="isLoadingSuggestions" class="text-[10px] xs:text-xs text-text-muted">
                {{ t('chat.loadingSuggestions') }}
              </div>
              <div v-else-if="aiSuggestions.length" class="flex flex-wrap gap-2">
                <button
                  v-for="suggestion in aiSuggestions"
                  :key="suggestion"
                  @click="sendSuggestedMessage(suggestion)"
                  class="px-3 xs:px-4 py-2 bg-surface border border-border text-text-deep hover:border-primary/50 rounded-full text-xs xs:text-sm font-medium touch-manipulation active:scale-95 transition-colors min-h-[44px]"
                >
                  {{ suggestion }}
                </button>
              </div>
              <div v-else class="text-[10px] xs:text-xs text-text-muted">
                {{ t('chat.noSuggestions') }}
              </div>
            </div>
          </div>
        </Transition>


        <!-- Shortcuts -->
        <Transition name="slide-up">
          <div
            v-if="showShortcuts"
            class="bg-surface border-t border-border p-3 xs:p-4"
          >
            <div class="max-w-3xl mx-auto">
              <div class="flex items-start justify-between gap-3 mb-1">
                <h4 class="text-xs xs:text-sm font-semibold text-text-deep flex items-center gap-2">
                  <span>⚡</span>
                  {{ t('shortcuts.title') }}
                </h4>
                <button
                  @click="showShortcuts = false"
                  class="text-[10px] xs:text-xs text-text-muted hover:text-text-deep border border-border rounded-full px-3 py-1.5 min-h-[36px] touch-manipulation active:scale-95 transition-colors"
                  :aria-label="t('cancel')"
                >
                  {{ t('cancel') }}
                </button>
              </div>
              <p class="text-[10px] xs:text-xs text-text-muted mb-3">{{ t('shortcuts.helper') }}</p>
              <p v-if="shortcutsError" class="text-[10px] xs:text-xs text-red-600 mb-3">{{ shortcutsError }}</p>
              
              <div class="space-y-4">
                <div>
                  <p class="text-xs xs:text-sm font-semibold text-text-deep mb-2">
                    {{ t('shortcuts.savedTitle') }}
                  </p>
                  <div v-if="savedShortcutItems.length" class="flex flex-wrap gap-2">
                    <div
                      v-for="shortcut in savedShortcutItems"
                      :key="shortcut.id"
                      class="flex flex-wrap items-center gap-2"
                    >
                      <button
                        @click="useShortcut(shortcut.content)"
                        class="px-3 xs:px-4 py-2 bg-surface border border-border text-text-deep hover:border-primary/50 rounded-full text-xs xs:text-sm font-medium min-h-[44px] touch-manipulation active:scale-95 transition-colors"
                        :aria-label="t('shortcuts.ariaUse', { label: shortcut.title })"
                      >
                        {{ shortcut.title }}
                      </button>
                      <button
                        @click="removeShortcut(shortcut.id)"
                        class="px-3 xs:px-4 py-2 bg-border/40 text-text-muted hover:text-text-deep rounded-full text-xs xs:text-sm font-medium min-h-[44px] touch-manipulation active:scale-95 transition-colors"
                        :aria-label="t('shortcuts.ariaRemove', { label: shortcut.title })"
                      >
                        {{ t('shortcuts.remove') }}
                      </button>
                    </div>
                  </div>
                  <p v-else class="text-[10px] xs:text-xs text-text-muted">
                    {{ t('shortcuts.empty') }}
                  </p>
                </div>
                
                <div>
                  <p class="text-xs xs:text-sm font-semibold text-text-deep mb-2">
                    {{ t('shortcuts.createTitle') }}
                  </p>
                  <div class="grid gap-2">
                    <label class="text-[10px] xs:text-xs text-text-muted" :for="'shortcut-title'">
                      {{ t('shortcuts.titleLabel') }}
                    </label>
                    <input
                      id="shortcut-title"
                      v-model="newShortcutTitle"
                      type="text"
                      class="input-field text-sm xs:text-base"
                      :placeholder="t('shortcuts.titlePlaceholder')"
                    />
                    <label class="text-[10px] xs:text-xs text-text-muted" :for="'shortcut-content'">
                      {{ t('shortcuts.contentLabel') }}
                    </label>
                    <textarea
                      id="shortcut-content"
                      v-model="newShortcutContent"
                      class="input-field text-sm xs:text-base min-h-[72px]"
                      :placeholder="t('shortcuts.contentPlaceholder')"
                      rows="2"
                    ></textarea>
                    <div class="flex flex-wrap gap-2">
                      <button
                        @click="saveShortcut(newShortcutTitle, newShortcutContent)"
                        class="px-3 xs:px-4 py-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-full text-xs xs:text-sm font-medium min-h-[44px] touch-manipulation active:scale-95 transition-colors"
                        :aria-label="t('shortcuts.ariaSave', { label: newShortcutTitle || t('shortcuts.untitled') })"
                      >
                        {{ t('shortcuts.add') }}
                      </button>
                      <button
                        @click="useShortcut(newShortcutContent)"
                        class="px-3 xs:px-4 py-2 bg-surface border border-border text-text-deep hover:border-primary/50 rounded-full text-xs xs:text-sm font-medium min-h-[44px] touch-manipulation active:scale-95 transition-colors"
                        :aria-label="t('shortcuts.ariaUse', { label: newShortcutTitle || t('shortcuts.untitled') })"
                      >
                        {{ t('shortcuts.useDraft') }}
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
        </Transition>
        
        <!-- Input Area - Recording Mode -->
        <div 
          v-if="isRecording"
          class="sticky bottom-0 bg-red-50 border-t border-red-200 p-3 xs:p-4 bottom-bar-safe"
        >
          <div class="max-w-3xl mx-auto flex items-center gap-3">
            <!-- Cancel Button -->
            <button
              @click="cancelRecording"
              class="w-10 h-10 xs:w-11 xs:h-11 rounded-full bg-white text-red-500 shadow-soft flex items-center justify-center shrink-0 touch-manipulation active:scale-90"
              :aria-label="t('chat.cancelRecording')"
            >
              <svg class="w-5 h-5 xs:w-6 xs:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
            
            <!-- Recording Indicator -->
            <div class="flex-1 flex items-center gap-3">
              <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span class="text-red-600 font-medium text-sm xs:text-base">{{ t('chat.recording') }}</span>
              <span class="text-red-500 font-mono text-sm xs:text-base">{{ formatRecordingTime(recordingDuration) }}</span>
            </div>
            
            <!-- Stop/Send Button -->
            <button
              @click="stopRecording"
              class="w-12 h-12 xs:w-14 xs:h-14 rounded-full bg-red-500 text-white shadow-button flex items-center justify-center shrink-0 touch-manipulation active:scale-90 animate-pulse"
              :aria-label="t('chat.stopRecording')"
            >
              <svg class="w-6 h-6 xs:w-7 xs:h-7" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Input Area - Normal Mode -->
        <div 
          v-else
          class="sticky bottom-0 bg-background/95 backdrop-blur border-t border-border p-2 xs:p-3 bottom-bar-safe"
          :class="{ 'pb-1': isKeyboardOpen }"
        >
          <div class="max-w-3xl mx-auto space-y-2">
            <!-- Action Buttons Row -->
            <div class="flex items-center justify-center gap-3">
              <!-- Shortcuts Button -->
              <button
                @click="toggleShortcuts"
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center shrink-0 touch-manipulation active:scale-90 transition-colors',
                  showShortcuts ? 'bg-primary/20 text-primary' : 'bg-border/50 text-text-muted hover:text-text-deep'
                ]"
                :aria-expanded="showShortcuts"
                :aria-label="t('shortcuts.toggle')"
              >
                <span class="text-sm">⚡</span>
              </button>

              <!-- Suggestions Button -->
              <button
                @click="toggleSuggestions"
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center shrink-0 touch-manipulation active:scale-90 transition-colors',
                  showSuggestions ? 'bg-primary/20 text-primary' : 'bg-border/50 text-text-muted hover:text-text-deep'
                ]"
                :aria-expanded="showSuggestions"
                :aria-label="t('chat.smartSuggestions')"
              >
                <span class="text-sm">✨</span>
              </button>

              <!-- Voice Note Button -->
              <div class="relative">
                <button
                  @click="startRecording"
                  :disabled="isUploadingVoice"
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center shrink-0 touch-manipulation active:scale-90 transition-colors',
                    voiceRecordingError ? 'bg-red-100 text-red-600' : isUploadingVoice ? 'bg-gray-200 text-gray-400' : 'bg-border/50 text-text-muted hover:text-text-deep'
                  ]"
                  :aria-label="t('a11y.recordVoice')"
                >
                  <svg v-if="!isUploadingVoice" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                  </svg>
                  <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </button>
                <!-- Error tooltip -->
                <div 
                  v-if="voiceRecordingError"
                  class="absolute bottom-full mb-2 start-0 bg-red-500 text-white text-xs px-3 py-2 rounded-lg shadow-lg whitespace-nowrap z-20"
                  @click="voiceRecordingError = null"
                >
                  {{ voiceRecordingError }}
                  <div class="absolute top-full start-4 w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-red-500"></div>
                </div>
              </div>
            </div>

            <!-- Text Input Row -->
            <div class="flex items-end gap-2 bg-surface border border-border rounded-2xl px-3 py-2 shadow-soft">
              <textarea
                v-model="newMessage"
                :placeholder="t('chat.inputPlaceholder')"
                class="input-field flex-1 text-sm max-h-[120px] resize-none leading-relaxed border-0 focus:ring-0 bg-transparent min-h-[40px] py-2"
                rows="1"
                @keydown.enter.exact.prevent="sendMessage"
                enterkeyhint="send"
              ></textarea>

              <!-- Send Button -->
              <button
                @click="sendMessage"
                class="w-9 h-9 rounded-full bg-primary text-white shadow-button flex items-center justify-center shrink-0 touch-manipulation active:scale-90"
                :class="{ 'opacity-50': !newMessage.trim() }"
                :disabled="!newMessage.trim()"
              >
                <svg 
                  class="w-4 h-4" 
                  :class="{ 'flip-rtl': isRTL }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>

    <!-- Profile Edit View -->
    <div 
      v-else-if="currentView === 'profile'" 
      class="min-h-screen-safe flex flex-col relative z-10 bg-background"
    >
      <!-- Header with Sticky Save -->
      <header class="sticky top-0 z-20 bg-surface/90 backdrop-blur-lg border-b border-border header-safe">
        <div class="flex items-center justify-between px-3 xs:px-4 py-2 xs:py-3">
          <button
            @click="goBack"
            class="btn-icon bg-background shadow-soft touch-manipulation"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 xs:w-6 xs:h-6 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <div class="text-center">
            <h1 class="text-base xs:text-lg font-semibold text-text-deep">{{ t('profile.editProfile') }}</h1>
          </div>
          
          <!-- Prominent Save Button in Header -->
          <button
            @click="saveProfile"
            :disabled="isSavingProfile"
            class="bg-primary text-white font-medium px-4 py-2 rounded-full min-h-[44px] touch-manipulation active:scale-95 shadow-sm flex items-center gap-1.5 disabled:opacity-70 disabled:cursor-not-allowed"
            :aria-label="t('a11y.saveChanges')"
            :title="`${t('save')} (⌘S / Ctrl+S)`"
          >
            <svg v-if="isSavingProfile" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-else>💾</span>
            {{ isSavingProfile ? t('saving') : t('save') }}
          </button>
        </div>
      </header>
      
      <!-- Content -->
      <main class="flex-1 px-3 xs:px-4 py-4 xs:py-6 overflow-auto momentum-scroll hide-scrollbar">
        <div class="w-full space-y-4 xs:space-y-6">
          
          <!-- Photo Section -->
          <div class="animate-slide-up">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>📷</span>
              {{ t('profile.photos') }}
            </h3>
            
            <!-- Photo Grid -->
            <div class="grid grid-cols-3 gap-2 xs:gap-3">
              <!-- Empty state -->
              <div 
                v-if="!getPrimaryPhotoUrl() && userProfile.photos.length === 0"
                class="col-span-3 rounded-xl border-2 border-dashed border-border bg-surface/60 p-4 text-center text-xs text-text-muted"
              >
                {{ t('profile.addPhoto') }} — {{ t('profile.photoHint') }}
              </div>
              <!-- Main/Primary Photo -->
              <div 
                v-if="getPrimaryPhotoUrl()"
                class="relative aspect-[3/4] rounded-xl overflow-hidden ring-2 ring-primary bg-gradient-to-br from-primary/20 to-accent/20"
              >
                <img 
                  :src="getPrimaryPhotoUrl()" 
                  alt="Primary Photo"
                  class="w-full h-full object-cover"
                  @error="$event.target.style.opacity = '0'"
                />
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <span class="text-4xl opacity-30">👤</span>
                </div>
                <div class="absolute top-1 start-1 bg-primary text-white text-[10px] px-1.5 py-0.5 rounded-full font-medium z-10">
                  {{ t('profile.main') }}
                </div>
              </div>
              
              <!-- Additional Photos -->
              <div 
                v-for="(photo, index) in userProfile.photos.filter(p => !p.is_primary)"
                :key="photo.id"
                class="relative aspect-[3/4] rounded-xl overflow-hidden bg-gradient-to-br from-primary/10 to-accent/10 border border-border group"
              >
                <img 
                  :src="getPhotoUrl(photo)" 
                  :alt="`Photo ${index + 2}`"
                  class="w-full h-full object-cover"
                  @error="$event.target.style.opacity = '0'"
                />
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <span class="text-3xl opacity-30">📷</span>
                </div>
                <!-- Photo actions overlay -->
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <button 
                    @click="setPrimaryPhoto(photo.id)"
                    class="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center touch-manipulation"
                    :title="t('profile.setAsPrimary')"
                  >
                    ⭐
                  </button>
                  <button 
                    @click="deletePhoto(photo.id)"
                    class="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center touch-manipulation"
                    :title="t('delete')"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <!-- Add Photo Button -->
              <label 
                v-if="userProfile.photos.length < 6"
                class="aspect-[3/4] rounded-xl border-2 border-dashed border-primary/40 bg-primary-light/30 flex flex-col items-center justify-center cursor-pointer hover:bg-primary-light/50 transition-colors touch-manipulation"
                :class="{ 'opacity-50 cursor-not-allowed': isUploadingPhoto }"
              >
                <input 
                  type="file"
                  accept="image/*"
                  class="hidden"
                  @change="handlePhotoUpload"
                  :disabled="isUploadingPhoto"
                />
                <span v-if="isUploadingPhoto" class="text-2xl animate-spin">⏳</span>
                <span v-else class="text-2xl">➕</span>
                <span class="text-xs text-primary mt-1 font-medium">
                  {{ isUploadingPhoto ? 'Uploading...' : 'Add Photo' }}
                </span>
              </label>
            </div>
            
            <!-- Upload error -->
            <p v-if="photoUploadError" class="text-xs text-red-500 mt-2 text-center">
              {{ photoUploadError }}
            </p>
            
            <!-- Photo instructions -->
            <div class="mt-3 p-3 bg-primary-light/30 rounded-xl border border-primary/10">
              <p class="text-xs text-text-muted text-center leading-relaxed">
                {{ t('profile.photoInstructions') }}
              </p>
              <p class="text-xs text-primary font-medium mt-1 text-center">
                {{ userProfile.photos.length }}/6 {{ t('profile.photos') }}
              </p>
            </div>
          </div>

          <!-- Basic Info -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-1">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>📝</span>
              {{ t('profile.basicInfo') }}
            </h3>
            
            <div class="space-y-3 xs:space-y-4">
              <!-- Name -->
              <div>
                <label class="block text-xs xs:text-sm font-medium text-text-deep mb-1 xs:mb-1.5">
                  {{ t('profile.name') }}
                </label>
                <input 
                  v-model="userProfile.name"
                  type="text"
                  class="input-field"
                />
              </div>
              
              <!-- Age -->
              <div>
                <label class="block text-xs xs:text-sm font-medium text-text-deep mb-1 xs:mb-1.5">
                  {{ t('profile.age') }}
                </label>
                <input 
                  v-model.number="userProfile.age"
                  type="number"
                  inputmode="numeric"
                  min="18"
                  max="120"
                  class="input-field"
                />
              </div>
              
              <!-- Location -->
              <div>
                <label class="block text-xs xs:text-sm font-medium text-text-deep mb-1 xs:mb-1.5">
                  {{ t('profile.location') }}
                </label>
                <input 
                  v-model="userProfile.location"
                  type="text"
                  class="input-field"
                />
              </div>
              
              <!-- Bio -->
              <div>
                <label class="block text-xs xs:text-sm font-medium text-text-deep mb-1 xs:mb-1.5">
                  {{ t('profile.bio') }}
                </label>
                <textarea 
                  v-model="userProfile.bio"
                  rows="3"
                  class="input-field resize-none"
                  :placeholder="t('profile.bioPlaceholder')"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Profile Prompt -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-2">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>💬</span>
              {{ t('profile.prompt') }}
            </h3>
            
            <div class="space-y-3 xs:space-y-4">
              <!-- Prompt Selector -->
              <div class="flex flex-col gap-2">
                <button
                  v-for="promptId in profilePromptOptions"
                  :key="promptId"
                  @click="userProfile.promptId = promptId"
                  :class="[
                    'px-4 py-3 rounded-xl text-xs xs:text-sm font-medium transition-all touch-manipulation active:scale-[0.98] text-start',
                    userProfile.promptId === promptId 
                      ? 'bg-primary text-white shadow-md' 
                      : 'bg-primary-light text-primary border border-primary/20 hover:border-primary/40'
                  ]"
                >
                  <span class="flex items-center gap-2">
                    <span v-if="userProfile.promptId === promptId" class="text-base">✓</span>
                    <span>{{ t(`profilePrompts.${promptId}`) }}</span>
                  </span>
                </button>
              </div>
              
              <!-- Answer -->
              <div>
                <label class="block text-xs xs:text-sm font-medium text-text-deep mb-1 xs:mb-1.5">
                  {{ t('profile.promptAnswer') }}
                </label>
                <input 
                  v-model="userProfile.promptAnswer"
                  type="text"
                  class="input-field"
                  :placeholder="t(`profilePrompts.${userProfile.promptId}`)"
                />
              </div>
            </div>
          </div>

          <!-- Time Preferences -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-2">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-2 flex items-center gap-2">
              <span>⏰</span>
              {{ t('timePreferences.title') }}
            </h3>
            <p class="text-xs text-text-muted mb-4">{{ t('timePreferences.subtitle') }}</p>
            
            <div class="space-y-4">
              <!-- Preferred Times -->
              <div>
                <p class="text-xs xs:text-sm text-text-muted mb-2">{{ t('timePreferences.preferredTimes') }}</p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="time in timeOptions"
                    :key="time.id"
                    @click="toggleTime(time.id)"
                    :class="[
                      'flex items-center gap-1.5 px-3 py-2 rounded-full text-xs xs:text-sm transition-all touch-manipulation active:scale-95',
                      (userProfile.preferredTimes || []).includes(time.id)
                        ? 'bg-primary text-white'
                        : 'bg-surface border border-border text-text-muted'
                    ]"
                  >
                    <span>{{ time.emoji }}</span>
                    <span>{{ t(`timePreferences.times.${time.id}`) }}</span>
                  </button>
                </div>
              </div>
              
              <!-- Response Pace -->
              <div>
                <p class="text-xs xs:text-sm text-text-muted mb-2">{{ t('timePreferences.responsePace') }}</p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="pace in responsePaceOptions"
                    :key="pace.id"
                    @click="userProfile.responsePace = pace.id"
                    :class="[
                      'flex items-center gap-1.5 px-3 py-2 rounded-full text-xs xs:text-sm transition-all touch-manipulation active:scale-95',
                      userProfile.responsePace === pace.id
                        ? 'bg-accent text-white'
                        : 'bg-surface border border-border text-text-muted'
                    ]"
                  >
                    <span>{{ pace.emoji }}</span>
                    <span>{{ t(`timePreferences.responsePaceOptions.${pace.id}`) }}</span>
                  </button>
                </div>
              </div>
              
              <!-- Date Pace -->
              <div>
                <p class="text-xs xs:text-sm text-text-muted mb-2">{{ t('timePreferences.datePace') }}</p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="pace in datePaceOptions"
                    :key="pace.id"
                    @click="userProfile.datePace = pace.id"
                    :class="[
                      'flex items-center gap-1.5 px-3 py-2 rounded-full text-xs xs:text-sm transition-all touch-manipulation active:scale-95',
                      userProfile.datePace === pace.id
                        ? 'bg-success text-white'
                        : 'bg-surface border border-border text-text-muted'
                    ]"
                  >
                    <span>{{ pace.emoji }}</span>
                    <span>{{ t(`timePreferences.datePaceOptions.${pace.id}`) }}</span>
                  </button>
                </div>
              </div>
              
              <!-- Time Notes -->
              <div>
                <label class="block text-xs xs:text-sm font-medium text-text-deep mb-1.5">
                  {{ t('timePreferences.notes') }}
                </label>
                <input 
                  v-model="userProfile.timeNotes"
                  type="text"
                  class="input-field"
                  :placeholder="t('timePreferences.notesPlaceholder')"
                />
              </div>
            </div>
          </div>

          <!-- Identity Tags -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-3">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>🏷️</span>
              {{ t('profile.myTags') }}
            </h3>
            
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="tag in availableDisabilityTags"
                :key="tag.code"
                @click="toggleProfileTag(tag.code)"
                :class="[
                  'flex items-center gap-1.5 xs:gap-2 px-2.5 xs:px-3 py-2 xs:py-2.5 rounded-xl text-xs xs:text-sm transition-all touch-manipulation active:scale-95',
                  userProfile.tags.includes(tag.code) 
                    ? 'bg-primary text-white' 
                    : 'bg-surface border border-border text-text-muted'
                ]"
              >
                <span>{{ tag.icon }}</span>
                <span class="flex-1 text-start truncate">{{ getTagLabel(tag) }}</span>
                <span v-if="userProfile.tags.includes(tag.code)" class="text-xs">✓</span>
              </button>
            </div>
          </div>

          <!-- Tag Visibility -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-3">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>🔒</span>
              {{ t('tagVisibility.title') }}
            </h3>
            <p class="text-xs xs:text-sm text-text-muted mb-3">
              {{ t('tagVisibility.subtitle') }}
            </p>
            <div v-if="userProfile.tags.length" class="space-y-3">
              <div
                v-for="tagCode in userProfile.tags"
                :key="tagCode"
                class="bg-surface rounded-xl p-3 border border-border"
              >
                <div class="flex items-center gap-2">
                  <span class="text-lg">{{ getTagIcon(tagCode) }}</span>
                  <span class="text-sm font-semibold text-text-deep flex-1">{{ getTagLabel(tagCode) }}</span>
                  <select
                    :value="userProfile.tagVisibilities[tagCode]?.visibility || getDefaultTagVisibility(tagCode)"
                    @change="setTagVisibility(tagCode, $event.target.value)"
                    class="text-xs bg-background border border-border rounded-full px-2 py-1"
                    :aria-label="t('tagVisibility.selectAria', { tag: getTagLabel(tagCode) })"
                  >
                    <option v-for="option in tagVisibilityOptions" :key="option.id" :value="option.id">
                      {{ option.label }}
                    </option>
                  </select>
                </div>

                <div v-if="userProfile.tagVisibilities[tagCode]?.visibility === 'specific'" class="mt-2">
                  <p class="text-xs text-text-muted mb-2">{{ t('tagVisibility.choosePeople') }}</p>
                  <div v-if="matches.length" class="flex flex-wrap gap-2">
                    <label
                      v-for="match in matches"
                      :key="match.id"
                      class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border border-border bg-background text-xs"
                    >
                      <input
                        type="checkbox"
                        class="accent-primary"
                        :value="match.other_user?.id"
                        v-model="userProfile.tagVisibilities[tagCode].allowedViewerIds"
                      />
                      <span>{{ match.other_profile?.display_name || match.other_user?.username }}</span>
                    </label>
                  </div>
                  <p v-else class="text-xs text-text-muted">{{ t('tagVisibility.noMatches') }}</p>
                </div>
              </div>
            </div>
            <p v-else class="text-xs text-text-muted">{{ t('tagVisibility.noneSelected') }}</p>
          </div>

          <!-- Intent & Openness -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-3">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>🎯</span>
              {{ t('intent.title') }}
            </h3>
            <div class="flex flex-wrap gap-2 mb-4">
              <button
                v-for="intent in relationshipIntentOptions"
                :key="intent.id"
                @click="setRelationshipIntent(intent.id)"
                :class="[
                  'flex items-center gap-2 px-3 xs:px-4 py-2 xs:py-2.5 rounded-full transition-all touch-manipulation active:scale-95',
                  userProfile.relationshipIntent === intent.id
                    ? 'bg-primary text-white shadow-button'
                    : 'bg-surface border-2 border-border text-text-muted hover:border-primary/50'
                ]"
              >
                <span class="text-base">{{ intent.emoji }}</span>
                <span class="text-xs xs:text-sm font-medium">{{ t(`intent.options.${intent.id}`) }}</span>
                <span v-if="userProfile.relationshipIntent === intent.id" class="text-sm">✓</span>
              </button>
            </div>

            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 flex items-center gap-2">
              <span>🤗</span>
              {{ t('openness.title') }}
            </h3>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="option in opennessOptions"
                :key="option.id"
                @click="toggleOpennessTag(option.id)"
                :class="[
                  'flex items-center gap-2 px-3 xs:px-4 py-2 xs:py-2.5 rounded-full transition-all touch-manipulation active:scale-95',
                  userProfile.opennessTags.includes(option.id)
                    ? 'bg-secondary text-white shadow-button'
                    : 'bg-surface border-2 border-border text-text-muted hover:border-secondary/50'
                ]"
              >
                <span class="text-base">{{ option.emoji }}</span>
                <span class="text-xs xs:text-sm font-medium">{{ t(`openness.options.${option.id}`) }}</span>
                <span v-if="userProfile.opennessTags.includes(option.id)" class="text-sm">✓</span>
              </button>
            </div>
          </div>

          <!-- Looking For -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-4">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>💝</span>
              {{ t('lookingFor.title') }}
            </h3>
            
            <!-- Who are you interested in? -->
            <div class="mb-5">
              <p class="text-xs xs:text-sm text-text-muted mb-3">{{ t('lookingFor.interestedIn') }}</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="gender in genderOptions"
                  :key="gender.id"
                  @click="toggleGender(gender.id)"
                  :class="[
                    'flex items-center gap-2 px-3 xs:px-4 py-2 xs:py-2.5 rounded-full transition-all touch-manipulation active:scale-95',
                    userProfile.lookingFor.genders.includes(gender.id)
                      ? 'bg-primary text-white shadow-soft ring-2 ring-primary/30'
                      : 'bg-surface border border-border text-text-muted hover:border-primary/50'
                  ]"
                >
                  <span class="text-base">{{ gender.emoji }}</span>
                  <span class="text-xs xs:text-sm font-medium">{{ t(`lookingFor.genders.${gender.id}`) }}</span>
                  <span v-if="userProfile.lookingFor.genders.includes(gender.id)" class="text-sm">✓</span>
                </button>
              </div>
            </div>
            
            <!-- Age Range -->
            <div class="mb-5">
              <p class="text-xs xs:text-sm text-text-muted mb-3">{{ t('lookingFor.ageRange') }}</p>
              <div class="flex items-center gap-3">
                <div class="flex-1">
                  <label class="block text-[10px] xs:text-xs text-text-muted mb-1">{{ t('lookingFor.minAge') }}: {{ userProfile.lookingFor.ageRange.min }}</label>
                  <input 
                    v-model.number="userProfile.lookingFor.ageRange.min"
                    type="number"
                    inputmode="numeric"
                    min="18"
                    max="99"
                    class="input-field text-center text-sm"
                    :class="{ 'border-danger ring-danger/30': ageRangeError }"
                    @blur="normalizeAgeRange"
                  />
                </div>
                <span class="text-text-muted mt-4">–</span>
                <div class="flex-1">
                  <label class="block text-[10px] xs:text-xs text-text-muted mb-1">{{ t('lookingFor.maxAge') }}: {{ userProfile.lookingFor.ageRange.max }}</label>
                  <input 
                    v-model.number="userProfile.lookingFor.ageRange.max"
                    type="number"
                    inputmode="numeric"
                    min="18"
                    max="99"
                    class="input-field text-center text-sm"
                    :class="{ 'border-danger ring-danger/30': ageRangeError }"
                    @blur="normalizeAgeRange"
                  />
                </div>
              </div>
              <!-- Age range validation error -->
              <p v-if="ageRangeError" class="text-xs text-danger mt-2 flex items-center gap-1">
                <span>⚠️</span>
                {{ ageRangeError }}
              </p>
            </div>

            <!-- Location -->
            <div class="mb-5">
              <p class="text-xs xs:text-sm text-text-muted mb-2">{{ t('lookingFor.location') }}</p>
              <input 
                v-model="userProfile.lookingFor.location"
                type="text"
                class="input-field"
                :placeholder="t('lookingFor.locationPlaceholder')"
              />
              <p class="text-[10px] text-text-muted/70 mt-1.5 flex items-center gap-1">
                <span>💡</span>
                {{ t('lookingFor.locationHint') }}
              </p>
            </div>

            <!-- Distance - Accessible with +/- buttons and text input -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <div>
                  <label :for="'distance-input-profile'" class="text-xs xs:text-sm text-text-muted">{{ t('lookingFor.maxDistance') }}</label>
                  <p class="text-[10px] text-text-muted/70">{{ t('lookingFor.distanceRange') }}</p>
                </div>
              </div>
              
              <!-- Accessible distance control with +/- buttons and text input -->
              <div class="flex items-center gap-3 mb-3" role="group" :aria-label="t('a11y.distanceSlider', { km: userProfile.lookingFor.maxDistance })">
                <!-- Decrease button -->
                <button
                  type="button"
                  @click="userProfile.lookingFor.maxDistance = Math.max(5, userProfile.lookingFor.maxDistance - 5)"
                  class="w-12 h-12 bg-surface border-2 border-primary/30 rounded-full flex items-center justify-center text-primary font-bold text-xl touch-manipulation active:scale-90 active:bg-primary-light hover:bg-primary-light transition-colors"
                  :aria-label="t('a11y.decreaseDistance')"
                  :disabled="userProfile.lookingFor.maxDistance <= 5"
                  :class="{ 'opacity-50 cursor-not-allowed': userProfile.lookingFor.maxDistance <= 5 }"
                >
                  −
                </button>
                
                <!-- Text input for direct entry -->
                <div class="flex-1 flex items-center justify-center">
                  <input
                    id="distance-input-profile"
                    v-model.number="userProfile.lookingFor.maxDistance"
                    type="number"
                    min="5"
                    max="200"
                    step="5"
                    class="w-20 text-center text-xl font-bold text-primary bg-primary-light border-2 border-primary/30 rounded-xl py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                    :aria-label="t('lookingFor.maxDistance')"
                    @blur="userProfile.lookingFor.maxDistance = Math.min(200, Math.max(5, userProfile.lookingFor.maxDistance || 50))"
                  />
                  <span class="text-sm text-text-muted ms-2">{{ t('lookingFor.km') }}</span>
                </div>
                
                <!-- Increase button -->
                <button
                  type="button"
                  @click="userProfile.lookingFor.maxDistance = Math.min(200, userProfile.lookingFor.maxDistance + 5)"
                  class="w-12 h-12 bg-surface border-2 border-primary/30 rounded-full flex items-center justify-center text-primary font-bold text-xl touch-manipulation active:scale-90 active:bg-primary-light hover:bg-primary-light transition-colors"
                  :aria-label="t('a11y.increaseDistance')"
                  :disabled="userProfile.lookingFor.maxDistance >= 200"
                  :class="{ 'opacity-50 cursor-not-allowed': userProfile.lookingFor.maxDistance >= 200 }"
                >
                  +
                </button>
              </div>
              
              <!-- Slider as alternative input method -->
              <div class="relative">
                <input 
                  v-model.number="userProfile.lookingFor.maxDistance"
                  type="range"
                  min="5"
                  max="200"
                  step="5"
                  class="w-full h-3 bg-gradient-to-r from-primary/20 to-primary/60 rounded-full appearance-none cursor-pointer accent-primary"
                  :aria-label="t('a11y.distanceSlider', { km: userProfile.lookingFor.maxDistance })"
                  aria-hidden="true"
                />
                <!-- Distance range labels -->
                <div class="flex justify-between mt-1 text-[10px] text-text-muted">
                  <span>5 {{ t('lookingFor.km') }}</span>
                  <span>100 {{ t('lookingFor.km') }}</span>
                  <span>200 {{ t('lookingFor.km') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Interests -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-5">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>✨</span>
              {{ t('profile.myInterests') }}
            </h3>
            
            <div class="flex flex-wrap gap-2 mb-3 xs:mb-4">
              <span 
                v-for="(interest, index) in userProfile.interests"
                :key="index"
                :class="[
                  'inline-flex items-center gap-1.5 xs:gap-2 px-3 xs:px-4 py-1.5 xs:py-2 rounded-full text-xs xs:text-sm font-medium border transition-all',
                  interestColorClasses[index % interestColorClasses.length]
                ]"
              >
                {{ translateInterest(interest) }}
                <button 
                  @click="removeInterest(index)"
                  class="opacity-60 hover:opacity-100 active:text-danger touch-manipulation transition-opacity"
                >
                  ×
                </button>
              </span>
              
              <!-- Add Interest Button -->
              <button
                @click="addInterest"
                class="inline-flex items-center gap-1 px-3 xs:px-4 py-1.5 xs:py-2 border-2 border-dashed border-text-muted/30 text-text-muted rounded-full text-xs xs:text-sm font-medium touch-manipulation hover:border-primary hover:text-primary hover:bg-primary-light/50 active:border-primary active:bg-primary-light transition-all"
              >
                <span>+</span>
                {{ t('profile.addInterest') }}
              </button>
            </div>
          </div>

          <!-- Save Button -->
          <button
            @click="saveProfile"
            :disabled="isSavingProfile"
            class="w-full bg-primary text-white text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium shadow-button touch-manipulation active:scale-[0.98] animate-slide-up stagger-7 disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <svg v-if="isSavingProfile" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isSavingProfile ? t('saving') : t('profile.saveChanges') }}
          </button>
          
          <!-- Cleanup Button -->
          <!-- Invite Friends Button -->
          <button
            @click="openInviteFriends"
            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium shadow-button touch-manipulation active:scale-[0.98] mt-4 animate-slide-up stagger-7 flex items-center justify-center gap-2"
          >
            <span class="text-xl">👥</span>
            {{ t('inviteFriends.inviteButton') }}
          </button>

          <button
            @click="handleCleanup"
            class="w-full bg-surface border-2 border-amber-400/30 text-amber-600 text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium touch-manipulation active:scale-[0.98] active:bg-amber-50 mt-4 animate-slide-up stagger-8"
          >
            🧹 {{ t('profile.cleanup') }}
          </button>
          
          <!-- Logout Button -->
          <button
            @click="handleLogout"
            class="w-full bg-surface border-2 border-danger/30 text-danger text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium touch-manipulation active:scale-[0.98] active:bg-danger/10 mt-3 animate-slide-up stagger-9"
          >
            🚪 {{ t('logout') }}
          </button>
          
          <!-- Bottom spacing for safe area -->
          <div class="h-20"></div>
        </div>
      </main>
      
      <!-- Floating Save Button (FAB) - Always visible for accessibility -->
      <button
        @click="saveProfile"
        :disabled="isSavingProfile"
        class="fixed bottom-6 end-6 w-14 h-14 bg-primary text-white rounded-full shadow-lg flex items-center justify-center touch-manipulation active:scale-90 z-30 disabled:opacity-70 disabled:cursor-not-allowed"
        :class="{ 'animate-bounce-soft': !isSavingProfile }"
        :aria-label="t('a11y.saveChanges')"
        :title="`${t('save')} (⌘S / Ctrl+S)`"
      >
        <svg v-if="isSavingProfile" class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
      </button>
    </div>

    <!-- Profile View Overlay -->
    <Transition name="fade">
      <div 
        v-if="viewingProfileData"
        class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center"
        @click.self="closeProfileView"
      >
        <div class="bg-surface w-full h-full overflow-y-auto shadow-2xl animate-scale-in">
          <!-- Photo Section - Full image display -->
          <div class="relative overflow-hidden flex-shrink-0 bg-black h-[55vh]">
            <!-- Photo indicators -->
            <div 
              v-if="getAllPhotos(viewingProfileData.raw).length > 1"
              class="absolute top-3 inset-x-3 z-20 flex gap-1"
            >
              <div 
                v-for="(photo, index) in getAllPhotos(viewingProfileData.raw)"
                :key="index"
                class="flex-1 h-1 rounded-full transition-all"
                :class="index === viewingProfilePhotoIndex ? 'bg-white' : 'bg-white/40'"
              ></div>
            </div>
            
            <!-- Tap zones for photo navigation -->
            <div 
              v-if="getAllPhotos(viewingProfileData.raw).length > 1"
              class="absolute inset-0 z-10 flex"
            >
              <div 
                class="w-1/3 h-full cursor-pointer" 
                @click="prevViewingPhoto"
              ></div>
              <div class="w-1/3 h-full"></div>
              <div 
                class="w-1/3 h-full cursor-pointer" 
                @click="nextViewingPhoto"
              ></div>
            </div>
            
            <!-- Profile Photo -->
            <img 
              v-if="!viewingProfileImageError && (getAllPhotos(viewingProfileData.raw).length > 0 || viewingProfileData.raw.photo || viewingProfileData.raw.picture_url)"
              :src="getAllPhotos(viewingProfileData.raw)[viewingProfilePhotoIndex] || getPhotoUrl(viewingProfileData.raw.photo || viewingProfileData.raw.picture_url)" 
              :alt="viewingProfileData.name"
              class="w-full h-full object-contain"
              @error="viewingProfileImageError = true"
            />
            <!-- Placeholder when no photo or image error -->
            <div 
              v-else
              class="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/30 to-accent/30"
            >
              <div class="text-center">
                <span class="text-7xl block mb-3 opacity-80">👤</span>
                <span class="text-white/70 text-sm font-medium">{{ t('profile.noPhoto') || 'No photo' }}</span>
              </div>
            </div>
            
            <!-- Close button -->
            <button 
              @click="closeProfileView"
              class="absolute top-3 end-3 z-30 w-10 h-10 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center text-white touch-manipulation"
            >
              ✕
            </button>
            
            <!-- Gradient Overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none"></div>
            
            <!-- Name & Age -->
            <div class="absolute bottom-4 inset-x-4 text-white z-10">
              <h2 class="text-2xl font-bold">
                {{ viewingProfileData.name || t('profile.unknownUser') || 'User' }}
                <span v-if="viewingProfileData.age" class="font-normal text-white/80">, {{ viewingProfileData.age }}</span>
              </h2>
              <p v-if="viewingProfileData.city" class="text-white/70 text-sm flex items-center gap-1 mt-1">
                📍 {{ viewingProfileData.city }}
              </p>
            </div>
          </div>
          
          <!-- Profile Details -->
          <div class="p-5">
            <!-- Bio -->
            <div v-if="viewingProfileData.bio" class="mb-4">
              <h3 class="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">{{ t('profile.about') }}</h3>
              <p class="text-text-deep">{{ viewingProfileData.bio }}</p>
            </div>

            <!-- Intent -->
            <div v-if="viewingProfileData.relationshipIntent" class="mb-4">
              <h3 class="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">{{ t('intent.title') }}</h3>
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary-light text-primary border border-primary/20 text-xs font-medium">
                <span>🎯</span>
                <span>{{ t(`intent.options.${viewingProfileData.relationshipIntent}`) }}</span>
              </span>
            </div>

            <!-- Openness -->
            <div v-if="viewingProfileData.opennessTags?.length" class="mb-4">
              <h3 class="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">{{ t('openness.title') }}</h3>
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="tag in viewingProfileData.opennessTags"
                  :key="tag"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-secondary-light text-secondary border border-secondary/20 rounded-full text-xs font-medium"
                >
                  <span>{{ opennessOptions.find(o => o.id === tag)?.emoji }}</span>
                  <span>{{ t(`openness.options.${tag}`) }}</span>
                </span>
              </div>
            </div>
            
            <!-- Tags -->
            <div v-if="viewingProfileData.tags?.length" class="mb-4">
              <h3 class="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">{{ t('profile.myTags') }}</h3>
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="tag in viewingProfileData.tags"
                  :key="typeof tag === 'string' ? tag : tag.code"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-primary-light to-coral/20 text-primary border border-primary/20 rounded-full text-xs font-medium"
                >
                  <span class="inline-flex items-center gap-1">
                    <span>{{ getTagIcon(tag) }}</span>
                    <span>{{ getTagLabel(tag) }}</span>
                  </span>
                </span>
              </div>
            </div>
            
            <!-- Interests -->
            <div v-if="viewingProfileData.interests?.length" class="mb-4">
              <h3 class="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">{{ t('profile.interests') }}</h3>
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="(interest, idx) in viewingProfileData.interests"
                  :key="typeof interest === 'string' ? interest : interest.name"
                  :class="[
                    'px-2.5 py-1 rounded-full text-xs font-medium border',
                    interestColorClasses[idx % interestColorClasses.length]
                  ]"
                >
                  {{ translateInterest(typeof interest === 'string' ? interest : interest.name) }}
                </span>
              </div>
            </div>
            
            <!-- Time Preferences -->
            <div v-if="viewingProfileData.responsePace || viewingProfileData.datePace" class="mb-4">
              <h3 class="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <span class="text-sm">🕐</span>
                {{ t('timePreferences.title') }}
              </h3>
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-if="viewingProfileData.responsePace"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-light text-amber border border-amber/20 rounded-full text-xs font-medium"
                >
                  <span>{{ responsePaceOptions.find(p => p.id === viewingProfileData.responsePace)?.emoji }}</span>
                  <span>{{ t(`timePreferences.responsePaceOptions.${viewingProfileData.responsePace}`) }}</span>
                </span>
                <span 
                  v-if="viewingProfileData.datePace"
                  class="inline-flex items-center gap-1 px-2.5 py-1 bg-emerald-light text-emerald border border-emerald/20 rounded-full text-xs font-medium"
                >
                  <span>{{ datePaceOptions.find(p => p.id === viewingProfileData.datePace)?.emoji }}</span>
                  <span>{{ t(`timePreferences.datePaceOptions.${viewingProfileData.datePace}`) }}</span>
                </span>
              </div>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="p-5 pt-0 flex gap-2 pb-8">
            <button 
              @click="closeProfileView"
              class="flex-1 btn-secondary text-sm"
            >
              {{ t('back') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Match Animation Overlay -->
    <Transition name="fade">
      <div 
        v-if="showMatchAnimation"
        class="fixed inset-0 z-50 bg-gradient-to-br from-primary via-accent to-fuchsia-600 flex items-center justify-center"
      >
        <!-- Constellation Background -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div 
            v-for="(point, i) in constellationPoints" 
            :key="i"
            class="absolute w-1 h-1 bg-white rounded-full animate-twinkle"
            :style="{
              left: `${point.x}%`,
              top: `${point.y}%`,
              width: `${point.size}px`,
              height: `${point.size}px`,
              animationDelay: `${point.delay}s`,
            }"
          ></div>
        </div>

        <!-- Match Content -->
        <div class="text-center text-white animate-scale-in px-4 xs:px-6">
          <h2 class="text-3xl xs:text-4xl font-bold mb-2 animate-float">
            🎉 {{ t('match.title') }} 🎉
          </h2>
          <p class="text-sm xs:text-base text-white/80 mb-6 xs:mb-8">
            {{ t('match.subtitle', { name: matchedProfile?.name }) }}
          </p>

          <!-- Profile Photos -->
          <div class="flex items-center justify-center gap-3 xs:gap-4 mb-6 xs:mb-8">
            <div class="w-20 xs:w-28 h-20 xs:h-28 rounded-full border-4 border-white overflow-hidden shadow-xl animate-slide-in-left">
              <img 
                v-if="getPrimaryPhotoUrl()"
                :src="getPrimaryPhotoUrl()"
                :alt="t('nav.profile')"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-3xl xs:text-4xl">
                👤
              </div>
            </div>
            <div class="text-3xl xs:text-4xl animate-heart-beat">💜</div>
            <div class="w-20 xs:w-28 h-20 xs:h-28 rounded-full border-4 border-white overflow-hidden shadow-xl animate-slide-in-right">
              <img 
                :src="getPhotoUrl(matchedProfile?.photo || matchedProfile?.picture_url)" 
                :alt="matchedProfile?.name"
                class="w-full h-full object-cover"
              />
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col gap-3 w-full max-w-xs mx-auto">
            <button
              @click="closeMatchAndChat"
              class="bg-white text-primary font-semibold py-3.5 xs:py-4 rounded-xl xs:rounded-2xl touch-manipulation active:scale-[0.97]"
            >
              {{ t('match.sendMessage') }}
            </button>
            <button
              @click="keepDiscovering"
              class="text-white/80 font-medium py-3 touch-manipulation active:opacity-70"
            >
              {{ t('match.keepDiscovering') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Invite Friends Modal -->
    <Transition name="fade">
      <div 
        v-if="showInviteFriendsModal"
        class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
        @click.self="closeInviteFriends"
      >
        <div class="bg-surface w-full max-w-md max-h-[85vh] rounded-3xl shadow-2xl overflow-hidden animate-scale-in flex flex-col">
          <!-- Modal Header -->
          <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-5 flex-shrink-0">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="text-3xl">👥</span>
                <div>
                  <h2 class="text-xl font-bold">{{ t('inviteFriends.title') }}</h2>
                  <p class="text-sm text-white/80">{{ t('inviteFriends.subtitle') }}</p>
                </div>
              </div>
              <button 
                @click="closeInviteFriends"
                class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center touch-manipulation active:bg-white/30"
                :aria-label="t('inviteFriends.close')"
              >
                ✕
              </button>
            </div>
            
            <!-- Stats -->
            <div class="flex gap-4 mt-4 text-sm">
              <div class="flex items-center gap-1.5">
                <span class="text-lg">📨</span>
                <span>{{ invitationStats.total_sent }} {{ t('inviteFriends.stats.sent') }}</span>
              </div>
              <div class="flex items-center gap-1.5">
                <span class="text-lg">✅</span>
                <span>{{ invitationStats.accepted }} {{ t('inviteFriends.stats.accepted') }}</span>
              </div>
            </div>
          </div>
          
          <!-- Description -->
          <div class="p-4 border-b border-border bg-primary-light/30 flex-shrink-0">
            <p class="text-sm text-text-muted">{{ t('inviteFriends.description') }}</p>
          </div>
          
          <!-- Friends List -->
          <div class="flex-1 overflow-y-auto momentum-scroll">
            <!-- Loading State -->
            <div v-if="inviteFriendsLoading" class="flex flex-col items-center justify-center py-12">
              <div class="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
              <p class="mt-4 text-text-muted">{{ t('inviteFriends.loading') }}</p>
            </div>
            
            <!-- Error State -->
            <div v-else-if="inviteFriendsError" class="p-6 text-center">
              <span class="text-4xl block mb-3">😔</span>
              <p class="text-text-muted">{{ inviteFriendsError }}</p>
              <button 
                @click="fetchFacebookFriends"
                class="mt-4 px-4 py-2 bg-primary text-white rounded-full text-sm font-medium touch-manipulation"
              >
                {{ t('profile.retry') || 'Retry' }}
              </button>
            </div>
            
            <!-- No Friends -->
            <div v-else-if="facebookFriends.length === 0" class="p-6 text-center">
              <span class="text-5xl block mb-4">🤷</span>
              <h3 class="text-lg font-semibold text-text-deep mb-2">{{ t('inviteFriends.noFriends') }}</h3>
              <p class="text-sm text-text-muted mb-4">{{ t('inviteFriends.noFriendsDescription') }}</p>
              
              <!-- Share via Facebook Button -->
              <button 
                @click="shareViaFacebook"
                class="px-6 py-3 bg-[#1877F2] text-white rounded-full font-medium flex items-center gap-2 mx-auto touch-manipulation active:opacity-90"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Share on Facebook
              </button>
            </div>
            
            <!-- Friends List -->
            <div v-else class="divide-y divide-border">
              <div 
                v-for="friend in facebookFriends"
                :key="friend.id"
                class="flex items-center gap-3 p-4 hover:bg-surface-hover transition-colors"
              >
                <!-- Friend Avatar -->
                <div class="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-accent/20 flex-shrink-0">
                  <img 
                    v-if="friend.picture_url"
                    :src="friend.picture_url"
                    :alt="friend.name"
                    class="w-full h-full object-cover"
                    @error="$event.target.style.display = 'none'"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-xl">
                    👤
                  </div>
                </div>
                
                <!-- Friend Info -->
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-text-deep truncate">{{ friend.name }}</p>
                  <p v-if="friend.is_app_user" class="text-xs text-primary font-medium">
                    ✨ {{ t('inviteFriends.alreadyOnApp') }}
                  </p>
                </div>
                
                <!-- Action Button -->
                <button 
                  v-if="!friend.is_app_user"
                  @click="sendInvitation(friend)"
                  :disabled="friend.already_invited"
                  :class="[
                    'px-4 py-2 rounded-full text-sm font-medium transition-all touch-manipulation flex-shrink-0',
                    friend.already_invited
                      ? 'bg-surface border border-primary/30 text-primary'
                      : 'bg-primary text-white active:scale-95'
                  ]"
                >
                  <span v-if="friend.already_invited" class="flex items-center gap-1">
                    ✓ {{ t('inviteFriends.invited') }}
                  </span>
                  <span v-else>{{ t('inviteFriends.invite') }}</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Footer with Share Button -->
          <div class="p-4 border-t border-border bg-surface flex-shrink-0">
            <button 
              @click="shareViaFacebook"
              class="w-full py-3 bg-[#1877F2] text-white rounded-xl font-medium flex items-center justify-center gap-2 touch-manipulation active:opacity-90"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Share via Facebook
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Aurora Background Effect */
.aurora-bg {
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 50%, #FCE7F3 100%);
}

.aurora {
  position: absolute;
  filter: blur(80px);
  opacity: 0.5;
  border-radius: 50%;
  animation: aurora-drift 20s ease-in-out infinite;
}

.aurora-1 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #4F46E5 0%, #A855F7 100%);
  top: -100px;
  right: -50px;
  animation-delay: 0s;
}

.aurora-2 {
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #F472B6 0%, #FB7185 100%);
  bottom: -75px;
  left: -50px;
  animation-delay: -7s;
}

.aurora-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #22D3EE 0%, #6366F1 100%);
  top: 40%;
  left: 30%;
  animation-delay: -14s;
}

@media (min-width: 640px) {
  .aurora-1 { width: 600px; height: 600px; top: -200px; right: -100px; }
  .aurora-2 { width: 500px; height: 500px; bottom: -150px; left: -100px; }
  .aurora-3 { width: 400px; height: 400px; }
}

@keyframes aurora-drift {
  0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
  25% { transform: translate(30px, -30px) rotate(5deg) scale(1.05); }
  50% { transform: translate(-20px, 20px) rotate(-3deg) scale(0.95); }
  75% { transform: translate(10px, 10px) rotate(2deg) scale(1.02); }
}

@keyframes ping-slow {
  0% { transform: scale(1); opacity: 0.5; }
  75%, 100% { transform: scale(1.5); opacity: 0; }
}

.animate-ping-slow {
  animation: ping-slow 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.5); }
}

.animate-twinkle {
  animation: twinkle 2s ease-in-out infinite;
}

/* Reduced motion */
.reduce-motion * {
  animation: none !important;
  transition-duration: 0.01ms !important;
}

/* High contrast mode */
.high-contrast {
  --text-deep: #000;
  --text-muted: #333;
  --primary: #0000EE;
  --border: #000;
}

.high-contrast .bg-surface {
  background: #fff;
  border: 2px solid #000;
}

/* Dark mode - Fully dark */
.dark-mode {
  color-scheme: dark;
}

.dark-mode .bg-background,
.dark-mode.bg-background {
  background: #000000 !important;
}

.dark-mode .bg-background\/95 {
  background: rgba(0, 0, 0, 0.95) !important;
}

.dark-mode .bg-background\/70 {
  background: rgba(0, 0, 0, 0.7) !important;
}

.dark-mode .bg-background\/60 {
  background: rgba(0, 0, 0, 0.6) !important;
}

.dark-mode .bg-surface,
.dark-mode.bg-surface {
  background: #0A0A0A !important;
}

.dark-mode .bg-surface\/90 {
  background: rgba(10, 10, 10, 0.9) !important;
}

.dark-mode .bg-surface\/95 {
  background: rgba(10, 10, 10, 0.95) !important;
}

.dark-mode .bg-white {
  background: #0A0A0A !important;
}

.dark-mode .bg-border {
  background: #1A1A1A !important;
}

.dark-mode .bg-border\/60 {
  background: rgba(26, 26, 26, 0.6) !important;
}

.dark-mode .bg-background-alt {
  background: #050505 !important;
}

.dark-mode .text-text-deep,
.dark-mode.text-text-deep {
  color: #FFFFFF !important;
}

.dark-mode .text-text-muted {
  color: #A0A0A0 !important;
}

.dark-mode .text-text-light {
  color: #707070 !important;
}

.dark-mode .text-black {
  color: #FFFFFF !important;
}

.dark-mode .text-gray-900 {
  color: #FFFFFF !important;
}

.dark-mode .text-gray-800 {
  color: #E5E5E5 !important;
}

.dark-mode .text-gray-700 {
  color: #D0D0D0 !important;
}

.dark-mode .text-gray-600 {
  color: #A0A0A0 !important;
}

.dark-mode .text-gray-500 {
  color: #808080 !important;
}

.dark-mode .border-border {
  border-color: #1F1F1F !important;
}

.dark-mode .border-border\/70 {
  border-color: rgba(31, 31, 31, 0.7) !important;
}

.dark-mode .border-border\/60 {
  border-color: rgba(31, 31, 31, 0.6) !important;
}

.dark-mode .border-gray-200,
.dark-mode .border-gray-300 {
  border-color: #1F1F1F !important;
}

.dark-mode .shadow-soft,
.dark-mode .shadow-card {
  box-shadow: none !important;
}

/* Dark mode buttons */
.dark-mode .btn-secondary {
  background: #0A0A0A !important;
  border-color: #1F1F1F !important;
  color: #FFFFFF !important;
}

.dark-mode .btn-secondary:hover {
  border-color: #10A37F !important;
}

.dark-mode .btn-icon {
  background: #0A0A0A !important;
  border-color: #1F1F1F !important;
}

/* Dark mode cards */
.dark-mode .card {
  background: #0A0A0A !important;
  box-shadow: none !important;
}

/* Dark mode chips */
.dark-mode .chip {
  background: #0A0A0A !important;
  border-color: #1F1F1F !important;
  color: #FFFFFF !important;
}

.dark-mode .chip-active {
  background: #0F2A23 !important;
  border-color: #10A37F !important;
}

/* Dark mode inputs */
.dark-mode .input-field,
.dark-mode input,
.dark-mode textarea,
.dark-mode select {
  background: #0A0A0A !important;
  border-color: #1F1F1F !important;
  color: #FFFFFF !important;
}

.dark-mode input::placeholder,
.dark-mode textarea::placeholder {
  color: #505050 !important;
}

.dark-mode input:focus,
.dark-mode textarea:focus,
.dark-mode .input-field:focus {
  border-color: #10A37F !important;
  background: #050505 !important;
}

/* Dark mode glass effect */
.dark-mode .glass {
  background: rgba(0, 0, 0, 0.85) !important;
  border-color: rgba(31, 31, 31, 0.8) !important;
}

/* Dark mode scrollbar */
.dark-mode::-webkit-scrollbar-track {
  background: #0A0A0A !important;
}

.dark-mode::-webkit-scrollbar-thumb {
  background: #2A2A2A !important;
}

.dark-mode::-webkit-scrollbar-thumb:hover {
  background: #3A3A3A !important;
}

/* Dark mode dividers */
.dark-mode .divide-border > :not([hidden]) ~ :not([hidden]) {
  border-color: #1F1F1F !important;
}

/* Dark mode light backgrounds */
.dark-mode .bg-primary-light {
  background: #0F2A23 !important;
}

.dark-mode .bg-primary-light\/30 {
  background: rgba(15, 42, 35, 0.3) !important;
}

.dark-mode .bg-primary-light\/50 {
  background: rgba(15, 42, 35, 0.5) !important;
}

.dark-mode .bg-secondary-light {
  background: #0A2622 !important;
}

.dark-mode .bg-teal-light {
  background: #0A2622 !important;
}

.dark-mode .bg-rose-light {
  background: #2A1418 !important;
}

.dark-mode .bg-violet-light {
  background: #1A1528 !important;
}

.dark-mode .bg-amber-light {
  background: #2A2010 !important;
}

.dark-mode .bg-indigo-light {
  background: #14162A !important;
}

.dark-mode .bg-emerald-light {
  background: #0A2A1A !important;
}

.dark-mode .bg-gray-100,
.dark-mode .bg-gray-200 {
  background: #1A1A1A !important;
}

.dark-mode .bg-red-100 {
  background: #2A1414 !important;
}

.dark-mode .bg-border\/50 {
  background: rgba(26, 26, 26, 0.5) !important;
}

/* Dark mode for surface with backdrop blur */
.dark-mode [class*="bg-surface"][class*="backdrop-blur"] {
  background: rgba(0, 0, 0, 0.85) !important;
}

/* Dark mode for gradient backgrounds */
.dark-mode .bg-gradient-mesh {
  background: radial-gradient(at 40% 20%, #0A1A15 0px, transparent 50%), radial-gradient(at 80% 0%, #0A1A15 0px, transparent 50%), radial-gradient(at 0% 50%, #0A0A0A 0px, transparent 50%) !important;
}

/* Dark mode dividers and separators */
.dark-mode .border-t,
.dark-mode .border-b,
.dark-mode .border-y {
  border-color: #1F1F1F !important;
}

.dark-mode .border-primary\/20 {
  border-color: rgba(16, 163, 127, 0.2) !important;
}

/* Ensure modal backgrounds are dark */
.dark-mode .fixed.inset-0[class*="bg-"] {
  background-color: rgba(0, 0, 0, 0.9) !important;
}

/* Dark mode for any remaining white backgrounds */
.dark-mode [class*="bg-white"] {
  background: #0A0A0A !important;
}

/* Dark mode for gradient prompt cards and light gradients */
.dark-mode [class*="bg-gradient"][class*="from-primary-light"],
.dark-mode [class*="bg-gradient"][class*="from-secondary-light"],
.dark-mode [class*="bg-gradient"][class*="via-peach"],
.dark-mode [class*="bg-gradient"][class*="to-accent"] {
  background: linear-gradient(135deg, #0F1A17 0%, #0A0A0A 50%, #0A0A0A 100%) !important;
  border-color: #1F1F1F !important;
}

/* Override Tailwind gradient colors in dark mode */
.dark-mode .from-primary-light {
  --tw-gradient-from: #0F2A23 !important;
}

.dark-mode .via-peach,
.dark-mode .via-peach\/40 {
  --tw-gradient-via: #1A1A1A !important;
}

.dark-mode .to-accent,
.dark-mode .to-accent\/20 {
  --tw-gradient-to: #0A0A0A !important;
}

.dark-mode .to-coral,
.dark-mode .to-coral\/20 {
  --tw-gradient-to: #0A1A1A !important;
}

.dark-mode .from-coral {
  --tw-gradient-from: #0A2020 !important;
}

/* Dark mode hover states */
.dark-mode .hover\:bg-background:hover {
  background: #050505 !important;
}

.dark-mode .hover\:bg-surface:hover {
  background: #111111 !important;
}

/* Dark mode for body background */
.dark-mode body,
body.dark-mode {
  background: #000000 !important;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s ease;
}

.scale-enter-from,
.scale-leave-to {
  transform: scale(0.8);
  opacity: 0;
}

/* RTL flip for back arrow */
[dir="rtl"] .flip-rtl {
  transform: scaleX(-1);
}

/* Min height for dynamic viewport */
.min-h-screen-safe {
  min-height: 100vh;
  min-height: 100dvh;
}

/* Header safe area */
.header-safe {
  padding-top: max(0.5rem, env(safe-area-inset-top));
}

/* Bottom bar safe area */
.bottom-bar-safe {
  padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
}
</style>
