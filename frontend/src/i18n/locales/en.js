/**
 * English (en) translations
 */
export default {
  // General
  appName: 'Nomi',
  tagline: 'Find Your Connection',
  motto: 'Because everyone deserves love',
  back: 'Back',
  next: 'Next',
  skip: 'Skip',
  done: 'Done',
  save: 'Save',
  logout: 'Log Out',
  cancel: 'Cancel',
  edit: 'Edit',
  delete: 'Delete',
  confirm: 'Confirm',
  
  // Language Selection
  languageSelection: {
    title: 'Choose Your Language',
    subtitle: 'Select your preferred language',
  },
  
  // Onboarding
  onboarding: {
    title: 'The Deets',
    subtitle: 'Help us understand you better',
    description: 'Select all that apply to you. This helps us find people who understand and appreciate you.',
    selectedCount: '{count} selected',
    continueBtn: 'Continue to Discovery',
    moodQuestion: 'How are you feeling today?',
  },
  
  // Moods
  moods: {
    lowEnergy: 'Low Energy',
    open: 'Open to Connect',
    chatty: 'Ready to Chat',
    adventurous: 'Feeling Bold',
  },
  
  // Disability Tags
  tags: {
    wheelchairUser: 'Wheelchair User',
    neurodivergent: 'Neurodivergent',
    deafHoh: 'Deaf/HOH',
    blindLowVision: 'Blind/Low Vision',
    chronicIllness: 'Chronic Illness',
    mentalHealth: 'Mental Health',
    mobility: 'Mobility Difference',
    cognitive: 'Cognitive Difference',
    invisible: 'Invisible Disability',
    acquired: 'Acquired Disability',
    caregiver: 'Caregiver/Ally',
    autism: 'Autism',
  },
  
  // Discovery
  discovery: {
    title: 'Nomi Match',
    subtitle: 'People who get you',
    noMoreProfiles: "You've seen everyone for now!",
    checkBackLater: 'Check back later for new connections',
    passBtn: 'Pass',
    connectBtn: 'Connect',
    superBtn: 'Super',
    age: '{age} years old',
    distance: '{km} km away',
    shared: 'shared',
    compatibility: 'Match',
  },
  
  // Matches
  matches: {
    title: 'My Matches',
    subtitle: 'Your connections',
    noMatches: 'No matches yet',
    noMatchesDescription: 'Keep swiping to find your connections!',
    matchedOn: 'Matched',
    startChat: 'Start Chat',
    viewProfile: 'View Profile',
    tapToViewProfile: 'Tap to view profile',
  },
  
  // Chat
  chat: {
    title: 'Connection',
    subtitle: 'Your conversations',
    inputPlaceholder: 'Type a message...',
    send: 'Send',
    voiceNote: 'Record voice note',
    online: 'Online',
    offline: 'Offline',
    typing: 'typing...',
    today: 'Today',
    yesterday: 'Yesterday',
    icebreaker: 'Icebreaker',
    icebreakers: 'Icebreakers',
    disconnect: 'Disconnect',
    disconnectTitle: 'Disconnect from match?',
    disconnectMessage: 'This will remove this person from your matches and delete all chat messages. This action cannot be undone.',
    disconnectConfirm: 'Disconnect',
  },
  
  // Icebreaker prompts
  icebreakerPrompts: {
    comfortShow: "What's your comfort show?",
    idealDay: 'Describe your ideal low-key day',
    proudOf: "What's something you're proud of?",
  },
  
  // Profile Prompts
  profilePrompts: {
    laughMost: 'The thing that makes me laugh most is...',
    perfectSunday: 'My perfect Sunday looks like...',
    convinced: "I'm convinced that...",
  },
  
  // Ask Me About It - Celebration prompts
  askMeAboutIt: {
    title: 'Ask Me About It',
    subtitle: 'Celebrate what makes you, you',
    prompts: {
      coolestThing: "The coolest thing about my condition is...",
      superpower: "My superpower from being different is...",
      wishPeopleKnew: "What I wish people knew is...",
      proudOf: "Something I'm proud of overcoming is...",
      dontLetStop: "I don't let anything stop me from...",
      loveAboutCommunity: "What I love about the disability community is...",
    },
  },
  
  // Time Preferences
  timePreferences: {
    title: 'Time Preferences',
    subtitle: 'Help others know when you\'re available',
    preferredTimes: 'Best times for me',
    times: {
      morning: 'Morning',
      afternoon: 'Afternoon',
      evening: 'Evening',
      night: 'Night',
      flexible: 'Flexible',
    },
    responsePace: 'My response pace',
    responsePaceOptions: {
      quick: 'I respond quickly',
      moderate: 'Within a few hours',
      slow: 'May take a day or more',
      variable: 'Depends on my energy',
    },
    datePace: 'Meeting preferences',
    datePaceOptions: {
      ready: 'Ready to meet soon',
      slow: 'Prefer to chat first',
      virtual: 'Virtual dates preferred',
      flexible: 'Open to whatever feels right',
    },
    notes: 'Additional notes',
    notesPlaceholder: 'e.g. I have PT on Tuesdays, I\'m a night owl...',
  },
  
  // Profile
  profile: {
    title: 'My Profile',
    about: 'About me',
    interests: 'Interests',
    editProfile: 'Edit Profile',
    photos: 'Photos',
    basicInfo: 'Basic Info',
    name: 'Name',
    age: 'Age',
    location: 'Location',
    bio: 'Bio',
    bioPlaceholder: 'Tell others about yourself...',
    myTags: 'My Identity Tags',
    myInterests: 'My Interests',
    addInterest: 'Add interest',
    prompt: 'Profile Prompt',
    promptAnswer: 'Your answer',
    saveChanges: 'Save Changes',
    photoHint: 'Tap photos to manage',
    setAsPrimary: 'Set as primary photo',
    main: 'Main',
    addPhoto: 'Add Photo',
    uploadingPhoto: 'Uploading...',
    maxPhotos: 'Maximum 6 photos allowed',
    cleanup: 'Clear My Matches & Chats',
    cleanupConfirm: 'This will delete all your matches, messages, and swipes. Are you sure?',
    cleanupSuccess: 'All matches and chats cleared successfully!',
    cleanupError: 'Failed to clear data. Please try again.',
  },
  
  // Looking For
  lookingFor: {
    title: 'Looking For',
    step: 'Step 2 of 2',
    subtitle: 'Who catches your eye?',
    description: 'Tell us what you\'re looking for so we can find your perfect matches.',
    interestedIn: 'I\'m interested in...',
    whatSeeking: 'What are you looking for?',
    ageRange: 'Age Range',
    minAge: 'Min',
    maxAge: 'Max',
    location: 'Location',
    yourLocation: 'Your city or area',
    locationPlaceholder: 'e.g. Tel Aviv, New York...',
    maxDistance: 'Maximum distance',
    km: 'km',
    genders: {
      male: 'Men',
      female: 'Women',
      nonbinary: 'Non-binary',
      everyone: 'Everyone',
    },
    types: {
      casual: 'Casual Dating',
      serious: 'Serious Relationship',
      friends: 'Just Friends',
      activity: 'Activity Partners',
    },
  },
  
  // Match
  match: {
    title: "It's a Match!",
    subtitle: 'You and {name} liked each other!',
    sendMessage: 'Send a Message',
    keepDiscovering: 'Keep Discovering',
  },
  
  // Navigation
  nav: {
    discover: 'Discover',
    matches: 'Matches',
    chat: 'Chat',
    profile: 'Profile',
  },
  
  // Accessibility
  a11y: {
    title: 'Accessibility',
    switchLanguage: 'Switch language',
    goBack: 'Go back',
    toggleTag: 'Toggle {tag} tag',
    passProfile: 'Pass on this profile',
    connectProfile: 'Connect with this person',
    superLike: 'Super Like',
    sendMessage: 'Send message',
    recordVoice: 'Record voice message',
    textSize: 'Text Size',
    highContrast: 'High Contrast',
    reducedMotion: 'Reduced Motion',
  },
  
  // Stats
  stats: {
    members: 'Members',
    connections: 'Connections',
    happy: 'Happy',
  },
  
  // Auth
  auth: {
    orContinueWith: 'or continue with',
    loginWithFacebook: 'Continue with Facebook',
    loginWithInstagram: 'Continue with Instagram',
  },
}
