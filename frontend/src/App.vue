<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from './composables/useI18n'
import { useAuth } from './composables/useAuth'
import { profileApi, matchingApi, chatApi, clearCache } from './services/api'

const { t, locale, isRTL, dir, setLocale, getLanguages } = useI18n()

const { 
  user, 
  isLoading: authLoading, 
  error: authError, 
  isAuthenticated,
  login, 
  logout, 
  validateToken,
  updateLanguage,
  hasFacebookConfig 
} = useAuth()

// App loading state for smoother transitions
const appLoading = ref(true)

// Get all available languages
const availableLanguages = getLanguages()

// Current view state
const currentView = ref('login') // 'login', 'language', 'onboarding', 'onboarding-preferences', 'discovery', 'matches', 'chat', 'profile'

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
})
const showA11yPanel = ref(false)

// Current mood/energy
const currentMood = ref('open')

const moodOptions = [
  { id: 'lowEnergy', emoji: '🌙' },
  { id: 'open', emoji: '🌸' },
  { id: 'chatty', emoji: '💬' },
  { id: 'adventurous', emoji: '✨' },
]

// User profile data (editable)
const userProfile = ref({
  name: 'Alex',
  age: 29,
  location: 'Tel Aviv',
  photo: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop',
  bio: '',
  tags: [],
  interests: ['Music', 'Reading', 'Hiking'],
  promptId: 'laughMost',
  promptAnswer: '',
  lookingFor: {
    genders: [], // 'men', 'women', 'nonbinary', 'everyone'
    relationshipTypes: [], // 'dating', 'serious', 'friends', 'activity'
    ageRange: { min: 18, max: 50 },
    maxDistance: 50, // km
    location: '', // City/area
  },
})

// Looking for options
const genderOptions = [
  { id: 'men', emoji: '👨' },
  { id: 'women', emoji: '👩' },
  { id: 'nonbinary', emoji: '🧑' },
  { id: 'everyone', emoji: '💫' },
]

const relationshipOptions = [
  { id: 'dating', emoji: '💕', gradient: 'from-pink-400 to-rose-500' },
  { id: 'serious', emoji: '💍', gradient: 'from-violet-400 to-purple-500' },
  { id: 'friends', emoji: '🤝', gradient: 'from-cyan-400 to-blue-500' },
  { id: 'activity', emoji: '🎯', gradient: 'from-amber-400 to-orange-500' },
]

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

const toggleRelationship = (relId) => {
  const rels = userProfile.value.lookingFor.relationshipTypes
  const index = rels.indexOf(relId)
  if (index > -1) {
    rels.splice(index, 1)
  } else {
    rels.push(relId)
  }
}

// Available profile prompts
const profilePromptOptions = ['laughMost', 'perfectSunday', 'convinced']

// Mock profile data for discovery
const mockProfiles = [
  {
    id: 1,
    name: 'Maya',
    age: 28,
    distance: 3,
    photo: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=500&fit=crop',
    bio: {
      en: 'Wheelchair user who loves adaptive yoga and photography. Looking for genuine connections.',
      he: 'מתניידת בכיסא גלגלים שאוהבת יוגה מותאמת וצילום. מחפשת חיבורים אמיתיים.',
      es: 'Usuaria de silla de ruedas que ama el yoga adaptativo y la fotografía.',
      fr: "Utilisatrice de fauteuil roulant qui aime le yoga adapté et la photographie.",
      ar: 'مستخدمة كرسي متحرك تحب اليوغا والتصوير. أبحث عن اتصالات حقيقية.',
    },
    tags: ['wheelchairUser', 'chronicIllness'],
    interests: {
      en: ['Photography', 'Yoga', 'Art'],
      he: ['צילום', 'יוגה', 'אמנות'],
      es: ['Fotografía', 'Yoga', 'Arte'],
      fr: ['Photographie', 'Yoga', 'Art'],
      ar: ['التصوير', 'اليوغا', 'الفن'],
    },
    mood: 'open',
    compatibility: 87,
    promptId: 'laughMost',
    promptAnswer: {
      en: 'When my cat judges my life choices',
      he: 'כשהחתול שלי שופט את הבחירות שלי בחיים',
      es: 'Cuando mi gato juzga mis decisiones de vida',
      fr: 'Quand mon chat juge mes choix de vie',
      ar: 'عندما تحكم قطتي على خياراتي في الحياة',
    },
  },
  {
    id: 2,
    name: 'Daniel',
    age: 32,
    distance: 7,
    photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop',
    bio: {
      en: 'Deaf artist and coffee enthusiast. I communicate in sign language.',
      he: 'אמן חרש וחובב קפה. מתקשר בשפת סימנים.',
      es: 'Artista sordo y entusiasta del café.',
      fr: "Artiste sourd et amateur de café.",
      ar: 'فنان أصم ومحب للقهوة.',
    },
    tags: ['deafHoh', 'neurodivergent'],
    interests: {
      en: ['Coffee', 'Art', 'Sign Language'],
      he: ['קפה', 'אמנות', 'שפת סימנים'],
      es: ['Café', 'Arte', 'Lengua de Señas'],
      fr: ['Café', 'Art', 'Langue des Signes'],
      ar: ['القهوة', 'الفن', 'لغة الإشارة'],
    },
    mood: 'chatty',
    compatibility: 73,
    promptId: 'perfectSunday',
    promptAnswer: {
      en: 'Gallery hopping, then sketching at a quiet café',
      he: 'סיור בגלריות, ואז ציור בבית קפה שקט',
      es: 'Recorriendo galerías, luego dibujando en un café',
      fr: 'Faire le tour des galeries, puis dessiner',
      ar: 'زيارة المعارض، ثم الرسم في مقهى هادئ',
    },
  },
  {
    id: 3,
    name: 'Noa',
    age: 26,
    distance: 5,
    photo: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop',
    bio: {
      en: 'Neurodivergent tech enthusiast. I appreciate patience and understanding.',
      he: 'נוירו-מגוונת וחובבת טכנולוגיה. מעריכה סבלנות והבנה.',
      es: 'Entusiasta de la tecnología neurodivergente.',
      fr: "Passionnée de technologie neurodivergente.",
      ar: 'متحمسة للتكنولوجيا ومتباينة عصبياً.',
    },
    tags: ['neurodivergent', 'autism'],
    interests: {
      en: ['Gaming', 'Coding', 'Sci-Fi'],
      he: ['גיימינג', 'תכנות', 'מדע בדיוני'],
      es: ['Juegos', 'Programación', 'Ciencia Ficción'],
      fr: ['Jeux Vidéo', 'Programmation', 'Science-Fiction'],
      ar: ['الألعاب', 'البرمجة', 'الخيال العلمي'],
    },
    mood: 'lowEnergy',
    compatibility: 92,
    promptId: 'convinced',
    promptAnswer: {
      en: 'Robots will eventually appreciate good memes',
      he: 'רובוטים יום אחד יעריכו ממים טובים',
      es: 'Los robots apreciarán los buenos memes',
      fr: 'Les robots apprécieront les bons memes',
      ar: 'الروبوتات ستقدر الميمات الجيدة',
    },
  },
]

const currentProfileIndex = ref(0)

// Discovery profiles from backend (falls back to mock)
const discoveryProfiles = ref([])
const noMoreProfiles = ref(false)

