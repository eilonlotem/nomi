/**
 * Spanish (es) translations
 */
export default {
  // General
  appName: 'Nomi',
  tagline: 'Encuentra tu Conexión',
  motto: 'Porque todos merecen amor',
  back: 'Atrás',
  next: 'Siguiente',
  skip: 'Omitir',
  done: 'Listo',
  save: 'Guardar',
  logout: 'Cerrar Sesión',
  cancel: 'Cancelar',
  edit: 'Editar',
  delete: 'Eliminar',
  confirm: 'Confirmar',
  
  // Language Selection
  languageSelection: {
    title: 'Elige tu Idioma',
    subtitle: 'Selecciona tu idioma preferido',
  },
  
  // Onboarding
  onboarding: {
    title: 'Los Detalles',
    subtitle: 'Ayúdanos a conocerte mejor',
    description: 'Selecciona todo lo que aplique. Esto nos ayuda a encontrar personas que te entiendan y aprecien.',
    selectedCount: '{count} seleccionados',
    continueBtn: 'Continuar a Descubrir',
    moodQuestion: '¿Cómo te sientes hoy?',
  },
  
  // Moods
  moods: {
    lowEnergy: 'Baja Energía',
    open: 'Abierto a Conectar',
    chatty: 'Listo para Charlar',
    adventurous: 'Sintiéndome Audaz',
  },
  
  // Disability Tags
  tags: {
    wheelchairUser: 'Usuario de Silla de Ruedas',
    neurodivergent: 'Neurodivergente',
    deafHoh: 'Sordo/Hipoacúsico',
    blindLowVision: 'Ciego/Baja Visión',
    chronicIllness: 'Enfermedad Crónica',
    mentalHealth: 'Salud Mental',
    mobility: 'Diferencia de Movilidad',
    cognitive: 'Diferencia Cognitiva',
    invisible: 'Discapacidad Invisible',
    acquired: 'Discapacidad Adquirida',
    caregiver: 'Cuidador/Aliado',
    autism: 'Autismo',
  },
  
  // Discovery
  discovery: {
    title: 'Nomi Match',
    subtitle: 'Personas que te entienden',
    noMoreProfiles: '¡Has visto a todos por ahora!',
    checkBackLater: 'Vuelve más tarde para nuevas conexiones',
    passBtn: 'Pasar',
    connectBtn: 'Conectar',
    superBtn: 'Súper',
    age: '{age} años',
    distance: '{km} km',
    shared: 'compartido',
    compatibility: 'Compatibilidad',
  },
  
  // Matches
  matches: {
    title: 'Mis Matches',
    subtitle: 'Tus conexiones',
    noMatches: 'Sin matches aún',
    noMatchesDescription: '¡Sigue deslizando para encontrar tus conexiones!',
    matchedOn: 'Match',
    startChat: 'Iniciar Chat',
    viewProfile: 'Ver Perfil',
  },
  
  // Chat
  chat: {
    title: 'Conexión',
    subtitle: 'Tus conversaciones',
    inputPlaceholder: 'Escribe un mensaje...',
    send: 'Enviar',
    voiceNote: 'Grabar nota de voz',
    online: 'En línea',
    offline: 'Desconectado',
    typing: 'escribiendo...',
    today: 'Hoy',
    yesterday: 'Ayer',
    icebreaker: 'Rompehielos',
    icebreakers: 'Rompehielos',
    disconnect: 'Desconectar',
    disconnectTitle: '¿Desconectar del match?',
    disconnectMessage: 'Esto eliminará a esta persona de tus matches y borrará todos los mensajes del chat. Esta acción no se puede deshacer.',
    disconnectConfirm: 'Desconectar',
  },
  
  // Icebreaker prompts
  icebreakerPrompts: {
    comfortShow: '¿Cuál es tu serie de confort?',
    idealDay: 'Describe tu día tranquilo ideal',
    proudOf: '¿De qué estás orgulloso/a?',
  },
  
  // Profile Prompts
  profilePrompts: {
    laughMost: 'Lo que más me hace reír es...',
    perfectSunday: 'Mi domingo perfecto se ve así...',
    convinced: 'Estoy convencido/a de que...',
  },
  
  // Profile
  profile: {
    title: 'Mi Perfil',
    about: 'Sobre mí',
    interests: 'Intereses',
    editProfile: 'Editar Perfil',
    photos: 'Fotos',
    basicInfo: 'Info Básica',
    name: 'Nombre',
    age: 'Edad',
    location: 'Ubicación',
    bio: 'Biografía',
    bioPlaceholder: 'Cuéntales a otros sobre ti...',
    myTags: 'Mis Etiquetas',
    myInterests: 'Mis Intereses',
    addInterest: 'Agregar interés',
    prompt: 'Pregunta de Perfil',
    promptAnswer: 'Tu respuesta',
    saveChanges: 'Guardar Cambios',
    photoHint: 'Toca para cambiar foto',
    main: 'Principal',
    cleanup: 'Borrar Mis Matches y Chats',
    cleanupConfirm: 'Esto eliminará todos tus matches, mensajes y swipes. ¿Estás seguro?',
    cleanupSuccess: '¡Todos los matches y chats borrados correctamente!',
    cleanupError: 'Error al borrar datos. Inténtalo de nuevo.',
  },
  
  // Looking For
  lookingFor: {
    title: 'Buscando',
    step: 'Paso 2 de 2',
    subtitle: '¿Quién te llama la atención?',
    description: 'Cuéntanos qué buscas para encontrar tus coincidencias perfectas.',
    interestedIn: 'Me interesan...',
    whatSeeking: '¿Qué buscas?',
    ageRange: 'Rango de edad',
    minAge: 'Mín',
    maxAge: 'Máx',
    location: 'Ubicación',
    yourLocation: 'Tu ciudad o área',
    locationPlaceholder: 'ej. Madrid, Barcelona...',
    maxDistance: 'Distancia máxima',
    km: 'km',
    genders: {
      men: 'Hombres',
      women: 'Mujeres',
      nonbinary: 'No binario',
      everyone: 'Todos',
    },
    types: {
      dating: 'Citas casuales',
      serious: 'Relación seria',
      friends: 'Solo amigos',
      activity: 'Compañeros de actividades',
    },
  },
  
  // Match
  match: {
    title: '¡Es un Match!',
    subtitle: '¡Tú y {name} se gustaron mutuamente!',
    sendMessage: 'Enviar Mensaje',
    keepDiscovering: 'Seguir Descubriendo',
  },
  
  // Navigation
  nav: {
    discover: 'Descubrir',
    matches: 'Matches',
    chat: 'Chat',
    profile: 'Perfil',
  },
  
  // Accessibility
  a11y: {
    title: 'Accesibilidad',
    switchLanguage: 'Cambiar idioma',
    goBack: 'Volver',
    toggleTag: 'Alternar etiqueta {tag}',
    passProfile: 'Pasar este perfil',
    connectProfile: 'Conectar con esta persona',
    superLike: 'Súper Like',
    sendMessage: 'Enviar mensaje',
    recordVoice: 'Grabar mensaje de voz',
    textSize: 'Tamaño de Texto',
    highContrast: 'Alto Contraste',
    reducedMotion: 'Movimiento Reducido',
  },
  
  // Stats
  stats: {
    members: 'Miembros',
    connections: 'Conexiones',
    happy: 'Felices',
  },
  
  // Auth
  auth: {
    orContinueWith: 'o continúa con',
    loginWithFacebook: 'Continuar con Facebook',
    loginWithInstagram: 'Continuar con Instagram',
  },
}
