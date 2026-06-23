<script setup lang="ts">
const { data: health, pending, error } = await useFetch('/api/health', {
  baseURL: useRuntimeConfig().public.apiBase,
})

const actions = [
  { label: 'New chat', description: 'Ask EntelekX anything', icon: 'i-heroicons-chat-bubble-left-right', color: 'brand', to: '/chat' },
  { label: 'Run Fusion', description: 'Multi-model panel', icon: 'i-heroicons-bolt', color: 'success', to: '/chat' },
  { label: 'Scaffold project', description: 'Pick a template', icon: 'i-heroicons-code-bracket', color: 'warning', to: '/studio' },
  { label: 'New task', description: 'Add to Life OS', icon: 'i-heroicons-clipboard-document-list', color: 'neutral', to: '/' },
]

const recent = [
  { title: 'API design discussion', meta: 'Chat · 2 hours ago', badge: '12 messages', icon: 'i-heroicons-chat-bubble-left-right', color: 'text-[#7b68ee]', bg: 'bg-white/[0.06]' },
  { title: 'Fusion: landing copy', meta: 'Fusion · yesterday', badge: '3 models', icon: 'i-heroicons-bolt', color: 'text-[#10b981]', bg: 'bg-white/[0.06]' },
  { title: 'entelekx-backend', meta: 'Dev Studio · 2 days ago', badge: 'Synced', icon: 'i-heroicons-code-bracket', color: 'text-[#f59e0b]', bg: 'bg-white/[0.06]' },
]

const tasks = [
  { title: 'Review Fusion panel results', due: 'Today', priority: 'High', priorityColor: 'text-[#e5484d]' },
  { title: 'Write SPEC-002 for Fusion Engine', due: 'Tomorrow', priority: 'Medium', priorityColor: 'text-[#f59e0b]' },
  { title: 'Configure local Ollama', due: 'This week', priority: 'Low', priorityColor: 'text-[#10b981]' },
]

const docs = [
  { title: 'EntelekX README' },
  { title: 'SPEC-001 Agent Kernel' },
]

const chats = [
  { title: 'API design discussion', model: 'Claude Sonnet 4', count: '12 msgs' },
]
</script>

