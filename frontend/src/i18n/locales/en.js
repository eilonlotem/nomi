/**
 * English (en) translations
 */
export default {
  // General
  appName: 'KnowMe',
  tagline: 'Find Your Connection',
  motto: 'Because everyone deserves love',
  back: 'Back',
  next: 'Next',
  skip: 'Skip',
  done: 'Done',
  save: 'Save',
  saving: 'Saving...',
  logout: 'Log Out',
  cancel: 'Cancel',
  edit: 'Edit',
  delete: 'Delete',
  confirm: 'Confirm',
  
  // Bot indicator
  bot: {
    badge: 'Bot',
    label: 'Bot',
    status: 'Bot',
  },
  
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
    functionalTagsTitle: 'Everyday experience',
    functionalTagsHint: 'Describe how it shows up day to day.',
  },

  // Tag categories
  tagCategories: {
    vision: 'Vision',
    hearing: 'Hearing',
    mobility: 'Mobility',
    communication: 'Communication',
    cognitive_emotional: 'Cognitive / emotional',
  },

  // Tag visibility
  tagVisibility: {
    title: 'Visibility & privacy',
    subtitle: 'Choose who can see each tag.',
    public: 'Visible to everyone',
    matches: 'Matches only',
    specific: 'Specific people',
    hidden: 'Hidden',
    choosePeople: 'Choose specific people',
    noMatches: 'No matches yet.',
    selectAria: 'Visibility for {tag}',
    noneSelected: 'Select at least one tag to set visibility.',
  },

  // Relationship Goal
  intent: {
    title: 'Relationship Goal',
    subtitle: 'What type of connection are you looking for?',
    options: {
      relationship: 'A romantic relationship',
      friendship: 'Friendship',
      unsure: 'Not sure yet',
    },
  },
  
  // Moods
  moods: {
    lowEnergy: 'Low Energy',
    open: 'Open to Connect',
    chatty: 'Ready to Chat',
    adventurous: 'Feeling Bold',
  },
  
  // Disability Tags (functional codes matching backend seed_data)
  tags: {
    // Vision
    difficultySeeing: 'Difficulty seeing',
    partialVision: 'Partial vision',
    visionAids: 'Use vision aids',
    lightSensitivity: 'Light sensitivity',
    // Hearing
    difficultyHearing: 'Difficulty hearing',
    partialHearing: 'Partial hearing',
    hearingAids: 'Use hearing aids',
    noisyConversations: 'Hard to follow group conversations',
    // Mobility
    mobilityDifficulty: 'Mobility challenges',
    wheelchairUser: 'Wheelchair user',
    shortDistances: 'Can walk short distances',
    needsAccessibility: 'Need physical accommodations',
    // Communication
    speechDifficulty: 'Speech difficulties',
    alternativeCommunication: 'Use alternative communication',
    needsTimeToSpeak: 'Need extra time to express myself',
    // Cognitive / Emotional
    processingDifficulty: 'Info processing challenges',
    sensoryOverload: 'Sensitive to overload/stimuli',
    slowClearPace: 'Need a slow, clear pace',
    calmSafeSpace: 'Need a calm, safe space',
    noiseSensitivity: 'Sensitivity to loud noises',
    socialCommunicationDifficulty: 'Difficulty with social communication',
  },
  
  // Discovery
  discovery: {
    title: 'KnowMe',
    subtitle: '',
    noMoreProfiles: "You've seen everyone for now!",
    checkBackLater: 'Check back later for new connections',
    noMoreExplanation: "You've viewed all available matches for your filters. Check back later for new profiles or adjust your preferences.",
    passBtn: 'Not now',
    connectBtn: 'Say hi',
    superBtn: 'Super',
    age: '{age} years old',
    distance: '{km} km away',
    shared: 'shared',
    compatibility: 'Match',
    swipeHint: '← Swipe Left to Pass | Swipe Right to Like →',
    accessibleHint: 'Swipe, tap buttons, or use arrow keys',
    keyboardHint: '← Pass | Like → | Space: Undo | Enter: View Profile',
    // Progressive disclosure
    learnMore: 'Learn more',
    deepDive: 'Deep dive',
    showLess: 'Show less',
    // Match breakdown
    whyMatch: 'Why this match?',
    sharedTags: 'shared tags',
    nearby: 'Nearby',
    sharedInterests: 'Shared interests',
    matchDisclaimer: 'Match scores are suggestions. Connection happens in unexpected ways! 💫',
    // Shared / in common
    inCommon: '{count} in common',
    sharedTagsCount: '{count} shared tags',
    sharedInterestsCount: '{count} shared interests',
    thingsInCommon: 'Things in common',
    // Undo
    skipping: 'Skipping',
    connecting: 'Connecting with',
    undo: 'Undo',
    // Review again
    reviewAgain: 'Review profiles again',
    reviewAgainHint: 'See profiles you previously passed on',
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
    conversations: 'Conversations',
    showSidebar: 'Show conversations',
    hideSidebar: 'Hide conversations',
    smartSuggestions: 'Suggested replies',
    loadingSuggestions: 'Loading suggestions...',
    refreshSuggestions: 'Refresh',
    showSuggestions: 'Show',
    hideSuggestions: 'Hide',
    noSuggestions: 'No suggestions yet.',
    summaryAction: 'Summarize',
    summaryTitle: 'Conversation summary',
    summaryLoading: 'Creating summary...',
    summaryUnavailable: 'Summary is unavailable right now.',
    today: 'Today',
    yesterday: 'Yesterday',
    icebreaker: 'Icebreaker',
    icebreakers: 'Conversation starters',
    needHelp: 'Need help starting?',
    notSureWhatToSay: 'Not sure what to say?',
    starterHint: 'Try one of these to break the ice:',
    disconnect: 'Disconnect',
    disconnectTitle: 'Disconnect from match?',
    disconnectMessage: 'This will remove this person from your matches and delete all chat messages. This action cannot be undone.',
    disconnectConfirm: 'Disconnect',
    // Voice recording
    recording: 'Recording...',
    cancelRecording: 'Cancel recording',
    stopRecording: 'Stop and send',
    playVoice: 'Play voice message',
    pauseVoice: 'Pause voice message',
    voiceMessage: 'Voice message',
    // Speech-to-text transcript
    showTranscript: 'Show text',
    hideTranscript: 'Hide text',
    liveTranscript: 'Live transcript',
    sendImage: 'Send image',
    imageMessage: 'Image',
  },

  // Shortcuts
  shortcuts: {
    title: 'Shortcuts',
    helper: 'Tap a saved shortcut to add it to your message.',
    savedTitle: 'Your shortcuts',
    createTitle: 'Create a shortcut',
    suggestedTitle: 'Suggested responses',
    empty: 'No shortcuts saved yet.',
    add: 'Save',
    remove: 'Remove',
    saved: 'Saved',
    useDraft: 'Use draft',
    toggle: 'Toggle shortcuts',
    loadError: 'Could not load shortcuts.',
    saveError: 'Could not save shortcut.',
    removeError: 'Could not remove shortcut.',
    validationError: 'Title and message are required.',
    titleLabel: 'Title',
    titlePlaceholder: 'e.g. Phone number',
    contentLabel: 'Message',
    contentPlaceholder: 'Type the message to insert...',
    untitled: 'Untitled',
    ariaSave: 'Save shortcut: {label}',
    ariaRemove: 'Remove shortcut: {label}',
    ariaUse: 'Use shortcut: {label}',
    labels: {
      phoneNumber: 'Phone number',
      funnySentence: 'Funny sentence',
      weeklyPlans: 'Weekly plans',
    },
    responses: {
      phoneNumber: 'Here is my phone number: ',
      funnySentence: 'Quick funny thought: I tried to be a morning person, and my coffee filed a complaint.',
      weeklyPlans: 'My plans this week: ',
    },
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
  
  // Availability
  timePreferences: {
    title: 'Availability',
    subtitle: 'When are you typically free?',
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
      quick: 'Within 1 hour',
      moderate: 'Within 2-4 hours',
      slow: 'Within 1-2 days',
      variable: 'Varies by energy level',
    },
    notes: 'Additional notes',
    notesPlaceholder: 'e.g. I\'m a night owl, Fridays work best for me...',
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
    bioPlaceholder: 'Tell about yourself...',
    myTags: 'My Identity Tags',
    myInterests: 'My Interests',
    addInterest: 'Add interest',
    addCustomInterest: 'Add your own',
    customInterestPlaceholder: 'Type an interest...',
    customInterestHint: 'Up to 5 custom interests, max 20 characters each',
    prompt: 'A Bit About Me',
    promptSubtitle: 'This is the first thing people see on your profile',
    promptEncouragement: 'There\'s no right or wrong answer — just be yourself.',
    promptPlaceholder: 'Share a little about yourself...',
    promptCharCount: '{count}/300',
    saveChanges: 'Save Changes',
    photoHint: 'Tap to manage',
    photoInstructions: 'Upload up to 6 photos. Recommended: 800x800px, JPG/PNG formats. Tap to reorder or delete.',
    setAsPrimary: 'Set as primary photo',
    main: 'Main',
    addPhoto: 'Add Photo',
    uploadingPhoto: 'Uploading...',
    maxPhotos: 'Maximum 6 photos allowed',
    cleanup: 'Clear My Matches & Chats',
    cleanupConfirm: 'This will delete all your matches, messages, and swipes. Are you sure?',
    cleanupSuccess: 'All matches and chats cleared successfully!',
    cleanupError: 'Failed to clear data. Please try again.',
    noPhoto: 'No photo',
    unknownUser: 'User',
  },
  
  // Search Preferences
  lookingFor: {
    title: 'Search Preferences',
    step: 'Step 2 of 2',
    subtitle: 'Who catches your eye?',
    description: 'Tell us your preferences and we\'ll find the right matches for you.',
    interestedIn: 'Gender',
    ageRange: 'Age Range',
    minAge: 'Min',
    maxAge: 'Max',
    ageRangeError: 'Minimum age must be less than or equal to maximum age',
    location: 'Location',
    yourLocation: 'Your city or area',
    locationPlaceholder: 'e.g. Tel Aviv, New York...',
    locationHint: 'Select a recognized city for accurate distance matching',
    maxDistance: 'Maximum distance',
    maxDistanceUpTo: 'Up to {km} km',
    distanceRange: 'Range: 5-200 km',
    km: 'km',
    genders: {
      male: 'Men',
      female: 'Women',
      everyone: 'Everyone',
    },
  },
  
  // Match
  match: {
    title: "It's a Match!",
    subtitle: 'You and {name} liked each other!',
    sendMessage: 'Send a Message',
    keepDiscovering: 'Keep Discovering',
  },
  
  // Report
  report: {
    button: 'Report',
    confirmTitle: 'Report this user?',
    confirmMessage: 'This will block this person and remove them from your matches. They will not be able to contact you again.',
    confirmAction: 'Report & Block',
    success: 'User reported and blocked.',
  },

  // Feedback
  feedback: {
    button: 'Leave Feedback',
    title: 'Share Your Feedback',
    subtitle: 'Help us improve KnowMe',
    placeholder: 'Tell us what you think...',
    send: 'Send Feedback',
    thanks: 'Thank you for your feedback!',
    emailSubject: 'KnowMe App Feedback',
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
    title: 'Accessibility Settings',
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
    highContrastDesc: 'Increase color contrast',
    darkMode: 'Dark Mode',
    darkModeDesc: 'Use a darker color palette',
    reducedMotion: 'Reduced Motion',
    reducedMotionDesc: 'Disable animations',
    screenReaderMode: 'Screen Reader Mode',
    screenReaderModeDesc: 'Optimize for screen readers',
    showEmojis: 'Show Emojis',
    showEmojisDesc: 'Display emoji icons',
    photoOf: 'Photo {current} of {total}',
    undoAction: 'Undo last action',
    viewProfile: 'View full profile',
    distanceSlider: 'Distance preference slider. Current: {km} kilometers',
    increaseDistance: 'Increase distance',
    decreaseDistance: 'Decrease distance',
    saveChanges: 'Save changes',
    unsavedChanges: 'You have unsaved changes',
    keyboardShortcuts: 'Keyboard Shortcuts',
    arrowKeysHint: 'Pass / Like profiles',
    spaceHint: 'Undo last action',
    saveHint: 'Save profile changes',
    enterHint: 'View full profile',
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
    loginAsGuest: 'Try as Guest',
    connecting: 'Connecting...',
    readyToFind: 'Ready to find your person?',
    inclusive: '100% Inclusive',
    termsText: 'By continuing, you agree to our',
    terms: 'Terms',
    and: 'and',
    privacyPolicy: 'Privacy Policy',
    devMode: 'Dev Mode (Mock Login)',
    aboutUs: 'About Us',
    sessionExpired: 'Your session has expired. Please log in again.',
  },
  
  // Invite Friends
  inviteFriends: {
    title: 'Send Invite to Friends',
    subtitle: 'Share the love!',
    description: 'Invite your Facebook friends to join KnowMe and find their connections.',
    inviteButton: 'Send Invite to Friends',
    loading: 'Loading friends...',
    noFriends: 'No friends to invite',
    noFriendsDescription: 'Connect with Facebook to see friends you can invite.',
    invite: 'Invite',
    invited: 'Invited',
    alreadyOnApp: 'Already on KnowMe',
    sendInvite: 'Send Invite',
    inviteSent: 'Invite sent!',
    inviteError: 'Failed to send invite',
    shareMessage: "Hey! I'm using KnowMe - an inclusive dating app. Join me!",
    close: 'Close',
    loginRequired: 'Please log in with Facebook to invite friends',
    stats: {
      sent: 'Invites sent',
      accepted: 'Joined',
      pending: 'Pending',
    },
  },

  // Interest categories
  interestCategories: {
    Creative: 'Creative',
    Active: 'Active',
    Entertainment: 'Entertainment',
    'Food & Drink': 'Food & Drink',
    'Tech & Learning': 'Tech & Learning',
    Lifestyle: 'Lifestyle',
    Social: 'Social & Community',
    Other: 'Other',
  },

  // Interest Tags (for translation lookup)
  interests: {
    // Creative
    Photography: 'Photography',
    Art: 'Art',
    Music: 'Music',
    Writing: 'Writing',
    Painting: 'Painting',
    Design: 'Design',
    'Digital Art': 'Digital Art',
    'Graphic Design': 'Graphic Design',
    Guitar: 'Guitar',
    Drumming: 'Drumming',
    'Music Production': 'Music Production',
    Poetry: 'Poetry',
    Comics: 'Comics',
    // Active
    Yoga: 'Yoga',
    Hiking: 'Hiking',
    Swimming: 'Swimming',
    Sports: 'Sports',
    Dancing: 'Dancing',
    Running: 'Running',
    Fitness: 'Fitness',
    Basketball: 'Basketball',
    'Scuba Diving': 'Scuba Diving',
    Beach: 'Beach',
    Surfing: 'Surfing',
    // Entertainment
    Gaming: 'Gaming',
    Movies: 'Movies',
    Reading: 'Reading',
    'Sci-Fi': 'Sci-Fi',
    Podcasts: 'Podcasts',
    'Board Games': 'Board Games',
    Comedy: 'Comedy',
    'Stand-up Comedy': 'Stand-up Comedy',
    Anime: 'Anime',
    // Food & Drink
    Cooking: 'Cooking',
    Baking: 'Baking',
    Coffee: 'Coffee',
    Wine: 'Wine',
    Nutrition: 'Nutrition',
    // Tech & Learning
    Technology: 'Technology',
    Coding: 'Coding',
    Science: 'Science',
    Languages: 'Languages',
    Engineering: 'Engineering',
    Psychology: 'Psychology',
    Philosophy: 'Philosophy',
    History: 'History',
    Astronomy: 'Astronomy',
    // Lifestyle
    Travel: 'Travel',
    Nature: 'Nature',
    Animals: 'Animals',
    Fashion: 'Fashion',
    Meditation: 'Meditation',
    Wellness: 'Wellness',
    Dogs: 'Dogs',
    Cats: 'Cats',
    Blogging: 'Blogging',
    // Social & Community
    'Social Justice': 'Social Justice',
    Volunteering: 'Volunteering',
    Teaching: 'Teaching',
    Healthcare: 'Healthcare',
    Museums: 'Museums',
    Architecture: 'Architecture',
  },
}