// Current profile - prioritize backend data, normalized for template
const currentProfile = computed(() => {
  const profiles = discoveryProfiles.value.length > 0 ? discoveryProfiles.value : mockProfiles
  const profile = profiles[currentProfileIndex.value]
  if (!profile) return null
  
  // Normalize backend profile format to match expected template format
  const isBackendProfile = discoveryProfiles.value.length > 0
  
  if (isBackendProfile) {
    // Backend profile format - normalize it
    const primaryPhoto = profile.primary_photo?.image || profile.picture_url || 
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
    }
  }
  
  // Mock profile - return as-is
  return profile
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

// Matches and conversations from backend
const matches = ref([])
const conversations = ref([])

// Mock chat data
// Chat state
const currentConversation = ref(null)
const chatMessages = ref([])
const chatPartner = ref({
  name: '',
  photo: '',
  isOnline: true,
})

// Legacy mockChat for compatibility (will be replaced with chatMessages)
const mockChat = computed(() => ({
  matchName: chatPartner.value.name,
  matchPhoto: chatPartner.value.photo,
  isOnline: chatPartner.value.isOnline,
  messages: chatMessages.value.map(msg => ({
    id: msg.id,
    sender: msg.is_mine ? 'me' : 'them',
    text: { en: msg.content, he: msg.content, es: msg.content, fr: msg.content, ar: msg.content },
    time: new Date(msg.sent_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
    reaction: null,
    isRead: msg.is_read,
  })),
}))

const newMessage = ref('')

// Message reactions
const reactions = [
  { emoji: '💜', label: 'Love' },
  { emoji: '🤗', label: 'Hug' },
  { emoji: '💪', label: 'Strength' },
  { emoji: '🌟', label: 'Shine' },
]

// Tag definitions with gradient colors
const disabilityTags = [
  { id: 'wheelchairUser', icon: '♿', gradient: 'from-blue-500 to-cyan-400' },
  { id: 'neurodivergent', icon: '🧠', gradient: 'from-purple-500 to-pink-400' },
  { id: 'deafHoh', icon: '🦻', gradient: 'from-amber-500 to-orange-400' },
  { id: 'blindLowVision', icon: '👁️', gradient: 'from-emerald-500 to-teal-400' },
  { id: 'chronicIllness', icon: '💊', gradient: 'from-rose-500 to-pink-400' },
  { id: 'mentalHealth', icon: '💚', gradient: 'from-green-500 to-emerald-400' },
  { id: 'mobility', icon: '🚶', gradient: 'from-indigo-500 to-blue-400' },
  { id: 'cognitive', icon: '💭', gradient: 'from-violet-500 to-purple-400' },
  { id: 'invisible', icon: '🔮', gradient: 'from-fuchsia-500 to-pink-400' },
  { id: 'acquired', icon: '⭐', gradient: 'from-yellow-500 to-amber-400' },
  { id: 'caregiver', icon: '🤝', gradient: 'from-sky-500 to-blue-400' },
  { id: 'autism', icon: '♾️', gradient: 'from-red-500 to-orange-400' },
]

// Icebreaker prompts
const icebreakers = computed(() => [
  { id: 'comfortShow', text: t('icebreakerPrompts.comfortShow') },
  { id: 'idealDay', text: t('icebreakerPrompts.idealDay') },
  { id: 'proudOf', text: t('icebreakerPrompts.proudOf') },
])

const showIcebreakers = ref(false)

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
  })
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
  const deltaTime = Date.now() - touchStartTime.value
  const velocity = Math.abs(deltaX) / deltaTime
  
  // Check if swipe was fast enough or far enough
  const isQuickSwipe = velocity > VELOCITY_THRESHOLD && Math.abs(deltaX) > 30
  const isFarEnough = Math.abs(cardOffset.value) > SWIPE_THRESHOLD
  
  if (isQuickSwipe || isFarEnough) {
    // Complete the swipe animation
    animateSwipeOut(deltaX > 0 ? 'right' : 'left')
  } else {
    // Snap back to center with spring animation
    animateSnapBack()
  }
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
  
  currentView.value = 'onboarding'
}

const toggleTag = (tagId) => {
  const index = selectedTags.value.indexOf(tagId)
  if (index === -1) {
    selectedTags.value.push(tagId)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

const toggleProfileTag = (tagId) => {
  const index = userProfile.value.tags.indexOf(tagId)
  if (index === -1) {
    userProfile.value.tags.push(tagId)
  } else {
    userProfile.value.tags.splice(index, 1)
  }
}

const goToDiscovery = async () => {
  userProfile.value.tags = [...selectedTags.value]
  currentView.value = 'discovery'
  
  // Fetch fresh discovery profiles based on new preferences
  if (isAuthenticated.value) {
    currentProfileIndex.value = 0
    await fetchDiscoveryProfiles()
  }
}

const passProfile = async () => {
  // Record swipe in backend if authenticated
  if (isAuthenticated.value && currentProfile.value) {
    try {
      // Use user_id for backend profiles, id for mock
      const profileId = currentProfile.value.user_id || currentProfile.value.id
      await matchingApi.swipe(profileId, 'pass')
    } catch (err) {
      console.warn('Could not record swipe:', err.message)
    }
  }
  
  const profiles = discoveryProfiles.value.length > 0 ? discoveryProfiles.value : mockProfiles
  if (currentProfileIndex.value < profiles.length - 1) {
    currentProfileIndex.value++
  } else {
    // No more profiles
    noMoreProfiles.value = true
    // Try to fetch more from backend
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
        return
      }
    } catch (err) {
      console.warn('Could not record like:', err.message)
    }
  }
  
  // Fallback to mock match animation (for demo purposes)
  matchedProfile.value = currentProfile.value
  showMatchAnimation.value = true
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
      noMoreProfiles.value = true
    }
  } catch (err) {
    console.warn('Could not fetch discovery profiles:', err.message)
  }
}

// Fetch user's matches
const fetchMatches = async () => {
  if (!isAuthenticated.value) return
  
  try {
    const result = await matchingApi.getMatches()
    matches.value = result.results || result || []
  } catch (err) {
    console.warn('Could not fetch matches:', err.message)
  }
}

// Fetch user's conversations  
const fetchConversations = async () => {
  if (!isAuthenticated.value) return
  
  try {
    const result = await chatApi.getConversations()
    conversations.value = result.results || result || []
  } catch (err) {
    console.warn('Could not fetch conversations:', err.message)
  }
}

const closeMatchAndChat = () => {
  showMatchAnimation.value = false
  currentView.value = 'chat'
}

const goBack = () => {
  if (currentView.value === 'language') {
    currentView.value = 'login'
    loggedInWith.value = null
  } else if (currentView.value === 'onboarding') {
    currentView.value = 'language'
  } else if (currentView.value === 'onboarding-preferences') {
    currentView.value = 'onboarding'
  } else if (currentView.value === 'discovery') {
    currentView.value = 'onboarding-preferences'
  } else if (currentView.value === 'matches') {
    currentView.value = 'discovery'
  } else if (currentView.value === 'chat') {
    currentView.value = 'matches'
  } else if (currentView.value === 'profile') {
    currentView.value = 'discovery'
  }
}

const goToPreferences = () => {
  currentView.value = 'onboarding-preferences'
}

const goToProfile = () => {
  currentView.value = 'profile'
}

