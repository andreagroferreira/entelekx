<template>
  <div class="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <header class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
      <div class="flex items-center justify-between max-w-6xl mx-auto">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold">
            E
          </div>
          <span class="font-semibold text-lg">EntelekX</span>
        </div>
        <nav class="flex gap-4 text-sm">
          <NuxtLink to="/" class="hover:text-primary">Home</NuxtLink>
          <NuxtLink to="/chat" class="hover:text-primary">Chat</NuxtLink>
          <NuxtLink to="/studio" class="hover:text-primary">Studio</NuxtLink>
          <NuxtLink to="/settings" class="hover:text-primary">Settings</NuxtLink>
        </nav>
      </div>
    </header>

    <main class="max-w-6xl mx-auto p-6">
      <slot />
    </main>
  </div>
</template>
