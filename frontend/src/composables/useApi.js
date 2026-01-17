/**
 * useApi Composable - Vue 3 composable for API interactions
 */

import { ref, reactive } from 'vue'
import api, { profileApi, matchingApi, chatApi, userApi } from '../services/api.js'

/**
 * Create a reactive API call wrapper
 */
const createApiCall = (apiFunction) => {
  const data = ref(null)
  const error = ref(null)
  const isLoading = ref(false)

  const execute = async (...args) => {
    isLoading.value = true
    error.value = null
    
    try {
      data.value = await apiFunction(...args)
      return { success: true, data: data.value }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  return { data, error, isLoading, execute }
}

/**
 * Profile composable
 */
export function useProfile() {
  const profile = ref(null)
  const tags = ref([])
  const interests = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const fetchProfile = async () => {
    isLoading.value = true
    error.value = null
    try {
      profile.value = await profileApi.getMyProfile()
      return profile.value
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateProfile = async (data) => {
    isLoading.value = true
    error.value = null
    try {
      profile.value = await profileApi.updateProfile(data)
      return { success: true, profile: profile.value }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      isLoading.value = false
    }
  }

  const fetchTags = async () => {
    try {
      const response = await profileApi.getTags()
      tags.value = response.results || response
      return tags.value
    } catch (err) {
      console.error('Failed to fetch tags:', err)
      return []
    }
  }

  const fetchInterests = async () => {
    try {
      const response = await profileApi.getInterests()
      interests.value = response.results || response
      return interests.value
    } catch (err) {
      console.error('Failed to fetch interests:', err)
      return []
    }
  }

  const updateMood = async (mood) => {
    try {
      await profileApi.updateMood(mood)
      if (profile.value) {
        profile.value.current_mood = mood
      }
      return { success: true }
    } catch (err) {
      return { success: false, error: err.message }
    }
  }

  const updateLookingFor = async (data) => {
    try {
      await profileApi.updateLookingFor(data)
      return { success: true }
    } catch (err) {
      return { success: false, error: err.message }
    }
  }

  return {
    profile,
    tags,
    interests,
    isLoading,
    error,
    fetchProfile,
    updateProfile,
    fetchTags,
    fetchInterests,
    updateMood,
    updateLookingFor,
  }
}

/**
 * Discovery/Matching composable
 */
export function useDiscovery() {
  const profiles = ref([])
  const currentIndex = ref(0)
  const isLoading = ref(false)
  const error = ref(null)
  const lastMatch = ref(null)

  const currentProfile = () => profiles.value[currentIndex.value] || null

  const fetchProfiles = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await matchingApi.discover()
      profiles.value = response.results || response || []
      currentIndex.value = 0
      return profiles.value
    } catch (err) {
      error.value = err.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  const swipe = async (action) => {
    const profile = currentProfile()
    if (!profile) return { success: false, error: 'No profile to swipe on' }

    try {
      const result = await matchingApi.swipe(profile.id, action)
      
      // Move to next profile
      currentIndex.value++
      
      // Check if it's a match
      if (result.is_match) {
        lastMatch.value = result.match
      }
      
      // Fetch more profiles if running low
      if (currentIndex.value >= profiles.value.length - 2) {
        fetchProfiles()
      }
      
      return { success: true, isMatch: result.is_match, match: result.match }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    }
  }

  const pass = () => swipe('pass')
  const like = () => swipe('like')
  const superLike = () => swipe('super')

  return {
    profiles,
    currentIndex,
    currentProfile,
    isLoading,
    error,
    lastMatch,
    fetchProfiles,
    swipe,
    pass,
    like,
    superLike,
  }
}

/**
 * Matches composable
 */
export function useMatches() {
  const matches = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const fetchMatches = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await matchingApi.getMatches()
      matches.value = response.results || response || []
      return matches.value
    } catch (err) {
      error.value = err.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  return {
    matches,
    isLoading,
    error,
    fetchMatches,
  }
}

/**
 * Chat composable
 */
export function useChat() {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const fetchConversations = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await chatApi.getConversations()
      conversations.value = response.results || response || []
      return conversations.value
    } catch (err) {
      error.value = err.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  const openConversation = async (conversationId) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await chatApi.getMessages(conversationId)
      messages.value = response.results || response || []
      currentConversation.value = conversationId
      return messages.value
    } catch (err) {
      error.value = err.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  const sendMessage = async (content, messageType = 'text') => {
    if (!currentConversation.value) {
      return { success: false, error: 'No conversation selected' }
    }

    try {
      const message = await chatApi.sendMessage(
        currentConversation.value, 
        content, 
        messageType
      )
      messages.value.push(message)
      return { success: true, message }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    }
  }

  return {
    conversations,
    currentConversation,
    messages,
    isLoading,
    error,
    fetchConversations,
    openConversation,
    sendMessage,
  }
}

export default {
  useProfile,
  useDiscovery,
  useMatches,
  useChat,
}