<template>
  <div class="p-5">
    <div class="max-w-[1400px] mx-auto">
      <!-- Banner -->
      <div class="mb-5 flex items-center justify-between">
        <div class="text-sm text-[#b4b4b4]">
          Get the most out of your workspace. Add cards to customize this page.
        </div>
        <button class="btn-ghost text-xs">Get Started</button>
      </div>

      <!-- Cards grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Quick actions -->
        <div class="card">
          <div class="font-semibold text-sm mb-4">Quick actions</div>
          <div class="grid grid-cols-2 gap-3">
            <NuxtLink
              v-for="action in actions"
              :key="action.label"
              :to="action.to"
              class="flex items-center gap-3 p-3 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] transition-colors"
            >
              <div
                class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                :class="{
                  'bg-[#7b68ee] text-white': action.color === 'brand',
                  'bg-[#10b981]/15 text-[#10b981]': action.color === 'success',
                  'bg-[#f59e0b]/15 text-[#f59e0b]': action.color === 'warning',
                  'bg-white/[0.08] text-[#b4b4b4]': action.color === 'neutral',
                }"
              >
                <UIcon :name="action.icon" class="w-4 h-4" />
              </div>
              <div class="min-w-0">
                <div class="text-sm font-medium text-[#eeeeee] truncate">{{ action.label }}</div>
                <div class="text-xs text-[#7b7b7b]">{{ action.description }}</div>
              </div>
            </NuxtLink>
          </div>
        </div>

        <!-- Recent -->
        <div class="card">
          <div class="font-semibold text-sm mb-4">Recent</div>
          <div class="space-y-1">
            <NuxtLink
              v-for="item in recent"
              :key="item.title"
              to="/chat"
              class="flex items-center justify-between p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div :class="['w-8 h-8 rounded-lg flex items-center justify-center shrink-0', item.bg, item.color]">
                  <UIcon :name="item.icon" class="w-4 h-4" />
                </div>
                <div class="min-w-0">
                  <div class="text-sm text-[#eeeeee] truncate">{{ item.title }}</div>
                  <div class="text-xs text-[#7b7b7b]">{{ item.meta }}</div>
                </div>
              </div>
              <span class="text-xs text-[#7b7b7b] shrink-0">{{ item.badge }}</span>
            </NuxtLink>
          </div>
        </div>

        <!-- My Tasks -->
        <div class="card lg:row-span-2">
          <div class="flex items-center justify-between mb-4">
            <div class="font-semibold text-sm">My Tasks</div>
            <button class="btn-primary">+ New task</button>
          </div>
          <div class="border-b border-white/[0.08] mb-3">
            <div class="flex">
              <button class="tab active">To do</button>
              <button class="tab">Done</button>
              <button class="tab">All</button>
            </div>
          </div>
          <div class="space-y-1">
            <div
              v-for="task in tasks"
              :key="task.title"
              class="flex items-start gap-3 p-2 rounded-lg hover:bg-white/[0.04] cursor-pointer"
            >
              <div class="w-4 h-4 rounded-full border-2 border-[#7b7b7b] mt-0.5 shrink-0"></div>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-[#eeeeee]">{{ task.title }}</div>
                <div class="flex items-center gap-2 mt-1">
                  <span class="tag">{{ task.due }}</span>
                  <span :class="['tag', task.priorityColor]">{{ task.priority }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Docs -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <div class="font-semibold text-sm">Docs</div>
            <button class="btn-ghost text-xs">+ New doc</button>
          </div>
          <div class="space-y-1">
            <div
              v-for="doc in docs"
              :key="doc.title"
              class="flex items-center gap-3 p-2 rounded-lg hover:bg-white/[0.04] cursor-pointer"
            >
              <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-[#b4b4b4]" />
              <div class="text-sm text-[#eeeeee]">{{ doc.title }}</div>
            </div>
          </div>
        </div>

        <!-- AI Chats -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <div class="font-semibold text-sm">AI Chats</div>
            <NuxtLink to="/chat" class="btn-ghost text-xs">+ New chat</NuxtLink>
          </div>
          <div class="space-y-1">
            <NuxtLink
              v-for="chat in chats"
              :key="chat.title"
              to="/chat"
              class="flex items-center gap-3 p-2 rounded-lg hover:bg-white/[0.04] transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-[#7b68ee]/15 text-[#7b68ee] flex items-center justify-center">
                <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
              </div>
              <div class="min-w-0">
                <div class="text-sm text-[#eeeeee]">{{ chat.title }}</div>
                <div class="text-xs text-[#7b7b7b]">{{ chat.model }} · {{ chat.count }}</div>
              </div>
            </NuxtLink>
          </div>
        </div>

        <!-- System status -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <div class="font-semibold text-sm">System status</div>
            <span
              :class="[
                'text-xs px-2 py-0.5 rounded-full',
                pending ? 'bg-[#f59e0b]/15 text-[#f59e0b]' : error ? 'bg-[#e5484d]/15 text-[#e5484d]' : 'bg-[#10b981]/15 text-[#10b981]',
              ]"
            >
              {{ pending ? 'Checking...' : error ? 'Offline' : 'Online' }}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="p-3 rounded-lg bg-white/[0.04]">
              <div class="text-[#7b7b7b] text-xs mb-1">Database</div>
              <div :class="error ? 'text-[#e5484d]' : 'text-[#10b981]'">{{ error ? 'Disconnected' : 'Connected' }}</div>
            </div>
            <div class="p-3 rounded-lg bg-white/[0.04]">
              <div class="text-[#7b7b7b] text-xs mb-1">Vector store</div>
              <div :class="error ? 'text-[#e5484d]' : 'text-[#10b981]'">{{ error ? 'Unavailable' : 'Ready' }}</div>
            </div>
            <div class="p-3 rounded-lg bg-white/[0.04]">
              <div class="text-[#7b7b7b] text-xs mb-1">Agent kernel</div>
              <div class="text-[#10b981]">Running</div>
            </div>
            <div class="p-3 rounded-lg bg-white/[0.04]">
              <div class="text-[#7b7b7b] text-xs mb-1">Backup</div>
              <div class="text-[#eeeeee]">Daily · encrypted</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