const goToMatches = async () => {
  currentView.value = 'matches'
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
  
  // Set up chat partner info
  chatPartner.value = {
    name: profile.name || profile.display_name || profile.first_name || 'Unknown',
    photo: profile.picture_url || '',
    isOnline: true,
  }
  
  // Get conversation ID from match
  currentConversation.value = match.conversation_id || null
  chatMessages.value = []
  
  // Fetch messages from API if we have a conversation
  if (currentConversation.value && isAuthenticated.value) {
    try {
      const messages = await chatApi.getMessages(currentConversation.value)
      chatMessages.value = messages.results || messages || []
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }
  
  currentView.value = 'chat'
}

const sendMessage = async () => {
  if (newMessage.value.trim() && currentConversation.value) {
    const text = newMessage.value
    newMessage.value = '' // Clear immediately for UX
    
    // Optimistically add the message
    const tempMessage = {
      id: Date.now(),
      content: text,
      is_mine: true,
      sender: 'me',
      sent_at: new Date().toISOString(),
      is_read: false,
    }
    chatMessages.value.push(tempMessage)
    
    // Send to API
    try {
      const response = await chatApi.sendMessage(currentConversation.value, text)
      // Replace temp message with real one
      const index = chatMessages.value.findIndex(m => m.id === tempMessage.id)
      if (index !== -1) {
        chatMessages.value[index] = response
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      // Remove the temp message on failure
      chatMessages.value = chatMessages.value.filter(m => m.id !== tempMessage.id)
      // Restore the message text
      newMessage.value = text
    }
  }
}

const sendIcebreaker = async (prompt) => {
  if (!currentConversation.value) return
  
  // Optimistically add the message
  const tempMessage = {
    id: Date.now(),
    content: prompt.text,
    is_mine: true,
    sender: 'me',
    sent_at: new Date().toISOString(),
    is_read: false,
    isIcebreaker: true,
  }
  chatMessages.value.push(tempMessage)
  showIcebreakers.value = false
  
  // Send to API
  try {
    const response = await chatApi.sendMessage(currentConversation.value, prompt.text, 'icebreaker')
    const index = chatMessages.value.findIndex(m => m.id === tempMessage.id)
    if (index !== -1) {
      chatMessages.value[index] = response
    }
  } catch (error) {
    console.error('Failed to send icebreaker:', error)
    chatMessages.value = chatMessages.value.filter(m => m.id !== tempMessage.id)
  }
}

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
  // Save profile to backend if authenticated
  if (isAuthenticated.value) {
    try {
      // Find tag IDs from codes
      const tagIds = backendTags.value
        .filter(t => selectedTags.value.includes(t.code))
        .map(t => t.id)
      
      await profileApi.updateProfile({
        display_name: userProfile.value.name,
        bio: userProfile.value.bio,
        city: userProfile.value.location,
        disability_tag_ids: tagIds,
        current_mood: currentMood.value,
        prompt_id: userProfile.value.promptId,
        prompt_answer: userProfile.value.promptAnswer,
      })
      
      // Save looking for preferences
      await profileApi.updateLookingFor({
        genders: userProfile.value.lookingFor.genders,
        relationship_types: userProfile.value.lookingFor.relationshipTypes,
        min_age: userProfile.value.lookingFor.ageRange.min,
        max_age: userProfile.value.lookingFor.ageRange.max,
        max_distance: userProfile.value.lookingFor.maxDistance,
        preferred_location: userProfile.value.lookingFor.location,
      })
      
      console.log('Profile saved to backend')
    } catch (err) {
      console.warn('Could not save profile to backend:', err.message)
    }
  }
  
  currentView.value = 'discovery'
}

// Social login handler
const handleSocialLogin = async (provider) => {
  loginError.value = null
  
  const result = await login(provider)
  
  if (result.success) {
    loggedInWith.value = provider
    
    // Update user profile with data from social login
    if (result.facebookData) {
      userProfile.value.name = result.facebookData.name || userProfile.value.name
      if (result.facebookData.picture_url) {
        userProfile.value.photo = result.facebookData.picture_url
      }
    }
    
    // Navigate to language selection
    currentView.value = 'language'
  } else {
    loginError.value = result.error || 'Login failed. Please try again.'
  }
}

// Backend data state
const backendTags = ref([])
const backendProfiles = ref([])
const useBackendData = ref(false)

// Fetch initial data from backend
// Optimized parallel data fetching
const initializeApp = async () => {
  appLoading.value = true
  
  try {
    // Start fetching tags immediately (doesn't require auth)
    const tagsPromise = profileApi.getTags().catch(() => null)
    
    // Validate token
    const isValid = await validateToken()
    
    if (isValid && user.value) {
      loggedInWith.value = user.value.social_provider || 'facebook'
      currentView.value = 'language'
      
      // Fetch profile, tags, discovery profiles, matches, and conversations in parallel
      const [profile, tagsResponse, discoverResponse, matchesResponse, conversationsResponse] = await Promise.all([
        profileApi.getMyProfile().catch(() => null),
        tagsPromise,
        matchingApi.discover().catch(() => []),
        matchingApi.getMatches().catch(() => ({ results: [] })),
        chatApi.getConversations().catch(() => ({ results: [] })),
      ])
      
      // Process tags
      if (tagsResponse && (tagsResponse.results || tagsResponse.length)) {
        backendTags.value = tagsResponse.results || tagsResponse
        useBackendData.value = true
      }
      
      // Process discovery profiles
      if (discoverResponse && discoverResponse.length > 0) {
        discoveryProfiles.value = discoverResponse
        noMoreProfiles.value = false
      }
      
      // Process matches
      matches.value = matchesResponse?.results || matchesResponse || []
      
      // Process conversations
      conversations.value = conversationsResponse?.results || conversationsResponse || []
      
      // Process profile
      if (profile) {
        userProfile.value = {
          ...userProfile.value,
          name: profile.display_name || userProfile.value.name,
          bio: profile.bio || '',
          location: profile.city || userProfile.value.location,
          tags: (profile.disability_tags || []).map(t => t.code),
          interests: (profile.interests || []).map(i => i.name),
          promptId: profile.prompt_id || userProfile.value.promptId,
          promptAnswer: profile.prompt_answer || '',
          age: profile.age || userProfile.value.age,
          photo: profile.picture_url || userProfile.value.photo,
        }
        selectedTags.value = userProfile.value.tags
        currentMood.value = profile.current_mood || 'open'
        
        // Load looking for preferences
        if (profile.looking_for) {
          userProfile.value.lookingFor = {
            genders: profile.looking_for.genders || [],
            relationshipTypes: profile.looking_for.relationship_types || [],
            ageRange: {
              min: profile.looking_for.min_age || 18,
              max: profile.looking_for.max_age || 50,
            },
            maxDistance: profile.looking_for.max_distance || 50,
            location: profile.looking_for.preferred_location || '',
          }
        }
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
    console.warn('Initialization error:', err.message)
    useBackendData.value = false
  } finally {
    appLoading.value = false
  }
}

// Check for existing auth on mount
onMounted(() => {
  initializeApp()
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
      textSizeClass,
      a11ySettings.highContrast ? 'high-contrast' : '',
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
          <p class="text-text-muted text-lg font-medium">Loading...</p>
        </div>
      </div>
    </Transition>

    <!-- Organic Blob Background - only render after initial load for performance -->
    <div v-if="!appLoading" class="fixed inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
      <div class="blob blob-primary w-[300px] h-[300px] -top-24 -end-24"></div>
      <div class="blob blob-secondary w-[250px] h-[250px] top-1/2 -start-32"></div>
    </div>
    
    <!-- Static gradient background - lighter than animated blobs -->
    <div class="fixed inset-0 pointer-events-none bg-organic-pattern opacity-40" aria-hidden="true"></div>

    <!-- Accessibility Quick Settings Button -->
    <button
      v-if="!isKeyboardOpen"
      @click="showA11yPanel = !showA11yPanel"
      class="fixed bottom-20 xs:bottom-24 end-3 xs:end-4 z-50 w-11 h-11 xs:w-12 xs:h-12 bg-surface rounded-full shadow-card flex items-center justify-center active:scale-95 transition-transform touch-manipulation"
      :aria-label="t('a11y.title')"
    >
      <span class="text-lg xs:text-xl">⚙️</span>
    </button>

    <!-- Accessibility Panel -->
    <Transition name="slide-up">
      <div 
        v-if="showA11yPanel"
        class="fixed bottom-32 xs:bottom-40 end-3 xs:end-4 z-50 bg-surface rounded-2xl shadow-card p-4 w-[calc(100vw-24px)] xs:w-64 max-w-[280px]"
      >
        <h3 class="font-semibold text-text-deep mb-3 flex items-center gap-2">
          <span>♿</span>
          {{ t('a11y.title') }}
        </h3>
        
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
                'flex-1 py-3 rounded-lg text-sm font-medium transition-colors touch-manipulation active:scale-95',
                a11ySettings.textSize === size 
                  ? 'bg-primary text-white' 
                  : 'bg-background text-text-muted'
              ]"
            >
              {{ size === 'normal' ? 'A' : size === 'large' ? 'A+' : 'A++' }}
            </button>
          </div>
        </div>

        <!-- High Contrast -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation">
          <span class="text-sm">{{ t('a11y.highContrast') }}</span>
          <button
            @click="a11ySettings.highContrast = !a11ySettings.highContrast"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative',
              a11ySettings.highContrast ? 'bg-primary' : 'bg-border'
            ]"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.highContrast ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>

        <!-- Reduced Motion -->
        <label class="flex items-center justify-between py-3 cursor-pointer touch-manipulation">
          <span class="text-sm">{{ t('a11y.reducedMotion') }}</span>
          <button
            @click="a11ySettings.reducedMotion = !a11ySettings.reducedMotion"
            :class="[
              'w-14 h-8 rounded-full transition-colors relative',
              a11ySettings.reducedMotion ? 'bg-primary' : 'bg-border'
            ]"
          >
            <span 
              :class="[
                'absolute top-1 w-6 h-6 bg-white rounded-full shadow transition-all',
                a11ySettings.reducedMotion ? 'end-1' : 'start-1'
              ]"
            ></span>
          </button>
        </label>
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
          nomi
        </h1>
        <p class="text-lg xs:text-xl text-text-deep font-medium mb-1">Find Your Connection</p>
        
        <!-- Warm tagline with hand-drawn feel -->
        <p class="text-sm xs:text-base text-text-muted mb-12 xs:mb-14 flex items-center justify-center gap-2">
          <span class="inline-block animate-wiggle" style="animation-delay: 0s;">✿</span>
          <span class="italic">Because everyone deserves love</span>
          <span class="inline-block animate-wiggle" style="animation-delay: 0.2s;">✿</span>
        </p>

        <!-- Organic Stats Cards -->
        <div class="mb-10 xs:mb-12 grid grid-cols-3 gap-3 animate-slide-up stagger-1">
          <div class="bg-surface-warm p-4 rounded-[20px] shadow-soft">
            <p class="text-2xl xs:text-3xl font-display font-bold text-primary">12K+</p>
            <p class="text-[11px] xs:text-xs text-text-muted mt-1">Members</p>
          </div>
          <div class="bg-surface-warm p-4 rounded-[20px] shadow-soft">
            <p class="text-2xl xs:text-3xl font-display font-bold text-secondary">3.2K</p>
            <p class="text-[11px] xs:text-xs text-text-muted mt-1">Matches</p>
          </div>
          <div class="bg-surface-warm p-4 rounded-[20px] shadow-soft">
            <p class="text-2xl xs:text-3xl font-display font-bold text-accent-dark">89%</p>
            <p class="text-[11px] xs:text-xs text-text-muted mt-1">Happy</p>
          </div>
        </div>
        
        <!-- Login prompt -->
        <p class="text-sm xs:text-base text-text-muted mb-6 animate-slide-up stagger-2 font-medium">
          Ready to find your person?
        </p>

        <!-- Error Message -->
        <div 
          v-if="loginError" 
          class="mb-4 p-4 bg-red-50 border border-red-200 rounded-[16px] text-red-600 text-sm animate-slide-up"
        >
          {{ loginError }}
        </div>

        <!-- Social Login Buttons with unique styling -->
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
            <span>{{ authLoading ? 'Connecting...' : 'Continue with Facebook' }}</span>
          </button>

          <!-- Instagram -->
          <button
            @click="handleSocialLogin('instagram')"
            :disabled="authLoading"
            class="group relative flex items-center justify-center gap-3 w-full py-5 bg-gradient-to-r from-[#F77737] via-[#E1306C] to-[#833AB4] text-white rounded-[20px] font-semibold shadow-soft overflow-hidden touch-manipulation active:scale-[0.98] transition-all duration-300 text-base xs:text-lg disabled:opacity-60 disabled:cursor-not-allowed"
            aria-label="Continue with Instagram"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
            </svg>
            <span>Continue with Instagram</span>
          </button>
        </div>

        <!-- Dev mode indicator -->
        <div v-if="!hasFacebookConfig" class="mt-4 text-center">
          <span class="inline-flex items-center gap-1 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
            <span>⚠️</span> Dev Mode (Mock Login)
          </span>
        </div>

        <!-- Organic divider -->
        <div class="my-8 flex items-center gap-4 animate-slide-up stagger-4">
          <div class="flex-1 h-[2px] bg-gradient-to-r from-transparent via-border to-transparent"></div>
          <span class="text-text-light text-xs font-medium">100% Inclusive</span>
          <div class="flex-1 h-[2px] bg-gradient-to-r from-transparent via-border to-transparent"></div>
        </div>

        <!-- Terms with warm styling -->
        <p class="text-xs xs:text-sm text-text-muted animate-slide-up stagger-5 leading-relaxed">
          By continuing, you agree to our 
          <a href="#" class="text-primary font-medium hover:underline">Terms</a> 
          and 
          <a href="#" class="text-primary font-medium hover:underline">Privacy Policy</a>
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
                  ? 'bg-gradient-to-r from-primary via-coral to-accent text-white shadow-button' 
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
          <div class="grid grid-cols-2 gap-3 mb-8">
            <button
              v-for="(tag, index) in disabilityTags"
              :key="tag.id"
              @click="toggleTag(tag.id)"
              :class="[
                'group relative rounded-[18px] transition-all duration-300 animate-scale-in touch-manipulation active:scale-[0.97] overflow-hidden',
                selectedTags.includes(tag.id) 
                  ? 'shadow-card' 
                  : 'shadow-soft hover:shadow-card',
                `stagger-${(index % 8) + 1}`
              ]"
              :aria-pressed="selectedTags.includes(tag.id)"
            >
              <!-- Gradient background when selected -->
              <div 
                :class="[
                  'absolute inset-0 transition-opacity duration-300',
                  selectedTags.includes(tag.id) ? 'opacity-100' : 'opacity-0'
                ]"
                :style="`background: linear-gradient(135deg, ${tag.gradient.includes('pink') ? '#FAE5E0' : tag.gradient.includes('green') ? '#D8EBE2' : tag.gradient.includes('amber') ? '#FEF3C7' : '#E0E7FF'}, #fff)`"
              ></div>
              
              <div 
                :class="[
                  'relative flex items-center gap-3 px-4 py-4 min-h-[60px] transition-all',
                  selectedTags.includes(tag.id) ? '' : 'bg-surface-warm'
                ]"
              >
                <span class="text-xl xs:text-2xl">{{ tag.icon }}</span>
                <span 
                  :class="[
                    'flex-1 text-sm font-semibold leading-tight text-start',
                    selectedTags.includes(tag.id) ? 'text-text-deep' : 'text-text-muted'
                  ]"
                >
                  {{ t(`tags.${tag.id}`) }}
                </span>
                <span 
                  v-if="selectedTags.includes(tag.id)"
                  class="text-primary text-lg animate-bounce-soft"
                >
                  ✓
                </span>
              </div>
            </button>
          </div>

          <!-- Mood Selector with organic style -->
          <div class="mb-6 card p-5 animate-slide-up stagger-6">
            <h3 class="text-sm font-semibold text-text-deep mb-4 flex items-center gap-2">
              <span>🌟</span>
              {{ t('onboarding.moodQuestion') }}
            </h3>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="mood in moodOptions"
                :key="mood.id"
                @click="currentMood = mood.id"
                :class="[
                  'flex flex-col items-center gap-2 py-3 rounded-[16px] transition-all touch-manipulation active:scale-95',
                  currentMood === mood.id 
                    ? 'bg-gradient-to-br from-primary/20 to-coral/20 shadow-soft scale-105' 
                    : 'bg-surface-warm hover:bg-background-alt'
                ]"
              >
                <span class="text-2xl xs:text-3xl">{{ mood.emoji }}</span>
                <span class="text-[10px] xs:text-xs font-medium text-text-muted whitespace-nowrap">{{ t(`moods.${mood.id}`) }}</span>
              </button>
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
          class="w-full bg-gradient-to-r from-primary via-coral to-accent text-white text-base xs:text-lg py-4 xs:py-5 rounded-[20px] font-semibold shadow-button touch-manipulation active:scale-[0.98] transition-all duration-300"
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

          <!-- What are you looking for? -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-2">
            <h3 class="text-sm xs:text-base font-semibold text-text-deep mb-3 flex items-center gap-2">
              <span>💕</span> {{ t('lookingFor.whatSeeking') }}
            </h3>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="rel in relationshipOptions"
                :key="rel.id"
                @click="toggleRelationship(rel.id)"
                :class="[
                  'relative p-[2px] rounded-xl transition-all touch-manipulation active:scale-[0.97]',
                  userProfile.lookingFor.relationshipTypes.includes(rel.id)
                    ? `bg-gradient-to-r ${rel.gradient}`
                    : 'bg-border'
                ]"
              >
                <div 
                  :class="[
                    'flex items-center gap-2 px-3 py-3 rounded-[10px] bg-surface transition-colors',
                    userProfile.lookingFor.relationshipTypes.includes(rel.id) ? 'bg-surface/90' : ''
                  ]"
                >
                  <span class="text-lg">{{ rel.emoji }}</span>
                  <span 
                    :class="[
                      'flex-1 text-sm font-medium text-start',
                      userProfile.lookingFor.relationshipTypes.includes(rel.id) ? 'text-text-deep' : 'text-text-muted'
                    ]"
                  >
                    {{ t(`lookingFor.types.${rel.id}`) }}
                  </span>
                  <span 
                    v-if="userProfile.lookingFor.relationshipTypes.includes(rel.id)"
                    class="text-primary"
                  >✓</span>
                </div>
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
            
            <!-- Distance Slider -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs text-text-muted">{{ t('lookingFor.maxDistance') }}</label>
                <span class="text-sm font-semibold text-primary">{{ userProfile.lookingFor.maxDistance }} {{ t('lookingFor.km') }}</span>
              </div>
              <input 
                v-model.number="userProfile.lookingFor.maxDistance"
                type="range"
                min="5"
                max="200"
                step="5"
                class="w-full h-2 bg-border rounded-full appearance-none cursor-pointer accent-primary"
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
          class="w-full bg-gradient-to-r from-primary to-indigo-600 text-white text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium shadow-button touch-manipulation active:scale-[0.98]"
        >
          {{ t('onboarding.continueBtn') }}
        </button>
      </div>
    </div>

    <!-- Discovery View -->
    <div 
      v-else-if="currentView === 'discovery'" 
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
            <h1 class="text-base xs:text-lg font-semibold text-text-deep">{{ t('discovery.title') }}</h1>
            <p class="text-[10px] xs:text-xs text-text-muted">{{ t('discovery.subtitle') }}</p>
          </div>
          
          <div class="flex items-center gap-2">
            <button
              @click="goToMatches"
              class="btn-icon bg-background shadow-soft touch-manipulation relative"
              :aria-label="t('matches.title')"
            >
              <span class="text-lg">💬</span>
              <span 
                v-if="matches.length > 0"
                class="absolute -top-1 -right-1 w-4 h-4 bg-primary text-white text-[10px] rounded-full flex items-center justify-center font-semibold"
              >
                {{ matches.length > 9 ? '9+' : matches.length }}
              </span>
            </button>
            <button
              @click="goToProfile"
              class="btn-icon bg-background shadow-soft touch-manipulation"
              :aria-label="t('nav.profile')"
            >
              <span class="text-lg">👤</span>
            </button>
          </div>
        </div>
      </header>
      
      <!-- Profile Card -->
      <main class="flex-1 px-3 xs:px-4 py-3 xs:py-6 flex flex-col items-center justify-center overflow-hidden relative">
        <!-- Swipe hint for first-time users -->
        <div class="absolute top-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 text-text-muted text-xs animate-pulse-soft pointer-events-none">
          <span>👈</span>
          <span>Swipe to decide</span>
          <span>👉</span>
        </div>
        
        <div 
          v-if="currentProfile"
          class="card w-full max-w-sm relative swipeable no-context-menu select-none"
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

          <!-- Compatibility Badge -->
          <div 
            class="absolute top-4 end-4 z-10 flex items-center gap-1.5 xs:gap-2 px-2.5 xs:px-3 py-1 xs:py-1.5 bg-surface/90 backdrop-blur-sm rounded-full shadow-soft transition-opacity"
            :class="swipeDirection ? 'opacity-0' : 'opacity-100'"
          >
            <span class="text-base xs:text-lg">💫</span>
            <span class="text-xs xs:text-sm font-semibold text-primary">{{ currentProfile.compatibility }}%</span>
          </div>

          <!-- Shared Tags Sparkles -->
          <div 
            v-if="sharedTags.length > 0"
            class="absolute top-4 start-4 z-10 flex items-center gap-1 px-2.5 xs:px-3 py-1 xs:py-1.5 bg-gradient-to-r from-primary to-accent text-white rounded-full text-[10px] xs:text-xs font-medium shadow-soft transition-opacity"
            :class="swipeDirection ? 'opacity-0' : 'opacity-100'"
          >
            <span>✨</span>
            {{ sharedTags.length }} {{ t('discovery.shared') }}
          </div>

          <!-- Photo -->
          <div class="relative aspect-[4/5] xs:aspect-[4/5] overflow-hidden">
            <img 
              :src="currentProfile.photo" 
              :alt="currentProfile.name"
              class="w-full h-full object-cover"
              loading="lazy"
            />
            <!-- Gradient Overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
            
            <!-- Profile Info -->
            <div class="absolute bottom-0 inset-x-0 p-4 xs:p-5 text-white">
              <!-- Mood Badge -->
              <div class="inline-flex items-center gap-1 xs:gap-1.5 px-2.5 xs:px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-[10px] xs:text-xs mb-2 xs:mb-3">
                <span>{{ moodOptions.find(m => m.id === currentProfile.mood)?.emoji }}</span>
                <span>{{ t(`moods.${currentProfile.mood}`) }}</span>
              </div>

              <h2 class="text-xl xs:text-2xl font-bold mb-1">
                {{ currentProfile.name }}, {{ currentProfile.age }}
              </h2>
              <p class="text-xs xs:text-sm text-white/80 mb-2 xs:mb-3">
                📍 {{ t('discovery.distance', { km: currentProfile.distance }) }}
              </p>
              
              <!-- Tags -->
              <div class="flex flex-wrap gap-1.5 xs:gap-2">
                <span 
                  v-for="tagId in currentProfile.tags" 
                  :key="tagId"
                  :class="[
                    'inline-flex items-center gap-1 xs:gap-1.5 px-2 xs:px-3 py-0.5 xs:py-1 rounded-full text-[10px] xs:text-xs font-medium',
                    sharedTags.includes(tagId) 
                      ? 'bg-primary text-white' 
                      : 'bg-white/20 backdrop-blur-sm'
                  ]"
                >
                  {{ disabilityTags.find(t => t.id === tagId)?.icon }}
                  {{ t(`tags.${tagId}`) }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Bio & Prompt -->
          <div class="p-4 xs:p-5">
            <!-- Profile Prompt -->
            <div class="bg-gradient-to-r from-primary-light to-accent/10 rounded-xl p-3 xs:p-4 mb-3 xs:mb-4 border border-primary/20">
              <p class="text-[10px] xs:text-xs font-semibold text-primary uppercase tracking-wide mb-1">
                {{ t(`profilePrompts.${currentProfile.promptId}`) }}
              </p>
              <p class="text-sm xs:text-base text-text-deep font-medium">
                "{{ getLocalized(currentProfile.promptAnswer) }}"
              </p>
            </div>

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
                v-for="interest in getLocalized(currentProfile.interests, [])"
                :key="interest"
                class="px-2.5 xs:px-3 py-1 xs:py-1.5 bg-gradient-to-r from-primary-light to-primary-light/50 text-primary rounded-full text-xs xs:text-sm font-medium"
              >
                {{ interest }}
              </span>
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
          <p class="text-sm xs:text-base text-text-muted">
            {{ t('discovery.checkBackLater') }}
          </p>
        </div>
      </main>
      
      <!-- Action Buttons -->
      <div 
        v-if="currentProfile"
        class="sticky bottom-0 bg-surface/90 backdrop-blur-lg p-4 xs:p-6 bottom-bar-safe"
      >
        <div class="flex items-center justify-center gap-4 xs:gap-6">
          <!-- Pass Button -->
          <button
            @click="passProfile"
            class="w-14 h-14 xs:w-16 xs:h-16 bg-surface rounded-full shadow-card border-2 border-danger/20 flex items-center justify-center touch-manipulation active:scale-90 active:border-danger"
            :aria-label="t('a11y.passProfile')"
          >
            <svg class="w-6 h-6 xs:w-7 xs:h-7 text-danger" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          
          <!-- Super Like Button -->
          <button
            class="w-12 h-12 xs:w-14 xs:h-14 bg-surface rounded-full shadow-card border-2 border-amber-400/30 flex items-center justify-center touch-manipulation active:scale-90 active:border-amber-400"
            :aria-label="t('a11y.superLike')"
          >
            <span class="text-xl xs:text-2xl">⭐</span>
          </button>
          
          <!-- Connect Button -->
          <button
            @click="connectProfile"
            class="w-16 h-16 xs:w-20 xs:h-20 bg-gradient-to-r from-primary to-accent rounded-full shadow-button flex items-center justify-center touch-manipulation active:scale-90"
            :aria-label="t('a11y.connectProfile')"
          >
            <svg class="w-7 h-7 xs:w-9 xs:h-9 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </button>
        </div>
        
        <!-- Button Labels -->
        <div class="flex items-center justify-center gap-4 xs:gap-6 mt-2 xs:mt-3">
          <span class="w-14 xs:w-16 text-center text-xs xs:text-sm text-text-muted">{{ t('discovery.passBtn') }}</span>
          <span class="w-12 xs:w-14 text-center text-xs xs:text-sm text-amber-500">{{ t('discovery.superBtn') }}</span>
          <span class="w-16 xs:w-20 text-center text-xs xs:text-sm text-primary font-medium">{{ t('discovery.connectBtn') }}</span>
        </div>
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
            class="btn-icon bg-background shadow-soft touch-manipulation"
            :aria-label="t('nav.profile')"
          >
            <span class="text-lg">👤</span>
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
            @click="currentView = 'discovery'"
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
            <!-- Avatar -->
            <div class="relative flex-shrink-0">
              <div class="w-14 h-14 xs:w-16 xs:h-16 rounded-2xl overflow-hidden bg-surface shadow-soft">
                <img 
                  v-if="getMatchProfile(match).picture_url"
                  :src="getMatchProfile(match).picture_url"
                  :alt="getMatchProfile(match).name"
                  class="w-full h-full object-cover"
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
      class="min-h-screen-safe flex flex-col relative z-10 bg-background"
    >
      <!-- Header -->
      <header class="sticky top-0 z-20 bg-surface border-b border-border shadow-soft header-safe">
        <div class="flex items-center gap-2 xs:gap-3 px-3 xs:px-4 py-2 xs:py-3">
          <button
            @click="goBack"
            class="btn-icon bg-background touch-manipulation"
            :aria-label="t('a11y.goBack')"
          >
            <svg class="w-5 h-5 xs:w-6 xs:h-6 text-text-deep flip-rtl" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          
          <!-- Match Info -->
          <div class="flex items-center gap-2 xs:gap-3 flex-1">
            <div class="relative">
              <img 
                :src="mockChat.matchPhoto" 
                :alt="mockChat.matchName"
                class="w-10 xs:w-11 h-10 xs:h-11 rounded-full object-cover ring-2 ring-primary/20"
              />
              <span 
                v-if="mockChat.isOnline"
                class="absolute -bottom-0.5 -end-0.5 w-3 xs:w-3.5 h-3 xs:h-3.5 bg-success rounded-full border-2 border-surface"
              ></span>
            </div>
            <div>
              <h1 class="text-sm xs:text-base font-semibold text-text-deep">
                {{ mockChat.matchName }}
              </h1>
              <p class="text-[10px] xs:text-xs text-success flex items-center gap-1">
                <span class="w-1.5 h-1.5 bg-success rounded-full animate-pulse"></span>
                {{ t('chat.online') }}
              </p>
            </div>
          </div>
          
          <!-- Profile Button -->
          <button
            @click="goToProfile"
            class="btn-icon bg-background touch-manipulation"
            :aria-label="t('nav.profile')"
          >
            <span class="text-lg">👤</span>
          </button>
        </div>
      </header>
      
      <!-- Messages -->
      <main class="flex-1 px-3 xs:px-4 py-3 xs:py-4 overflow-auto momentum-scroll hide-scrollbar">
        <div class="max-w-lg mx-auto space-y-3 xs:space-y-4">
          <!-- Date Separator -->
          <div class="text-center">
            <span class="inline-block px-3 xs:px-4 py-1 xs:py-1.5 bg-surface rounded-full text-[10px] xs:text-xs text-text-muted font-medium shadow-soft">
              {{ t('chat.today') }}
            </span>
          </div>
          
          <!-- Messages -->
          <div 
            v-for="(message, index) in mockChat.messages" 
            :key="message.id"
            class="flex animate-slide-up relative"
            :class="[
              message.sender === 'me' ? 'justify-end' : 'justify-start',
              `stagger-${index + 1}`
            ]"
          >
            <div 
              :class="[
                'max-w-[80%] px-3 xs:px-4 py-2.5 xs:py-3 rounded-2xl relative',
                message.sender === 'me' 
                  ? 'bg-gradient-to-br from-primary to-indigo-600 text-white rounded-ee-md' 
                  : 'bg-surface text-text-deep rounded-es-md shadow-soft',
                message.isIcebreaker ? 'ring-2 ring-accent/50' : ''
              ]"
              @click="message.sender === 'them' && toggleReactionMenu(message.id)"
            >
              <!-- Icebreaker Label -->
              <span 
                v-if="message.isIcebreaker"
                class="absolute -top-2 start-2 px-2 py-0.5 bg-accent text-white text-[9px] xs:text-[10px] font-medium rounded-full"
              >
                {{ t('chat.icebreaker') }}
              </span>

              <p class="text-sm xs:text-base leading-relaxed">{{ getLocalized(message.text) }}</p>
              <div class="flex items-center justify-between gap-2 mt-1">
                <p 
                  :class="[
                    'text-[10px] xs:text-xs',
                    message.sender === 'me' ? 'text-white/70' : 'text-text-muted'
                  ]"
                >
                  {{ message.time }}
                </p>
                
                <!-- Reaction -->
                <span v-if="message.reaction" class="text-sm">{{ message.reaction }}</span>
              </div>

              <!-- Reaction Menu (Mobile tap) -->
              <Transition name="scale">
                <div 
                  v-if="showReactionMenu === message.id && message.sender === 'them'"
                  class="absolute -bottom-10 start-0 z-10"
                >
                  <div class="flex gap-1 bg-surface rounded-full px-2 py-1.5 shadow-card">
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
        </div>
      </main>
      
      <!-- Icebreakers -->
      <Transition name="slide-up">
        <div 
          v-if="showIcebreakers"
          class="bg-surface border-t border-border p-3 xs:p-4"
        >
          <div class="max-w-lg mx-auto">
            <h4 class="text-xs xs:text-sm font-semibold text-text-muted mb-2 xs:mb-3 flex items-center gap-2">
              <span>🧊</span>
              {{ t('chat.icebreakers') }}
            </h4>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="prompt in icebreakers"
                :key="prompt.id"
                @click="sendIcebreaker(prompt)"
                class="px-3 xs:px-4 py-2 bg-gradient-to-r from-primary-light to-accent/10 text-primary rounded-full text-xs xs:text-sm font-medium touch-manipulation active:scale-95"
              >
                {{ prompt.text }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
      
      <!-- Input Area -->
      <div 
        class="sticky bottom-0 bg-surface border-t border-border p-3 xs:p-4 bottom-bar-safe"
        :class="{ 'pb-1': isKeyboardOpen }"
      >
        <div class="max-w-lg mx-auto flex items-end gap-2 xs:gap-3">
          <!-- Icebreaker Toggle -->
          <button
            @click="showIcebreakers = !showIcebreakers"
            :class="[
              'w-10 h-10 xs:w-11 xs:h-11 rounded-full flex items-center justify-center shrink-0 touch-manipulation active:scale-90 transition-colors',
              showIcebreakers ? 'bg-accent text-white' : 'bg-primary-light text-primary'
            ]"
          >
            <span class="text-lg xs:text-xl">🧊</span>
          </button>

          <!-- Voice Note Button -->
          <button
            class="w-10 h-10 xs:w-11 xs:h-11 rounded-full bg-primary-light text-primary flex items-center justify-center shrink-0 touch-manipulation active:scale-90"
            :aria-label="t('a11y.recordVoice')"
          >
            <svg class="w-5 h-5 xs:w-6 xs:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
            </svg>
          </button>
          
          <!-- Text Input -->
          <textarea
            v-model="newMessage"
            :placeholder="t('chat.inputPlaceholder')"
            class="input-field flex-1 text-base min-h-[60px] max-h-[120px] py-4 resize-none leading-relaxed"
            rows="2"
            @keydown.enter.exact.prevent="sendMessage"
            enterkeyhint="send"
          ></textarea>
          
          <!-- Send Button -->
          <button
            @click="sendMessage"
            class="w-10 h-10 xs:w-11 xs:h-11 rounded-full bg-gradient-to-r from-primary to-accent text-white shadow-button flex items-center justify-center shrink-0 touch-manipulation active:scale-90"
            :disabled="!newMessage.trim()"
            :class="{ 'opacity-50': !newMessage.trim() }"
          >
            <svg 
              class="w-5 h-5 xs:w-6 xs:h-6" 
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

    <!-- Profile Edit View -->
    <div 
      v-else-if="currentView === 'profile'" 
      class="min-h-screen-safe flex flex-col relative z-10 bg-background"
    >
      <!-- Header -->
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
          
          <button
            @click="saveProfile"
            class="text-primary font-medium px-2 xs:px-3 py-2 min-h-[48px] touch-manipulation active:opacity-70"
          >
            {{ t('save') }}
          </button>
        </div>
      </header>
      
      <!-- Content -->
      <main class="flex-1 px-3 xs:px-4 py-4 xs:py-6 overflow-auto momentum-scroll hide-scrollbar">
        <div class="max-w-lg mx-auto space-y-4 xs:space-y-6">
          
          <!-- Photo Section -->
          <div class="text-center animate-slide-up">
            <div class="relative inline-block">
              <img 
                :src="userProfile.photo" 
                alt="Profile Photo"
                class="w-24 xs:w-32 h-24 xs:h-32 rounded-full object-cover ring-4 ring-primary/20 mx-auto"
              />
              <button 
                class="absolute bottom-0 end-0 w-9 xs:w-10 h-9 xs:h-10 bg-primary text-white rounded-full flex items-center justify-center shadow-button touch-manipulation active:scale-90"
              >
                <span class="text-base xs:text-lg">📷</span>
              </button>
            </div>
            <p class="text-xs xs:text-sm text-text-muted mt-2">{{ t('profile.photoHint') }}</p>
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
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="promptId in profilePromptOptions"
                  :key="promptId"
                  @click="userProfile.promptId = promptId"
                  :class="[
                    'px-3 xs:px-4 py-2 rounded-full text-xs xs:text-sm font-medium transition-colors touch-manipulation active:scale-95',
                    userProfile.promptId === promptId 
                      ? 'bg-primary text-white' 
                      : 'bg-primary-light text-primary'
                  ]"
                >
                  {{ t(`profilePrompts.${promptId}`).substring(0, 25) }}...
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

          <!-- Identity Tags -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-3">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>🏷️</span>
              {{ t('profile.myTags') }}
            </h3>
            
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="tag in disabilityTags"
                :key="tag.id"
                @click="toggleProfileTag(tag.id)"
                :class="[
                  'flex items-center gap-1.5 xs:gap-2 px-2.5 xs:px-3 py-2 xs:py-2.5 rounded-xl text-xs xs:text-sm transition-all touch-manipulation active:scale-95',
                  userProfile.tags.includes(tag.id) 
                    ? 'bg-primary text-white' 
                    : 'bg-surface border border-border text-text-muted'
                ]"
              >
                <span>{{ tag.icon }}</span>
                <span class="flex-1 text-start truncate">{{ t(`tags.${tag.id}`) }}</span>
                <span v-if="userProfile.tags.includes(tag.id)" class="text-xs">✓</span>
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
                      ? 'bg-primary text-white shadow-soft'
                      : 'bg-surface border border-border text-text-muted hover:border-primary/50'
                  ]"
                >
                  <span class="text-base">{{ gender.emoji }}</span>
                  <span class="text-xs xs:text-sm font-medium">{{ t(`lookingFor.genders.${gender.id}`) }}</span>
                </button>
              </div>
            </div>
            
            <!-- What are you looking for? -->
            <div class="mb-5">
              <p class="text-xs xs:text-sm text-text-muted mb-3">{{ t('lookingFor.whatSeeking') }}</p>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="rel in relationshipOptions"
                  :key="rel.id"
                  @click="toggleRelationship(rel.id)"
                  :class="[
                    'relative p-[2px] rounded-xl transition-all touch-manipulation active:scale-[0.97]',
                    userProfile.lookingFor.relationshipTypes.includes(rel.id)
                      ? `bg-gradient-to-r ${rel.gradient}`
                      : 'bg-border'
                  ]"
                >
                  <div 
                    :class="[
                      'flex items-center gap-2 px-3 py-2.5 rounded-[10px] bg-surface transition-colors',
                      userProfile.lookingFor.relationshipTypes.includes(rel.id) ? 'bg-surface/90' : ''
                    ]"
                  >
                    <span class="text-lg">{{ rel.emoji }}</span>
                    <span 
                      :class="[
                        'flex-1 text-xs xs:text-sm font-medium text-start',
                        userProfile.lookingFor.relationshipTypes.includes(rel.id) ? 'text-text-deep' : 'text-text-muted'
                      ]"
                    >
                      {{ t(`lookingFor.types.${rel.id}`) }}
                    </span>
                    <span 
                      v-if="userProfile.lookingFor.relationshipTypes.includes(rel.id)"
                      class="text-primary text-xs"
                    >✓</span>
                  </div>
                </button>
              </div>
            </div>

            <!-- Age Range -->
            <div class="mb-5">
              <p class="text-xs xs:text-sm text-text-muted mb-3">{{ t('lookingFor.ageRange') }}</p>
              <div class="flex items-center gap-3">
                <div class="flex-1">
                  <label class="block text-[10px] xs:text-xs text-text-muted mb-1">{{ t('lookingFor.minAge') }}</label>
                  <input 
                    v-model.number="userProfile.lookingFor.ageRange.min"
                    type="number"
                    inputmode="numeric"
                    min="18"
                    max="99"
                    class="input-field text-center text-sm"
                  />
                </div>
                <span class="text-text-muted mt-4">–</span>
                <div class="flex-1">
                  <label class="block text-[10px] xs:text-xs text-text-muted mb-1">{{ t('lookingFor.maxAge') }}</label>
                  <input 
                    v-model.number="userProfile.lookingFor.ageRange.max"
                    type="number"
                    inputmode="numeric"
                    min="18"
                    max="99"
                    class="input-field text-center text-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Location -->
            <div class="mb-5">
              <p class="text-xs xs:text-sm text-text-muted mb-3">{{ t('lookingFor.location') }}</p>
              <input 
                v-model="userProfile.lookingFor.location"
                type="text"
                class="input-field"
                :placeholder="t('lookingFor.locationPlaceholder')"
              />
            </div>

            <!-- Distance -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <p class="text-xs xs:text-sm text-text-muted">{{ t('lookingFor.maxDistance') }}</p>
                <span class="text-sm font-semibold text-primary">{{ userProfile.lookingFor.maxDistance }} {{ t('lookingFor.km') }}</span>
              </div>
              <input 
                v-model.number="userProfile.lookingFor.maxDistance"
                type="range"
                min="5"
                max="200"
                step="5"
                class="w-full h-2 bg-border rounded-full appearance-none cursor-pointer accent-primary"
              />
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
                class="inline-flex items-center gap-1.5 xs:gap-2 px-3 xs:px-4 py-1.5 xs:py-2 bg-gradient-to-r from-primary-light to-accent/10 text-primary rounded-full text-xs xs:text-sm font-medium"
              >
                {{ interest }}
                <button 
                  @click="removeInterest(index)"
                  class="text-primary/70 active:text-danger touch-manipulation"
                >
                  ×
                </button>
              </span>
              
              <!-- Add Interest Button -->
              <button
                @click="addInterest"
                class="inline-flex items-center gap-1 px-3 xs:px-4 py-1.5 xs:py-2 border-2 border-dashed border-primary/30 text-primary rounded-full text-xs xs:text-sm font-medium touch-manipulation active:border-primary active:bg-primary-light"
              >
                <span>+</span>
                {{ t('profile.addInterest') }}
              </button>
            </div>
          </div>

          <!-- Language Selector -->
          <div class="card p-4 xs:p-5 animate-slide-up stagger-6">
            <h3 class="text-xs xs:text-sm font-semibold text-text-muted uppercase tracking-wide mb-3 xs:mb-4 flex items-center gap-2">
              <span>🌍</span>
              {{ t('languageSelection.title') }}
            </h3>
            
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="lang in availableLanguages"
                :key="lang.code"
                @click="setLocale(lang.code)"
                :class="[
                  'flex items-center gap-1.5 xs:gap-2 px-3 xs:px-4 py-2.5 xs:py-3 rounded-xl transition-all touch-manipulation active:scale-95',
                  locale === lang.code 
                    ? 'bg-primary text-white' 
                    : 'bg-surface border border-border text-text-deep'
                ]"
              >
                <span class="text-lg xs:text-xl">{{ lang.flag }}</span>
                <span class="text-xs xs:text-sm font-medium">{{ lang.nativeName }}</span>
              </button>
            </div>
          </div>

          <!-- Save Button -->
          <button
            @click="saveProfile"
            class="w-full bg-gradient-to-r from-primary to-indigo-600 text-white text-base xs:text-lg py-3.5 xs:py-4 rounded-xl xs:rounded-2xl font-medium shadow-button touch-manipulation active:scale-[0.98] animate-slide-up stagger-7"
          >
            {{ t('profile.saveChanges') }}
          </button>
          
          <!-- Bottom spacing for safe area -->
          <div class="h-4"></div>
        </div>
      </main>
    </div>

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
              <div class="w-full h-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-3xl xs:text-4xl">
                👤
              </div>
            </div>
            <div class="text-3xl xs:text-4xl animate-heart-beat">💜</div>
            <div class="w-20 xs:w-28 h-20 xs:h-28 rounded-full border-4 border-white overflow-hidden shadow-xl animate-slide-in-right">
              <img 
                :src="matchedProfile?.photo" 
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
              @click="showMatchAnimation = false"
              class="text-white/80 font-medium py-3 touch-manipulation active:opacity-70"
            >
              {{ t('match.keepDiscovering') }}
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
