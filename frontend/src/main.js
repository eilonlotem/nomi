import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initSentry } from './composables/useErrorHandler'

const app = createApp(App)
app.use(router)

// Initialize Sentry error tracking
initSentry(app, router)

app.mount('#app')
