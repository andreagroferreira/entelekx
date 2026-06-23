<script setup lang="ts">
definePageMeta({ layout: false })

const activeTab = ref('Projects')
const tabs = ['Projects', 'Templates', 'Deployments', 'Tests', 'Logs']

const projects = [
  { name: 'entelekx-backend', stack: 'FastAPI · Python 3.12', status: 'Healthy', statusColor: 'text-[#10b981]', bg: 'bg-[#7b68ee]/15', icon: '🐍', files: '12 files', tests: '3 tests passing' },
  { name: 'entelekx-web', stack: 'Nuxt 3 · TypeScript', status: 'Unsynced', statusColor: 'text-[#f59e0b]', bg: 'bg-[#10b981]/15', icon: '🟢', files: '28 files', tests: 'Build pending' },
]

const templates = [
  { name: 'Laravel API', stack: 'PHP 8.4 · Pest', icon: '🟣' },
  { name: 'Nuxt 4 SPA', stack: 'Vue 3 · Tailwind', icon: '🟢' },
  { name: 'Next.js App', stack: 'React · TypeScript', icon: '🔵' },
  { name: 'FastAPI Service', stack: 'Python · SQLModel', icon: '🐍' },
]

const studioNav = [
  { label: 'Home', icon: 'i-heroicons-home', to: '/' },
  { label: 'Dev Studio', icon: 'i-heroicons-code-bracket', to: '/studio' },
]

const projectSpaces = [
  { label: 'entelekx-backend', emoji: '🐍', to: '/studio' },
  { label: 'entelekx-web', emoji: '🟢', to: '/studio' },
]

const route = useRoute()
function isActive(path: string) {
  return route.path === path
}
</script>

