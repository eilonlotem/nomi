import { ref, computed, watch } from 'vue'
import { 
  translations, 
  languages, 
  defaultLocale, 
  fallbackLocale,
  getLanguageConfig,
  isRTLLanguage 
} from '../i18n/index.js'

// Global state
const currentLocale = ref(defaultLocale)
const isRTL = computed(() => isRTLLanguage(currentLocale.value))
const dir = computed(() => isRTL.value ? 'rtl' : 'ltr')
const currentLanguage = computed(() => getLanguageConfig(currentLocale.value))

// Watch for locale changes and update document direction
watch(currentLocale, (newLocale) => {
  const config = getLanguageConfig(newLocale)
  const direction = config?.dir || 'ltr'
  
  document.documentElement.setAttribute('dir', direction)
  document.documentElement.setAttribute('lang', newLocale)
  document.body.setAttribute('dir', direction)
  
  // Store preference in localStorage
  try {
    localStorage.setItem('nomi-locale', newLocale)
  } catch (e) {
    // localStorage not available
  }
}, { immediate: true })

// Try to restore locale from localStorage on init
try {
  const savedLocale = localStorage.getItem('nomi-locale')
  if (savedLocale && translations[savedLocale]) {
    currentLocale.value = savedLocale
  }
} catch (e) {
  // localStorage not available
}

/**
 * Get nested value from object using dot notation
 * @param {Object} obj - The object to search
 * @param {string} path - Dot notation path (e.g., 'profile.name')
 * @returns {*} The value or undefined
 */
function getNestedValue(obj, path) {
  const keys = path.split('.')
  let value = obj
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key]
    } else {
      return undefined
    }
  }
  
  return value
}

/**
 * Main i18n composable
 */
export function useI18n() {
  /**
   * Translate a key with optional parameter interpolation
   * @param {string} key - Translation key in dot notation (e.g., 'profile.name')
   * @param {Object} params - Parameters for interpolation (e.g., { count: 5 })
   * @returns {string} Translated string
   */
  const t = (key, params = {}) => {
    // Try current locale
    let value = getNestedValue(translations[currentLocale.value], key)
    
    // Fallback to default locale if not found
    if (value === undefined && currentLocale.value !== fallbackLocale) {
      value = getNestedValue(translations[fallbackLocale], key)
    }
    
    // Return key if translation not found
    if (value === undefined) {
      console.warn(`[i18n] Missing translation for key: ${key}`)
      return key
    }
    
    // Handle non-string values (e.g., nested objects)
    if (typeof value !== 'string') {
      return value
    }
    
    // Interpolate parameters
    if (Object.keys(params).length > 0) {
      return value.replace(/\{(\w+)\}/g, (_, param) => {
        return params[param] !== undefined ? params[param] : `{${param}}`
      })
    }
    
    return value
  }
  
  /**
   * Set the current locale
   * @param {string} locale - Locale code (e.g., 'en', 'he', 'es')
   */
  const setLocale = (locale) => {
    if (translations[locale]) {
      currentLocale.value = locale
    } else {
      console.warn(`[i18n] Unknown locale: ${locale}`)
    }
  }
  
  /**
   * Toggle between available locales (cycles through all)
   */
  const toggleLocale = () => {
    const currentIndex = languages.findIndex(lang => lang.code === currentLocale.value)
    const nextIndex = (currentIndex + 1) % languages.length
    currentLocale.value = languages[nextIndex].code
  }
  
  /**
   * Check if a translation key exists
   * @param {string} key - Translation key
   * @returns {boolean}
   */
  const hasTranslation = (key) => {
    return getNestedValue(translations[currentLocale.value], key) !== undefined
  }
  
  /**
   * Get all available languages
   * @returns {Array} Array of language configurations
   */
  const getLanguages = () => languages
  
  /**
   * Get RTL languages only
   * @returns {Array} Array of RTL language configurations
   */
  const getRTLLanguages = () => languages.filter(lang => lang.dir === 'rtl')
  
  /**
   * Get LTR languages only
   * @returns {Array} Array of LTR language configurations
   */
  const getLTRLanguages = () => languages.filter(lang => lang.dir === 'ltr')
  
  return {
    // Translation function
    t,
    
    // Reactive state
    locale: currentLocale,
    isRTL,
    dir,
    currentLanguage,
    
    // Methods
    setLocale,
    toggleLocale,
    hasTranslation,
    getLanguages,
    getRTLLanguages,
    getLTRLanguages,
    
    // Constants
    languages,
    defaultLocale,
    fallbackLocale,
  }
}
