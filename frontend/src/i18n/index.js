/**
 * i18n Configuration
 * 
 * This module provides a scalable internationalization system.
 * To add a new language:
 * 1. Create a new file in /src/i18n/locales/{lang}.js
 * 2. Add the language to the `languages` array below
 * 3. Import and register in the `translations` object
 */

import en from './locales/en.js'
import he from './locales/he.js'

// Available languages configuration
export const languages = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧', dir: 'ltr' },
  { code: 'he', name: 'Hebrew', nativeName: 'עברית', flag: '🇮🇱', dir: 'rtl' },
]

// All translations
export const translations = {
  en,
  he,
}

// Default language - Hebrew only
export const defaultLocale = 'he'

// Fallback language (used when a translation is missing)
export const fallbackLocale = 'he'

// Get language config by code
export function getLanguageConfig(code) {
  return languages.find(lang => lang.code === code) || languages[0]
}

// Check if language is RTL
export function isRTLLanguage(code) {
  const config = getLanguageConfig(code)
  return config?.dir === 'rtl'
}

// Get all RTL language codes
export function getRTLLanguages() {
  return languages.filter(lang => lang.dir === 'rtl').map(lang => lang.code)
}

// Get all LTR language codes  
export function getLTRLanguages() {
  return languages.filter(lang => lang.dir === 'ltr').map(lang => lang.code)
}
