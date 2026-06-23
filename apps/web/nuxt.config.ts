export default defineNuxtConfig({
  compatibilityDate: '2026-06-21',
  devtools: { enabled: true },
  srcDir: 'app/',
  modules: ['@nuxt/ui', '@nuxtjs/tailwindcss'],
  colorMode: {
    preference: 'dark',
    fallback: 'dark',
    classSuffix: '',
    storage: 'cookie',
    dataValue: 'dark',
  },
  ui: {
    safelistColors: ['primary'],
    colors: {
      primary: 'emerald',
      neutral: 'zinc',
    },
  },
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: '~/tailwind.config.js',
    exposeConfig: false,
    viewer: false,
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:7349',
    },
  },
})