<template>
  <div class="min-h-screen bg-[#111111] text-[#eeeeee] flex">
    <!-- Global Navigation (52px) -->
    <aside class="w-[52px] bg-[#191919] border-r border-white/[0.08] flex flex-col items-center py-3 shrink-0 h-screen">
      <div class="mb-4 shrink-0">
        <div class="w-8 h-8 rounded-lg bg-[#7b68ee] flex items-center justify-center text-white font-bold text-sm">E</div>
      </div>
      <nav class="flex-1 flex flex-col gap-2 min-h-0 overflow-y-auto scrollbar-hide py-1">
        <NuxtLink
          to="/"
          title="Home"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] shrink-0"
        >
          <UIcon name="i-heroicons-home" class="w-5 h-5" />
        </NuxtLink>
        <NuxtLink
          to="/chat"
          title="Chat"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] shrink-0"
        >
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5" />
        </NuxtLink>
        <NuxtLink
          to="/"
          title="AI Hub"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] shrink-0"
        >
          <UIcon name="i-heroicons-bolt" class="w-5 h-5" />
        </NuxtLink>
        <NuxtLink
          to="/studio"
          title="Dev Studio"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors bg-white/[0.08] text-[#eeeeee] shrink-0"
        >
          <UIcon name="i-heroicons-code-bracket" class="w-5 h-5" />
        </NuxtLink>
        <NuxtLink
          to="/"
          title="Life OS"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] shrink-0"
        >
          <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" />
        </NuxtLink>
      </nav>
      <div class="flex flex-col gap-2 mt-auto shrink-0 pt-2">
        <NuxtLink
          to="/settings"
          title="Settings"
          class="flex items-center justify-center w-9 h-9 rounded-lg transition-colors text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] shrink-0"
        >
          <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" />
        </NuxtLink>
        <button class="flex items-center justify-center w-9 h-9 rounded-lg text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] transition-colors shrink-0">
          <div class="w-7 h-7 rounded-full bg-[#7b68ee] flex items-center justify-center text-white text-xs font-medium">A</div>
        </button>
      </div>
    </aside>

    <!-- Studio sidebar -->
    <aside class="w-[255px] bg-[#191919] border-r border-white/[0.08] flex flex-col shrink-0 h-screen">
      <div class="h-11 flex items-center px-4 border-b border-white/[0.08] shrink-0">
        <span class="font-semibold text-sm">EntelekX</span>
      </div>
      <nav class="flex-1 overflow-y-auto scrollbar-hide px-2 py-3 min-h-0">
        <NuxtLink
          v-for="item in studioNav"
          :key="item.label"
          :to="item.to"
          class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] transition-colors"
          :class="isActive(item.to) ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon :name="item.icon" class="w-4 h-4" />
          {{ item.label }}
        </NuxtLink>

        <div class="px-3 py-1.5 mt-4 text-[11px] font-semibold uppercase tracking-wider text-[#7b7b7b]">Projects</div>
        <NuxtLink
          v-for="item in projectSpaces"
          :key="item.label"
          :to="item.to"
          class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06] transition-colors"
        >
          <span class="text-base">{{ item.emoji }}</span>
          {{ item.label }}
        </NuxtLink>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0 bg-[#090909] h-screen overflow-hidden">
      <!-- Top bar -->
      <div class="h-11 bg-[#111111] border-b border-white/[0.08] flex items-center justify-between px-4 shrink-0">
        <div class="flex items-center gap-2 text-sm">
          <span class="text-[#b4b4b4]">Dev Studio</span>
          <span class="text-[#7b7b7b]">/</span>
          <span class="font-medium text-[#eeeeee]">Projects</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn-ghost">Import repo</button>
          <button class="btn-primary flex items-center gap-2">
            <UIcon name="i-heroicons-plus" class="w-4 h-4" />
            New project
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto scrollbar-hide p-6 overflow-x-hidden">
        <div class="max-w-[1200px] mx-auto">
          <div class="flex items-start justify-between mb-8">
            <div>
              <h1 class="text-3xl font-semibold mb-1 text-[#eeeeee]">Dev Studio</h1>
              <div class="text-sm text-[#b4b4b4]">Build, edit, test and ship applications.</div>
            </div>
          </div>

          <!-- Tabs -->
          <div class="border-b border-white/[0.08] mb-6">
            <div class="flex">
              <button
                v-for="tab in tabs"
                :key="tab"
                class="tab"
                :class="activeTab === tab ? 'active' : ''"
                @click="activeTab = tab"
              >
                {{ tab }}
              </button>
            </div>
          </div>

          <!-- Projects -->
          <div v-if="activeTab === 'Projects'">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
              <div
                v-for="project in projects"
                :key="project.name"
                class="card hover:border-white/[0.14] transition-colors cursor-pointer group"
              >
                <div class="flex items-start justify-between mb-4">
                  <div :class="['w-11 h-11 rounded-xl flex items-center justify-center text-2xl', project.bg, project.statusColor]">
                    {{ project.icon }}
                  </div>
                  <span :class="['tag', project.statusColor]">{{ project.status }}</span>
                </div>
                <div class="font-semibold text-[#eeeeee] group-hover:text-[#7b68ee] transition-colors">{{ project.name }}</div>
                <div class="text-xs text-[#7b7b7b] mt-1">{{ project.stack }}</div>
                <div class="text-xs text-[#7b7b7b] mt-4">{{ project.files }} · {{ project.tests }}</div>
              </div>

              <button class="card border-dashed border-white/[0.12] flex flex-col items-center justify-center text-center hover:border-white/[0.2] transition-colors"
              >
                <div class="w-12 h-12 rounded-full bg-white/[0.06] flex items-center justify-center text-[#7b7b7b] mb-3">
                  <UIcon name="i-heroicons-plus" class="w-6 h-6" />
                </div>
                <div class="text-sm font-medium text-[#eeeeee]">Create project</div>
                <div class="text-xs text-[#7b7b7b] mt-1">From template or repo</div>
              </button>
            </div>

            <h2 class="text-[11px] font-semibold uppercase tracking-wider text-[#7b7b7b] mb-4">Start from template</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                v-for="t in templates"
                :key="t.name"
                class="card hover:border-white/[0.14] transition-colors text-left"
              >
                <div class="text-2xl mb-2">{{ t.icon }}</div>
                <div class="text-sm font-medium text-[#eeeeee]">{{ t.name }}</div>
                <div class="text-xs text-[#7b7b7b] mt-1">{{ t.stack }}</div>
              </button>
            </div>
          </div>

          <!-- Other tabs placeholder -->
          <div v-else class="card text-center py-16">
            <UIcon name="i-heroicons-wrench" class="w-12 h-12 text-[#7b7b7b] mx-auto mb-4" />
            <div class="text-lg font-medium text-[#eeeeee] mb-2">{{ activeTab }}</div>
            <div class="text-sm text-[#b4b4b4]">This section will be available in Phase 3.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
