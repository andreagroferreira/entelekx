/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'media',
  content: [
    './app/**/*.{vue,js,ts,jsx,tsx}',
    './app/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        ex: {
          bg: '#111111',
          'bg-deep': '#090909',
          sidebar: '#191919',
          surface: '#111111',
          border: 'rgba(255, 255, 255, 0.08)',
          'border-strong': 'rgba(255, 255, 255, 0.18)',
          text: '#eeeeee',
          'text-muted': '#b4b4b4',
          'text-faint': '#7b7b7b',
          brand: '#7b68ee',
          'brand-hover': '#8b7bf2',
          'brand-soft': '#d7d2fb',
          danger: '#e5484d',
          success: '#10b981',
          'success-hover': '#34d399',
          warning: '#f59e0b',
        },
      },
      borderRadius: {
        ex: '0.75rem',
        'ex-sm': '0.5rem',
      },
      fontSize: {
        '2xs': ['11px', '14px'],
      },
    },
  },
  plugins: [],
}
