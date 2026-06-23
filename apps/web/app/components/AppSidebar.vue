<script setup lang="ts">
const route = useRoute()

const items = [
  { to: '/', label: 'Home', icon: 'i-heroicons-home' },
  { to: '/chat', label: 'Chat', icon: 'i-heroicons-chat-bubble-left-right' },
  { to: '/', label: 'AI Hub', icon: 'i-heroicons-bolt' },
  { to: '/studio', label: 'Dev Studio', icon: 'i-heroicons-code-bracket' },
  { to: '/', label: 'Life OS', icon: 'i-heroicons-clipboard-document-list' },
]

function isActive(path: string) {
  return route.path === path
}
</script>

<template>
  <aside class="w-[52px] bg-[#191919] border-r border-white/[0.08] flex flex-col items-center py-3 shrink-0 h-screen">
    <div class="mb-4 shrink-0">
      <div class="w-8 h-8 rounded-lg bg-[#7b68ee] flex items-center justify-center text-white font-bold text-sm">E</div>
    </div>

    <nav class="flex-1 flex flex-col gap-2 min-h-0 overflow-y-auto scrollbar-hide py-1">
      <template v-for="item in items" :key="item.label">
        <NuxtLink
          v-if="item.to !== '/' || item.label === 'Home'"
          :to="item.to"
          :title="item.label"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors shrink-0"
          :class="[
            isActive(item.to) ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]',
          ]"
        >
          <UIcon :name="item.icon" class="w-5 h-5" />
        </NuxtLink>
        <button
          v-else
          :title="item.label"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] shrink-0"
        >
          <UIcon :name="item.icon" class="w-5 h-5" />
        </button>
      </template>
    </nav>

    <div class="flex flex-col gap-2 mt-auto shrink-0 pt-2">
      <NuxtLink
        to="/settings"
        title="Settings"
        class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors shrink-0"
        :class="[
          route.path === '/settings' ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]',
        ]"
      >
        <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" />
      </NuxtLink>
      <button class="flex items-center justify-center w-9 h-9 rounded-lg text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] transition-colors shrink-0">
        <div class="w-7 h-7 rounded-full bg-[#7b68ee] flex items-center justify-center text-white text-xs font-medium">A</div>
      </button>
    </div>
  </aside>
</template>
