import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initSentry } from './composables/useErrorHandler'

const app = createApp(App)
app.use(router)

// Initialize Sentry error tracking
initSentry(app, router)

// Disable autofill suggestions and keyboard accessory bar globally
document.addEventListener('DOMContentLoaded', () => {
  // Disable autofill on all inputs and textareas
  const disableAutofill = () => {
    const inputs = document.querySelectorAll('input, textarea')
    inputs.forEach(input => {
      if (!input.hasAttribute('autocomplete')) {
        input.setAttribute('autocomplete', 'off')
      }
      if (!input.hasAttribute('data-form-type')) {
        input.setAttribute('data-form-type', 'other')
      }
      if (!input.hasAttribute('data-lpignore')) {
        input.setAttribute('data-lpignore', 'true')
      }
    })
  }
  
  disableAutofill()
  
  // Re-run when DOM changes (for dynamically added inputs)
  const observer = new MutationObserver(disableAutofill)
  observer.observe(document.body, { childList: true, subtree: true })
})

app.mount('#app')
