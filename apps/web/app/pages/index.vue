<script setup lang="ts">
const { data: health, pending, error } = await useFetch('/api/health', {
  baseURL: useRuntimeConfig().public.apiBase,
})
</script>

<template>
  <div class="space-y-8">
    <section class="text-center py-12">
      <div class="w-16 h-16 rounded-2xl bg-primary mx-auto flex items-center justify-center text-white text-2xl font-bold mb-6">
        E
      </div>
      <h1 class="text-4xl font-bold mb-4">EntelekX</h1>
      <p class="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
        The personal AI operating system for builders who want to think, build, decide and ship — in one place.
      </p>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="p-6 rounded-xl border border-gray-200 dark:border-gray-800">
        <h3 class="font-semibold mb-2">Fusion Engine</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Run a panel of models and a judge to reach better answers.</p>
      </div>
      <div class="p-6 rounded-xl border border-gray-200 dark:border-gray-800">
        <h3 class="font-semibold mb-2">Dev Studio</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Scaffold, edit, test and deploy real applications.</p>
      </div>
      <div class="p-6 rounded-xl border border-gray-200 dark:border-gray-800">
        <h3 class="font-semibold mb-2">Life OS</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Notes, tasks, goals, decisions and a knowledge graph.</p>
      </div>
    </section>

    <section class="p-6 rounded-xl border border-gray-200 dark:border-gray-800">
      <h2 class="font-semibold mb-4">Backend Health</h2>
      <div v-if="pending">Checking...</div>
      <div v-else-if="error" class="text-red-600">Unable to reach backend. Is it running?</div>
      <div v-else class="font-mono text-sm">
        {{ health }}
      </div>
    </section>
  </div>
</template>
