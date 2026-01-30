/**
 * French (fr) translations
 */
export default {
  // General
  appName: 'Nomi',
  tagline: 'Trouvez Votre Connexion',
  motto: "Parce que tout le monde mérite l'amour",
  back: 'Retour',
  next: 'Suivant',
  skip: 'Passer',
  done: 'Terminé',
  save: 'Enregistrer',
  saving: 'Enregistrement...',
  logout: 'Déconnexion',
  cancel: 'Annuler',
  edit: 'Modifier',
  delete: 'Supprimer',
  confirm: 'Confirmer',
  
  // Bot indicator
  bot: {
    badge: 'Bot',
    label: 'Bot',
    status: 'Bot',
  },
  
  // Language Selection
  languageSelection: {
    title: 'Choisissez Votre Langue',
    subtitle: 'Sélectionnez votre langue préférée',
  },
  
  // Onboarding
  onboarding: {
    title: 'Les Détails',
    subtitle: 'Aidez-nous à mieux vous connaître',
    description: "Sélectionnez tout ce qui s'applique. Cela nous aide à trouver des personnes qui vous comprennent et vous apprécient.",
    selectedCount: '{count} sélectionnés',
    continueBtn: 'Continuer vers Découverte',
    moodQuestion: "Comment vous sentez-vous aujourd'hui?",
    functionalTagsTitle: 'Expérience au quotidien',
    functionalTagsHint: 'Décrivez comment cela se manifeste au quotidien.',
  },

  // Tag categories
  tagCategories: {
    vision: 'Vision',
    hearing: 'Audition',
    mobility: 'Mobilité',
    communication: 'Communication',
    cognitive_emotional: 'Cognitif / émotionnel',
  },

  // Tag visibility
  tagVisibility: {
    title: 'Visibilité et confidentialité',
    subtitle: 'Choisissez qui peut voir chaque étiquette.',
    public: 'Visible par tout le monde',
    matches: 'Seulement les matchs',
    specific: 'Personnes spécifiques',
    hidden: 'Masqué',
    choosePeople: 'Choisissez des personnes spécifiques',
    noMatches: 'Pas encore de matchs.',
    selectAria: 'Visibilité pour {tag}',
    noneSelected: 'Sélectionnez au moins une étiquette pour définir la visibilité.',
  },

  // Intent & openness
  intent: {
    title: 'Ce que je recherche',
    subtitle: 'Rendez vos intentions claires dès le départ.',
    options: {
      relationship: 'Je cherche une relation',
      friendship: 'Je cherche une amitié',
      open: 'Ouvert·e à tout',
      slow: 'Je préfère une approche calme',
      unsure: 'Je ne suis pas encore sûr·e',
    },
  },
  openness: {
    title: 'Ouvert·e à',
    subtitle: "Sélectionnez tout ce qui s'applique.",
    options: {
      openToCaregiver: 'Ouvert·e à une relation avec un·e aidant·e',
      openToMobility: "Ouvert·e à quelqu'un avec une mobilité réduite",
      openToMentalHealth: "Ouvert·e à quelqu'un qui vit avec la santé mentale",
      openToAll: 'Ouvert·e à tout le monde',
      notSure: 'Je ne sais pas',
      meetThenDecide: 'Préférer rencontrer puis décider',
      understandsDisability: "Je cherche quelqu'un qui comprend le handicap de l'intérieur",
    },
  },
  
  // Moods
  moods: {
    lowEnergy: 'Faible Énergie',
    open: 'Ouvert à Connecter',
    chatty: 'Prêt à Discuter',
    adventurous: 'Audacieux',
  },
  
  // Disability Tags
  tags: {
    wheelchairUser: 'Utilisateur de Fauteuil',
    neurodivergent: 'Neurodivergent',
    deafHoh: 'Sourd/Malentendant',
    blindLowVision: 'Aveugle/Malvoyant',
    chronicIllness: 'Maladie Chronique',
    mentalHealth: 'Santé Mentale',
    mobility: 'Différence de Mobilité',
    cognitive: 'Différence Cognitive',
    invisible: 'Handicap Invisible',
    acquired: 'Handicap Acquis',
    caregiver: 'Aidant/Allié',
    autism: 'Autisme',
  },
  
  // Discovery
  discovery: {
    title: 'Nomi Match',
    subtitle: 'Des personnes qui vous comprennent',
    noMoreProfiles: 'Vous avez vu tout le monde pour le moment!',
    checkBackLater: 'Revenez plus tard pour de nouvelles connexions',
    noMoreExplanation: 'Vous avez vu tous les profils disponibles selon vos filtres. Revenez plus tard pour de nouveaux profils ou ajustez vos préférences.',
    passBtn: 'Passer',
    connectBtn: 'Connecter',
    superBtn: 'Super',
    age: '{age} ans',
    distance: '{km} km',
    shared: 'partagé',
    compatibility: 'Compatibilité',
    swipeHint: '← Glissez à gauche pour passer | Glissez à droite pour aimer →',
    accessibleHint: 'Glissez, appuyez sur les boutons ou utilisez les flèches',
    keyboardHint: '← Passer | Aimer → | Espace: Annuler | Entrée: Voir Profil',
    // Progressive disclosure
    learnMore: 'En savoir plus',
    deepDive: 'Voir tout',
    showLess: 'Afficher moins',
    // Match breakdown
    whyMatch: 'Pourquoi ce match?',
    sharedTags: 'tags partagés',
    nearby: 'À proximité',
    sharedInterests: 'Intérêts partagés',
    matchDisclaimer: 'Les scores sont des suggestions. La connexion arrive de façons inattendues! 💫',
    // Undo
    skipping: 'Passage de',
    connecting: 'Connexion avec',
    undo: 'Annuler',
  },
  
  // Matches
  matches: {
    title: 'Mes Matchs',
    subtitle: 'Vos connexions',
    noMatches: 'Pas encore de matchs',
    noMatchesDescription: 'Continuez à glisser pour trouver vos connexions!',
    matchedOn: 'Match',
    startChat: 'Commencer le Chat',
    viewProfile: 'Voir le Profil',
  },
  
  // Chat
  chat: {
    title: 'Connexion',
    subtitle: 'Vos conversations',
    inputPlaceholder: 'Écrivez un message...',
    send: 'Envoyer',
    voiceNote: 'Enregistrer note vocale',
    online: 'En ligne',
    offline: 'Hors ligne',
    typing: 'écrit...',
    conversations: 'Conversations',
    showSidebar: 'Afficher les conversations',
    hideSidebar: 'Masquer les conversations',
    smartSuggestions: 'Réponses suggérées',
    loadingSuggestions: 'Chargement des suggestions...',
    refreshSuggestions: 'Actualiser',
    showSuggestions: 'Afficher',
    hideSuggestions: 'Masquer',
    noSuggestions: 'Pas encore de suggestions.',
    summaryAction: 'Résumer',
    summaryTitle: 'Résumé de la conversation',
    summaryLoading: 'Création du résumé...',
    summaryUnavailable: 'Le résumé est indisponible pour le moment.',
    today: "Aujourd'hui",
    yesterday: 'Hier',
    icebreaker: 'Brise-glace',
    icebreakers: 'Brise-glaces',
    disconnect: 'Déconnecter',
    disconnectTitle: 'Se déconnecter du match ?',
    disconnectMessage: 'Cela supprimera cette personne de vos matchs et effacera tous les messages. Cette action est irréversible.',
    disconnectConfirm: 'Déconnecter',
    // Voice recording
    recording: 'Enregistrement...',
    cancelRecording: "Annuler l'enregistrement",
    stopRecording: 'Arrêter et envoyer',
    playVoice: 'Lire le message vocal',
    pauseVoice: 'Mettre en pause le message vocal',
    voiceMessage: 'Message vocal',
  },

  // Shortcuts
  shortcuts: {
    title: 'Raccourcis',
    helper: 'Touchez un raccourci enregistré pour l\'ajouter à votre message.',
    savedTitle: 'Vos raccourcis',
    createTitle: 'Créer un raccourci',
    suggestedTitle: 'Réponses suggérées',
    empty: 'Aucun raccourci enregistré pour l\'instant.',
    add: 'Enregistrer',
    remove: 'Supprimer',
    saved: 'Enregistré',
    useDraft: 'Utiliser le brouillon',
    toggle: 'Ouvrir les raccourcis',
    loadError: 'Impossible de charger les raccourcis.',
    saveError: 'Impossible d\'enregistrer le raccourci.',
    removeError: 'Impossible de supprimer le raccourci.',
    validationError: 'Le titre et le message sont requis.',
    titleLabel: 'Titre',
    titlePlaceholder: 'ex. Numéro de téléphone',
    contentLabel: 'Message',
    contentPlaceholder: 'Saisissez le message à insérer...',
    untitled: 'Sans titre',
    ariaSave: 'Enregistrer le raccourci : {label}',
    ariaRemove: 'Supprimer le raccourci : {label}',
    ariaUse: 'Utiliser le raccourci : {label}',
    labels: {
      phoneNumber: 'Numéro de téléphone',
      funnySentence: 'Phrase drôle',
      weeklyPlans: 'Plans de la semaine',
    },
    responses: {
      phoneNumber: 'Voici mon numéro de téléphone : ',
      funnySentence: 'Petite pensée drôle : j\'ai essayé d\'être du matin et mon café a porté plainte.',
      weeklyPlans: 'Mes plans cette semaine : ',
    },
  },
  
  // Icebreaker prompts
  icebreakerPrompts: {
    comfortShow: 'Quelle est votre série réconfort?',
    idealDay: 'Décrivez votre journée tranquille idéale',
    proudOf: 'De quoi êtes-vous fier/fière?',
  },
  
  // Profile Prompts
  profilePrompts: {
    laughMost: 'Ce qui me fait le plus rire...',
    perfectSunday: 'Mon dimanche parfait ressemble à...',
    convinced: 'Je suis convaincu(e) que...',
    // Additional prompts from Ask Me About It
    coolestThing: 'Ce qu\'il y a de plus cool dans ma condition...',
    superpower: 'Mon super-pouvoir d\'être différent(e) est...',
    wishPeopleKnew: 'Ce que j\'aimerais que les gens sachent...',
    proudOf: 'Quelque chose dont je suis fier/fière...',
    dontLetStop: 'Je ne laisse rien m\'empêcher de...',
    loveAboutCommunity: 'Ce que j\'aime dans la communauté du handicap...',
  },
  
  // Profile
  profile: {
    title: 'Mon Profil',
    about: 'À propos de moi',
    interests: 'Intérêts',
    editProfile: 'Modifier le Profil',
    photos: 'Photos',
    basicInfo: 'Infos de Base',
    name: 'Nom',
    age: 'Âge',
    location: 'Localisation',
    bio: 'Bio',
    bioPlaceholder: 'Parlez de vous...',
    myTags: 'Mes Étiquettes',
    myInterests: 'Mes Intérêts',
    addInterest: 'Ajouter un intérêt',
    prompt: 'Question de Profil',
    promptAnswer: 'Écrivez votre réponse...',
    saveChanges: 'Enregistrer les Modifications',
    photoHint: 'Appuyez pour gérer',
    photoInstructions: 'Téléchargez jusqu\'à 6 photos. Recommandé: 800x800px, formats JPG/PNG. Appuyez pour réorganiser ou supprimer.',
    main: 'Principal',
    cleanup: 'Effacer Mes Matchs et Discussions',
    cleanupConfirm: 'Cela supprimera tous vos matchs, messages et swipes. Êtes-vous sûr?',
    cleanupSuccess: 'Tous les matchs et discussions effacés avec succès!',
    cleanupError: 'Échec de la suppression. Veuillez réessayer.',
    noPhoto: 'Pas de photo',
    unknownUser: 'Utilisateur',
  },
  
  // Looking For
  lookingFor: {
    title: 'Je recherche',
    step: 'Étape 2 sur 2',
    subtitle: 'Qui attire votre attention?',
    description: 'Dites-nous ce que vous recherchez pour trouver vos matchs parfaits.',
    interestedIn: 'Je suis intéressé(e) par...',
    ageRange: 'Tranche d\'âge',
    minAge: 'Min',
    maxAge: 'Max',
    ageRangeError: 'L\'âge minimum doit être inférieur ou égal à l\'âge maximum',
    location: 'Localisation',
    yourLocation: 'Votre ville ou région',
    locationPlaceholder: 'ex. Paris, Lyon...',
    locationHint: 'Sélectionnez une ville reconnue pour une distance précise',
    maxDistance: 'Distance maximale',
    distanceRange: 'Plage: 5-200 km',
    km: 'km',
    genders: {
      male: 'Hommes',
      female: 'Femmes',
      nonbinary: 'Non-binaire',
      everyone: 'Tout le monde',
    },
  },
  
  // Match
  match: {
    title: "C'est un Match!",
    subtitle: 'Vous et {name} vous êtes plu mutuellement!',
    sendMessage: 'Envoyer un Message',
    keepDiscovering: 'Continuer à Découvrir',
  },
  
  // Navigation
  nav: {
    discover: 'Découvrir',
    matches: 'Matchs',
    chat: 'Chat',
    profile: 'Profil',
  },
  
  // Accessibility
  a11y: {
    title: "Paramètres d'accessibilité",
    switchLanguage: 'Changer de langue',
    goBack: 'Retour',
    toggleTag: 'Basculer étiquette {tag}',
    passProfile: 'Passer ce profil',
    connectProfile: 'Connecter avec cette personne',
    superLike: 'Super Like',
    sendMessage: 'Envoyer message',
    recordVoice: 'Enregistrer message vocal',
    textSize: 'Taille du Texte',
    highContrast: 'Contraste Élevé',
    darkMode: 'Mode Sombre',
    darkModeDesc: 'Utiliser une palette de couleurs sombre',
    reducedMotion: 'Mouvement Réduit',
  },
  
  // Stats
  stats: {
    members: 'Membres',
    connections: 'Connexions',
    happy: 'Heureux',
  },
  
  // Auth
  auth: {
    orContinueWith: 'ou continuer avec',
    loginWithFacebook: 'Continuer avec Facebook',
    loginWithInstagram: 'Continuer avec Instagram',
    loginAsGuest: 'Essayer en tant qu\'invité',
    connecting: 'Connexion...',
    readyToFind: 'Prêt à trouver votre personne?',
    inclusive: '100% Inclusif',
    termsText: 'En continuant, vous acceptez nos',
    terms: 'Conditions',
    and: 'et',
    privacyPolicy: 'Politique de Confidentialité',
    devMode: 'Mode Développement',
    aboutUs: 'À Propos',
  },
  
  // Invite Friends
  inviteFriends: {
    title: 'Inviter des Amis',
    subtitle: "Partagez l'amour!",
    description: 'Invitez vos amis Facebook à rejoindre Nomi et trouver leurs connexions.',
    inviteButton: 'Inviter des Amis',
    loading: 'Chargement des amis...',
    noFriends: "Pas d'amis à inviter",
    noFriendsDescription: 'Connectez-vous avec Facebook pour voir les amis que vous pouvez inviter.',
    invite: 'Inviter',
    invited: 'Invité',
    alreadyOnApp: 'Déjà sur Nomi',
    sendInvite: 'Envoyer Invitation',
    inviteSent: 'Invitation envoyée!',
    inviteError: "Échec de l'envoi de l'invitation",
    shareMessage: "Salut! J'utilise Nomi, une app de rencontres inclusive. Rejoignez-moi!",
    close: 'Fermer',
    loginRequired: 'Connectez-vous avec Facebook pour inviter des amis',
    stats: {
      sent: 'Invitations envoyées',
      accepted: 'Rejoint',
      pending: 'En attente',
    },
  },

  // Interest Tags (translated)
  interests: {
    Music: 'Musique',
    Reading: 'Lecture',
    Hiking: 'Randonnée',
    Cooking: 'Cuisine',
    Gaming: 'Jeux vidéo',
    Art: 'Art',
    Sports: 'Sports',
    Travel: 'Voyage',
    Movies: 'Films',
    Photography: 'Photographie',
    Dancing: 'Danse',
    Writing: 'Écriture',
    Yoga: 'Yoga',
    Meditation: 'Méditation',
    Nature: 'Nature',
    Technology: 'Technologie',
    Fashion: 'Mode',
    Food: 'Gastronomie',
    Fitness: 'Fitness',
    Animals: 'Animaux',
  },
}
