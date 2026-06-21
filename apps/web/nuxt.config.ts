export default defineNuxtConfig({
  compatibilityDate: '2026-06-21',
  devtools: { enabled: true },
  modules: [],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:7349',
    },
  },
})
