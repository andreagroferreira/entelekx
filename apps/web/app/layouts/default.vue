<script setup lang="ts">
const route = useRoute()

const globalNav = [
  { to: '/', label: 'Home', icon: 'i-heroicons-home' },
  { to: '/chat', label: 'Chat', icon: 'i-heroicons-chat-bubble-left-right' },
  { to: '/', label: 'AI Hub', icon: 'i-heroicons-bolt' },
  { to: '/studio', label: 'Dev Studio', icon: 'i-heroicons-code-bracket' },
  { to: '/', label: 'Life OS', icon: 'i-heroicons-clipboard-document-list' },
]

const sidebarTop = [
  { to: '/', label: 'Home', icon: 'i-heroicons-home' },
  { to: '/', label: 'Inbox', icon: 'i-heroicons-bell' },
  { to: '/', label: 'Assigned comments', icon: 'i-heroicons-chat-bubble-left-right' },
  { to: '/', label: 'My Tasks', icon: 'i-heroicons-clipboard-document-list' },
  { to: '/', label: 'Spaces', icon: 'i-heroicons-squares-2x2' },
  { to: '/', label: 'Docs', icon: 'i-heroicons-document-text' },
  { to: '/chat', label: 'AI Chats', icon: 'i-heroicons-bolt' },
]

const spaces = [
  { to: '/studio', label: 'Wizarding Code', emoji: 'W' },
  { to: '/', label: 'EntelekX', emoji: 'E' },
]

const tabs = ['Overview', 'Chat', 'Studio', 'Tasks', 'Docs']
const tabRoutes: Record<string, string> = {
  Overview: '/',
  Chat: '/chat',
  Studio: '/studio',
  Tasks: '/',
  Docs: '/',
}

function isActive(path: string) {
  return route.path === path
}
function activeTabClass(tab: string) {
  return route.path === tabRoutes[tab]
}
</script>

<template>
  <div class="min-h-screen bg-[#111111] text-[#eeeeee] flex">
    <!-- Global Navigation (52px) -->
    <aside class="w-[52px] bg-[#191919] border-r border-white/[0.08] flex flex-col items-center py-3 shrink-0">
      <div class="mb-4">
        <div class="w-8 h-8 rounded-lg bg-[#7b68ee] flex items-center justify-center text-white font-bold text-sm">E</div>
      </div>

      <nav class="flex-1 flex flex-col gap-2">
        <NuxtLink
          v-for="item in globalNav"
          :key="item.to + item.label"
          :to="item.to"
          :title="item.label"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors"
          :class="isActive(item.to) ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon :name="item.icon" class="w-5 h-5" />
        </NuxtLink>
      </nav>

      <div class="flex flex-col gap-2 mt-auto">
        <NuxtLink
          to="/settings"
          title="Settings"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors"
          :class="isActive('/settings') ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" />
        </NuxtLink>
        <button class="flex items-center justify-center w-9 h-9 rounded-lg text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] transition-colors">
          <div class="w-7 h-7 rounded-full bg-[#7b68ee] flex items-center justify-center text-white text-xs font-medium">A</div>
        </button>
      </div>
    </aside>

    <!-- Home Sidebar (255px) -->
    <aside class="w-[255px] bg-[#191919] border-r border-white/[0.08] flex flex-col shrink-0">
      <div class="h-11 flex items-center px-4 border-b border-white/[0.08]">
        <span class="font-semibold text-sm">EntelekX</span>
      </div>

      <div class="p-3">
        <button class="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.05] hover:bg-white/[0.08] text-[#b4b4b4] text-sm transition-colors">
          <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
          Search
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto scrollbar-hide px-2 space-y-1">
        <NuxtLink
          v-for="item in sidebarTop"
          :key="item.label"
          :to="item.to"
          class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] transition-colors"
          :class="isActive(item.to) ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon :name="item.icon" class="w-4 h-4" />
          {{ item.label }}
        </NuxtLink>

        <div class="px-3 py-1.5 mt-4 text-[11px] font-semibold uppercase tracking-wider text-[#7b7b7b]">Spaces</div>
        <NuxtLink
          v-for="item in spaces"
          :key="item.label"
          :to="item.to"
          class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] transition-colors"
          :class="isActive(item.to) ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <span class="w-5 h-5 rounded bg-[#e5484d] text-white flex items-center justify-center text-[10px] font-bold">{{ item.emoji }}</span>
          {{ item.label }}
        </NuxtLink>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="flex-1 flex flex-col min-w-0 bg-[#090909]">
      <!-- Top bar -->
      <div class="h-11 bg-[#111111] border-b border-white/[0.08] flex items-center justify-between px-4 shrink-0">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 text-sm">
            <span class="font-medium text-[#eeeeee]">EntelekX</span>
            <span class="text-[11px] px-2 py-0.5 rounded-full bg-white/[0.08] text-[#b4b4b4]">Personal</span>
          </div>

          <div class="flex items-center ml-6">
            <button
              v-for="tab in tabs"
              :key="tab"
              class="px-3.5 py-2 text-[13px] border-b-2 transition-colors"
              :class="activeTabClass(tab) ? 'text-[#eeeeee] border-[#7b68ee]' : 'text-[#b4b4b4] border-transparent hover:text-[#eeeeee]'"
            >
              {{ tab }}
            </button>
            <button class="px-3.5 py-2 text-[13px] text-[#b4b4b4] border-b-2 border-transparent hover:text-[#eeeeee] transition-colors">+ View</button>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button class="btn-ghost">Agents</button>
          <button class="btn-ghost">Automate</button>
          <button class="btn-ghost">Brain</button>
          <button class="btn-ghost">Share</button>
          <div class="w-7 h-7 rounded-full bg-[#7b68ee] flex items-center justify-center text-white text-xs font-medium ml-2">A</div>
        </div>
      </div>

      <!-- Page content -->
      <div class="flex-1 overflow-auto scrollbar-hide">
        <slot />
      </div>
    </main>
  </div>
</template>
