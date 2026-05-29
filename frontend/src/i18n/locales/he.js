/**
 * Hebrew (he) translations
 */
export default {
  // General
  appName: 'KnowMe',
  tagline: 'מצא את החיבור שלך',
  motto: 'כי כולם ראויים לאהבה',
  back: 'חזור',
  next: 'הבא',
  skip: 'דלג',
  done: 'סיום',
  save: 'שמור',
  saving: 'שומר...',
  logout: 'התנתק',
  cancel: 'ביטול',
  edit: 'ערוך',
  delete: 'מחק',
  confirm: 'אישור',
  
  // Bot indicator
  bot: {
    badge: 'בוט',
    label: 'בוט',
    status: 'בוט',
  },
  
  // Language Selection
  languageSelection: {
    title: 'בחר את השפה שלך',
    subtitle: 'בחר את השפה המועדפת עליך',
  },
  
  // Onboarding
  onboarding: {
    title: 'הפרטים',
    subtitle: 'עזור לנו להבין אותך טוב יותר',
    description: 'בחר את כל מה שמתאים לך. זה עוזר לנו למצוא אנשים שמבינים ומעריכים אותך.',
    selectedCount: '{count} נבחרו',
    continueBtn: 'המשך לגילוי',
    moodQuestion: 'איך את/ה מרגיש היום?',
    functionalTagsTitle: 'תיאור יומיומי',
    functionalTagsHint: 'איך זה בא לידי ביטוי ביום־יום.',
  },

  // Tag categories
  tagCategories: {
    vision: 'ראייה',
    hearing: 'שמיעה',
    mobility: 'ניידות',
    communication: 'תקשורת ודיבור',
    cognitive_emotional: 'קוגניטיבי / רגשי',
  },

  // Tag visibility
  tagVisibility: {
    title: 'חשיפה ופרטיות',
    subtitle: 'בחרו מי יראה כל תגית.',
    public: 'גלוי לכולם',
    matches: 'גלוי למאצ׳ים בלבד',
    specific: 'גלוי לאנשים ספציפיים',
    hidden: 'מוסתר',
    choosePeople: 'בחרו אנשים ספציפיים',
    noMatches: 'עדיין אין מאצ׳ים.',
    selectAria: 'חשיפה עבור {tag}',
    noneSelected: 'בחרו לפחות תגית אחת כדי להגדיר חשיפה.',
  },

  // מטרת הקשר
  intent: {
    title: 'מטרת הקשר',
    subtitle: 'איזה סוג חיבור את/ה מחפש/ת?',
    options: {
      relationship: 'קשר רומנטי',
      friendship: 'חברות',
      unsure: 'עדיין לא בטוח/ה',
    },
  },
  
  // Moods
  moods: {
    lowEnergy: 'אנרגיה נמוכה',
    open: 'פתוח לחיבור',
    chatty: 'מוכן לשיחה',
    adventurous: 'מרגיש נועז',
  },
  
  // Disability Tags (functional codes matching backend seed_data)
  tags: {
    // ראייה
    difficultySeeing: 'מתקשה לראות',
    partialVision: 'רואה באופן חלקי',
    visionAids: 'נעזר/ת בעזרים לראייה',
    lightSensitivity: 'רגישות לאור',
    // שמיעה
    difficultyHearing: 'מתקשה לשמוע',
    partialHearing: 'שומע/ת באופן חלקי',
    hearingAids: 'נעזר/ת בעזרים לשמיעה',
    noisyConversations: 'מתקשה בשיחות עם הרבה אנשים',
    // ניידות
    mobilityDifficulty: 'קושי בהתניידות',
    wheelchairUser: 'מתנייד/ת בכיסא גלגלים',
    shortDistances: 'הולך/ת למרחקים קצרים',
    needsAccessibility: 'זקוק/ה להתאמות פיזיות',
    // תקשורת ודיבור
    speechDifficulty: 'קושי בדיבור',
    alternativeCommunication: 'מתקשר/ת בדרכים חלופיות',
    needsTimeToSpeak: 'צריך/ה זמן להתנסח',
    // קוגניטיבי / רגשי
    processingDifficulty: 'קושי בעיבוד מידע',
    sensoryOverload: 'רגישות לעומס או גירויים',
    slowClearPace: 'זקוק/ה לקצב איטי וברור',
    calmSafeSpace: 'צריך/ה מרחב רגוע ובטוח',
    noiseSensitivity: 'רגישות לרעשים חזקים',
    socialCommunicationDifficulty: 'קושי בתקשורת חברתית',
  },
  
  // Discovery
  discovery: {
    title: 'KnowMe',
    subtitle: '',
    noMoreProfiles: 'ראית את כולם לעת עתה!',
    checkBackLater: 'חזור מאוחר יותר לחיבורים חדשים',
    noMoreExplanation: 'צפית בכל הפרופילים הזמינים לפי ההעדפות שלך. בדוק מאוחר יותר לפרופילים חדשים או התאם את העדפות החיפוש.',
    passBtn: 'לא עכשיו',
    connectBtn: 'להגיד שלום',
    superBtn: 'סופר',
    age: 'בן/בת {age}',
    distance: '{km} ק״מ',
    shared: 'משותף',
    compatibility: 'התאמה',
    swipeHint: 'החלק שמאלה לדלג ← | → החלק ימינה לחיבור',
    accessibleHint: 'החלק, לחץ על הכפתורים, או השתמש במקשי החצים',
    keyboardHint: '→ דלג | התחבר ← | רווח: בטל | Enter: צפה בפרופיל',
    // Progressive disclosure
    learnMore: 'גלה עוד',
    deepDive: 'צלילה לעומק',
    showLess: 'הראה פחות',
    // Match breakdown
    whyMatch: 'למה ההתאמה הזו?',
    sharedTags: 'תגים משותפים',
    nearby: 'קרוב אלייך',
    sharedInterests: 'תחומי עניין משותפים',
    matchDisclaimer: 'ציוני התאמה הם הצעות. חיבור קורה בדרכים לא צפויות! 💫',
    // Shared / in common
    inCommon: '{count} משותפים',
    sharedTagsCount: '{count} תגיות משותפות',
    sharedInterestsCount: '{count} תחומי עניין משותפים',
    thingsInCommon: 'דברים משותפים',
    // Undo
    skipping: 'מדלג על',
    connecting: 'מתחבר עם',
    undo: 'בטל',
    // Review again
    reviewAgain: 'עברו על הפרופילים שוב',
    reviewAgainHint: 'ראו פרופילים שדילגתם עליהם',
  },
  
  // Matches
  matches: {
    title: 'ההתאמות שלי',
    subtitle: 'החיבורים שלך',
    noMatches: 'אין התאמות עדיין',
    noMatchesDescription: 'המשיכו לגלול כדי למצוא את החיבורים שלכם!',
    matchedOn: 'התאמה',
    startChat: 'התחל צ׳אט',
    viewProfile: 'צפה בפרופיל',
  },
  
  // Chat
  chat: {
    title: 'חיבור',
    subtitle: 'השיחות שלך',
    inputPlaceholder: 'כתוב הודעה...',
    send: 'שלח',
    voiceNote: 'הקלט הודעה קולית',
    online: 'מחובר',
    offline: 'לא מחובר',
    typing: 'מקליד...',
    conversations: 'שיחות',
    showSidebar: 'הצג שיחות',
    hideSidebar: 'הסתר שיחות',
    smartSuggestions: 'הצעות תשובה',
    loadingSuggestions: 'טוען הצעות...',
    refreshSuggestions: 'רענון',
    showSuggestions: 'הצג',
    hideSuggestions: 'הסתר',
    noSuggestions: 'אין הצעות כרגע.',
    summaryAction: 'סיכום',
    summaryTitle: 'סיכום שיחה',
    summaryLoading: 'יוצר סיכום...',
    summaryUnavailable: 'הסיכום לא זמין כרגע.',
    today: 'היום',
    yesterday: 'אתמול',
    icebreaker: 'שובר קרח',
    icebreakers: 'רעיונות לשיחה',
    needHelp: 'צריך עזרה להתחיל?',
    notSureWhatToSay: 'לא בטוח/ה מה לכתוב?',
    starterHint: 'נסו אחד מאלה לשבור את הקרח:',
    disconnect: 'נתק',
    disconnectTitle: 'להתנתק מההתאמה?',
    disconnectMessage: 'פעולה זו תסיר את האדם הזה מההתאמות שלך ותמחק את כל ההודעות. לא ניתן לבטל פעולה זו.',
    disconnectConfirm: 'נתק',
    // Voice recording
    recording: 'מקליט...',
    cancelRecording: 'בטל הקלטה',
    stopRecording: 'עצור ושלח',
    playVoice: 'נגן הודעה קולית',
    pauseVoice: 'השהה הודעה קולית',
    voiceMessage: 'הודעה קולית',
    // Speech-to-text transcript
    showTranscript: 'הצג טקסט',
    hideTranscript: 'הסתר טקסט',
    liveTranscript: 'תמלול חי',
    sendImage: 'שלח תמונה',
    imageMessage: 'תמונה',
  },

  // Shortcuts
  shortcuts: {
    title: 'קיצורים',
    helper: 'הקישו על קיצור שמור כדי להוסיף אותו להודעה.',
    savedTitle: 'הקיצורים שלי',
    createTitle: 'יצירת קיצור',
    suggestedTitle: 'תגובות לדוגמה',
    empty: 'עדיין אין קיצורים שמורים.',
    add: 'שמירה',
    remove: 'הסרה',
    saved: 'נשמר',
    useDraft: 'השתמשו בטיוטה',
    toggle: 'פתיחת קיצורים',
    loadError: 'לא ניתן לטעון קיצורים.',
    saveError: 'לא ניתן לשמור קיצור.',
    removeError: 'לא ניתן להסיר קיצור.',
    validationError: 'נדרש כותרת והודעה.',
    titleLabel: 'כותרת',
    titlePlaceholder: 'לדוגמה: מספר טלפון',
    contentLabel: 'הודעה',
    contentPlaceholder: 'כתבו את ההודעה להוספה...',
    untitled: 'ללא כותרת',
    ariaSave: 'שמירת קיצור: {label}',
    ariaRemove: 'הסרת קיצור: {label}',
    ariaUse: 'שימוש בקיצור: {label}',
    labels: {
      phoneNumber: 'מספר טלפון',
      funnySentence: 'משפט מצחיק',
      weeklyPlans: 'תוכניות השבוע',
    },
    responses: {
      phoneNumber: 'הנה מספר הטלפון שלי: ',
      funnySentence: 'מחשבה מצחיקה קצרה: ניסיתי להיות בן/בת בוקר והקפה שלי הגיש תלונה.',
      weeklyPlans: 'התוכניות שלי השבוע: ',
    },
  },
  
  // Icebreaker prompts
  icebreakerPrompts: {
    comfortShow: 'מה הסדרה שמנחמת אותך?',
    idealDay: 'תאר את היום הרגוע האידיאלי שלך',
    proudOf: 'על מה את/ה גאה?',
  },
  
  // Profile Prompts
  profilePrompts: {
    laughMost: 'מה שגורם לי לצחוק הכי הרבה זה...',
    perfectSunday: 'יום ראשון מושלם נראה כמו...',
    convinced: 'אני משוכנע/ת ש...',
  },
  
  // Ask Me About It - Celebration prompts
  askMeAboutIt: {
    title: 'תשאלו אותי על זה',
    subtitle: 'חגגו את מה שהופך אתכם למיוחדים',
    prompts: {
      coolestThing: "הדבר הכי מגניב במצב שלי זה...",
      superpower: "כוח העל שלי מלהיות שונה הוא...",
      wishPeopleKnew: "מה שהייתי רוצה שאנשים ידעו זה...",
      proudOf: "משהו שאני גאה שהתגברתי עליו זה...",
      dontLetStop: "אני לא נותן/ת לשום דבר לעצור אותי מ...",
      loveAboutCommunity: "מה שאני אוהב/ת בקהילת המוגבלות זה...",
    },
  },
  
  // זמינות
  timePreferences: {
    title: 'זמינות',
    subtitle: 'מתי את/ה בדרך כלל פנוי/ה?',
    preferredTimes: 'הזמנים הטובים בשבילי',
    times: {
      morning: 'בוקר',
      afternoon: 'צהריים',
      evening: 'ערב',
      night: 'לילה',
      flexible: 'גמיש',
    },
    responsePace: 'קצב התגובה שלי',
    responsePaceOptions: {
      quick: 'תוך שעה',
      moderate: 'תוך 2-4 שעות',
      slow: 'תוך 1-2 ימים',
      variable: 'משתנה לפי האנרגיה שלי',
    },
    notes: 'הערות נוספות',
    notesPlaceholder: 'למשל: אני ציפור לילה, ימי שישי הכי טובים בשבילי...',
  },
  
  // Profile
  profile: {
    title: 'הפרופיל שלי',
    about: 'עליי',
    interests: 'תחומי עניין',
    editProfile: 'עריכת פרופיל',
    photos: 'תמונות',
    basicInfo: 'מידע בסיסי',
    name: 'שם',
    age: 'גיל',
    location: 'מיקום',
    bio: 'אודות',
    bioPlaceholder: 'ספר על עצמך...',
    myTags: 'התגים שלי',
    myInterests: 'תחומי העניין שלי',
    addInterest: 'הוסף תחום עניין',
    addCustomInterest: 'הוסיפו משלכם',
    customInterestPlaceholder: 'הקלידו תחום עניין...',
    customInterestHint: 'עד 5 תחומי עניין מותאמים אישית, עד 20 תווים כל אחד',
    prompt: 'קצת עליי',
    promptSubtitle: 'זה הדבר הראשון שאנשים רואים בפרופיל שלך',
    promptEncouragement: 'אין תשובה נכונה או לא נכונה — פשוט היו עצמכם.',
    promptPlaceholder: 'שתפו קצת על עצמכם...',
    promptCharCount: '{count}/300',
    saveChanges: 'שמור שינויים',
    photoHint: 'לחץ לניהול',
    photoInstructions: 'העלה עד 6 תמונות. מומלץ: 800x800 פיקסלים, פורמט JPG/PNG. לחץ לסידור או מחיקה.',
    setAsPrimary: 'הגדר כתמונה ראשית',
    main: 'ראשית',
    addPhoto: 'הוסף תמונה',
    uploadingPhoto: 'מעלה...',
    maxPhotos: 'מותר עד 6 תמונות',
    cleanup: 'נקה את ההתאמות והצ\'אטים שלי',
    cleanupConfirm: 'פעולה זו תמחק את כל ההתאמות, ההודעות והסוויפים שלך. האם אתה בטוח?',
    cleanupSuccess: 'כל ההתאמות והצ\'אטים נוקו בהצלחה!',
    cleanupError: 'ניקוי נכשל. נסה שוב.',
    noPhoto: 'אין תמונה',
    unknownUser: 'משתמש',
  },
  
  // העדפות חיפוש
  lookingFor: {
    title: 'העדפות חיפוש',
    step: 'שלב 2 מתוך 2',
    subtitle: 'מי תופס את העין שלך?',
    description: 'ספרו לנו על ההעדפות שלכם ונמצא עבורכם את ההתאמות הנכונות.',
    interestedIn: 'מגדר',
    ageRange: 'טווח גילאים',
    minAge: 'מינימום',
    maxAge: 'מקסימום',
    ageRangeError: 'גיל מינימום חייב להיות קטן או שווה לגיל מקסימום',
    location: 'מיקום',
    yourLocation: 'העיר או האזור שלך',
    locationPlaceholder: 'לדוגמה: תל אביב, ירושלים...',
    locationHint: 'בחר עיר מוכרת לחישוב מרחק מדויק',
    maxDistance: 'מרחק מקסימלי',
    maxDistanceUpTo: 'עד {km} ק״מ',
    distanceRange: 'טווח: 5-200 ק״מ',
    km: 'ק״מ',
    genders: {
      male: 'גברים',
      female: 'נשים',
      everyone: 'כולם',
    },
  },
  
  // Match
  match: {
    title: 'זה מאץ׳!',
    subtitle: 'את/ה ו{name} אהבתם אחד את השני!',
    sendMessage: 'שלח הודעה',
    keepDiscovering: 'המשך לגלות',
  },
  
  // Report
  report: {
    button: 'דיווח',
    confirmTitle: 'לדווח על המשתמש/ת?',
    confirmMessage: 'פעולה זו תחסום את האדם הזה ותסיר אותו מההתאמות שלך. לא יוכלו ליצור איתך קשר שוב.',
    confirmAction: 'דווח וחסום',
    success: 'המשתמש דווח ונחסם.',
  },

  // Feedback
  feedback: {
    button: 'השאירו משוב',
    title: 'שתפו את המשוב שלכם',
    subtitle: 'עזרו לנו לשפר את KnowMe',
    placeholder: 'ספרו לנו מה אתם חושבים...',
    send: 'שלח משוב',
    thanks: 'תודה על המשוב!',
    emailSubject: 'משוב על אפליקציית KnowMe',
  },

  // Navigation
  nav: {
    discover: 'גלה',
    matches: 'התאמות',
    chat: 'צ׳אט',
    profile: 'פרופיל',
  },
  
  // Accessibility
  a11y: {
    title: 'נגישות',
    switchLanguage: 'החלף שפה',
    goBack: 'חזור אחורה',
    toggleTag: 'הפעל/כבה תגית {tag}',
    passProfile: 'דלג על פרופיל זה',
    connectProfile: 'התחבר עם האדם הזה',
    superLike: 'סופר לייק',
    sendMessage: 'שלח הודעה',
    recordVoice: 'הקלט הודעה קולית',
    textSize: 'גודל טקסט',
    highContrast: 'ניגודיות גבוהה',
    highContrastDesc: 'הגבר ניגודיות צבעים',
    darkMode: 'מצב כהה',
    darkModeDesc: 'השתמש בפלטת צבעים כהה',
    reducedMotion: 'הפחתת תנועה',
    reducedMotionDesc: 'בטל אנימציות',
    screenReaderMode: 'מצב קורא מסך',
    screenReaderModeDesc: 'מותאם לקוראי מסך',
    showEmojis: 'הצג אמוג\'י',
    showEmojisDesc: 'הצג אייקוני אמוג\'י',
    photoOf: 'תמונה {current} מתוך {total}',
    undoAction: 'בטל פעולה אחרונה',
    viewProfile: 'צפה בפרופיל מלא',
    distanceSlider: 'מחוון מרחק. נוכחי: {km} קילומטרים',
    increaseDistance: 'הגדל מרחק',
    decreaseDistance: 'הקטן מרחק',
    saveChanges: 'שמור שינויים',
    unsavedChanges: 'יש לך שינויים שלא נשמרו',
    keyboardShortcuts: 'קיצורי מקלדת',
    arrowKeysHint: 'דלג / התחבר לפרופילים',
    spaceHint: 'בטל פעולה אחרונה',
    saveHint: 'שמור שינויים בפרופיל',
    enterHint: 'צפה בפרופיל מלא',
  },
  
  // Stats
  stats: {
    members: 'משתמשים',
    connections: 'חיבורים',
    happy: 'מרוצים',
  },
  
  // Auth
  auth: {
    orContinueWith: 'או המשך עם',
    loginWithFacebook: 'המשך עם פייסבוק',
    loginWithInstagram: 'המשך עם אינסטגרם',
    loginAsGuest: 'נסו כאורח',
    connecting: 'מתחבר...',
    readyToFind: 'מוכנים למצוא את האדם שלכם?',
    inclusive: '100% הכלה',
    termsText: 'בהמשך, את/ה מסכים/ה ל',
    terms: 'תנאי השימוש',
    and: 'ו',
    privacyPolicy: 'מדיניות הפרטיות',
    devMode: 'מצב פיתוח (התחברות מדומה)',
    aboutUs: 'עלינו',
    sessionExpired: 'תוקף ההתחברות פג. אנא התחבר/י שוב.',
  },
  
  // Invite Friends
  inviteFriends: {
    title: 'שלח הזמנה לחברים',
    subtitle: 'שתפו את האהבה!',
    description: 'הזמינו את חברי הפייסבוק שלכם להצטרף ל-KnowMe ולמצוא את החיבורים שלהם.',
    inviteButton: 'שלח הזמנה לחברים',
    loading: 'טוען חברים...',
    noFriends: 'אין חברים להזמנה',
    noFriendsDescription: 'התחברו עם פייסבוק כדי לראות חברים שניתן להזמין.',
    invite: 'הזמן',
    invited: 'הוזמן',
    alreadyOnApp: 'כבר ב-KnowMe',
    sendInvite: 'שלח הזמנה',
    inviteSent: 'ההזמנה נשלחה!',
    inviteError: 'שליחת ההזמנה נכשלה',
    shareMessage: 'היי! אני משתמש/ת ב-KnowMe - אפליקציית היכרויות מכילה. בואו תצטרפו!',
    close: 'סגור',
    loginRequired: 'נא להתחבר עם פייסבוק כדי להזמין חברים',
    stats: {
      sent: 'הזמנות נשלחו',
      accepted: 'הצטרפו',
      pending: 'ממתין',
    },
  },

  // Interest categories
  interestCategories: {
    Creative: 'יצירתי',
    Active: 'פעיל',
    Entertainment: 'בידור',
    'Food & Drink': 'אוכל ושתייה',
    'Tech & Learning': 'טכנולוגיה ולמידה',
    Lifestyle: 'אורח חיים',
    Social: 'חברתי וקהילתי',
    Other: 'אחר',
  },

  // Interest Tags (translated)
  interests: {
    // יצירתי
    Photography: 'צילום',
    Art: 'אמנות',
    Music: 'מוזיקה',
    Writing: 'כתיבה',
    Painting: 'ציור',
    Design: 'עיצוב',
    'Digital Art': 'אמנות דיגיטלית',
    'Graphic Design': 'עיצוב גרפי',
    Guitar: 'גיטרה',
    Drumming: 'תופים',
    'Music Production': 'הפקת מוזיקה',
    Poetry: 'שירה',
    Comics: 'קומיקס',
    // פעיל
    Yoga: 'יוגה',
    Hiking: 'טיולים',
    Swimming: 'שחייה',
    Sports: 'ספורט',
    Dancing: 'ריקוד',
    Running: 'ריצה',
    Fitness: 'כושר',
    Basketball: 'כדורסל',
    'Scuba Diving': 'צלילה',
    Beach: 'חוף ים',
    Surfing: 'גלישה',
    // בידור
    Gaming: 'משחקים',
    Movies: 'סרטים',
    Reading: 'קריאה',
    'Sci-Fi': 'מדע בדיוני',
    Podcasts: 'פודקאסטים',
    'Board Games': 'משחקי קופסה',
    Comedy: 'קומדיה',
    'Stand-up Comedy': 'סטנדאפ',
    Anime: 'אנימה',
    // אוכל ושתייה
    Cooking: 'בישול',
    Baking: 'אפייה',
    Coffee: 'קפה',
    Wine: 'יין',
    Nutrition: 'תזונה',
    // טכנולוגיה ולמידה
    Technology: 'טכנולוגיה',
    Coding: 'תכנות',
    Science: 'מדע',
    Languages: 'שפות',
    Engineering: 'הנדסה',
    Psychology: 'פסיכולוגיה',
    Philosophy: 'פילוסופיה',
    History: 'היסטוריה',
    Astronomy: 'אסטרונומיה',
    // אורח חיים
    Travel: 'טיולים בעולם',
    Nature: 'טבע',
    Animals: 'בעלי חיים',
    Fashion: 'אופנה',
    Meditation: 'מדיטציה',
    Wellness: 'בריאות ורווחה',
    Dogs: 'כלבים',
    Cats: 'חתולים',
    Blogging: 'בלוגים',
    // חברתי וקהילתי
    'Social Justice': 'צדק חברתי',
    Volunteering: 'התנדבות',
    Teaching: 'הוראה',
    Healthcare: 'בריאות',
    Museums: 'מוזיאונים',
    Architecture: 'אדריכלות',
  },
}
