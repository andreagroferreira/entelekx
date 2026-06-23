<script setup lang="ts">
const route = useRoute()

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

function activeTabClass(tab: string) {
  return route.path === tabRoutes[tab]
}
</script>

<template>
  <div class="min-h-screen bg-[#111111] text-[#eeeeee] flex">
    <!-- Global Navigation (52px) -->
    <AppSidebar />

    <!-- Home Sidebar (255px) -->
    <aside class="w-[255px] bg-[#191919] border-r border-white/[0.08] flex flex-col shrink-0 h-screen">
      <div class="h-11 flex items-center px-4 border-b border-white/[0.08] shrink-0">
        <span class="font-semibold text-sm">EntelekX</span>
      </div>

      <div class="p-3 shrink-0">
        <button class="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.05] hover:bg-white/[0.08] text-[#b4b4b4] text-sm transition-colors">
          <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
          Search
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto scrollbar-hide px-2 space-y-1 min-h-0 pb-3">
        <!-- Home is real route -->
        <NuxtLink
          to="/"
          class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] transition-colors"
          :class="[
            $route.path === '/' ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]',
          ]"
        >
          <UIcon name="i-heroicons-home" class="w-4 h-4" />
          Home
        </NuxtLink>

        <!-- Placeholder sidebar items -->
        <button
          v-for="item in sidebarTop.filter(i => i.to !== '/')"
          :key="item.label"
          class="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] text-left transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]"
        >
          <UIcon :name="item.icon" class="w-4 h-4" />
          {{ item.label }}
        </button>

        <div class="px-3 py-1.5 mt-4 text-[11px] font-semibold uppercase tracking-wider text-[#7b7b7b]">Spaces</div>
        <!-- Wizarding Code is real route -->
        <NuxtLink
          to="/studio"
          class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] transition-colors"
          :class="[
            $route.path === '/studio' ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]',
          ]"
        >
          <span class="w-5 h-5 rounded bg-[#e5484d] text-white flex items-center justify-center text-[10px] font-bold">W</span>
          Wizarding Code
        </NuxtLink>

        <!-- EntelekX space is placeholder -->
        <button class="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] text-left transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]">
          <span class="w-5 h-5 rounded bg-[#7b68ee] text-white flex items-center justify-center text-[10px] font-bold">E</span>
          EntelekX
        </button>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="flex-1 flex flex-col min-w-0 bg-[#090909] h-screen overflow-hidden">
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
      <div class="flex-1 overflow-y-auto scrollbar-hide overflow-x-hidden">
        <slot />
      </div>
    </main>
  </div>
</template>
