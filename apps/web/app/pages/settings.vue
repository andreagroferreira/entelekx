<script setup lang="ts">
definePageMeta({ layout: false })

const apiBase = useRuntimeConfig().public.apiBase

const providers = ref([
  { name: 'openrouter', label: 'OpenRouter', key: 'sk-or-v1-••••••••', model: 'anthropic/claude-sonnet-4', icon: '🌐', description: 'Access 100+ models with one key.' },
  { name: 'openai', label: 'OpenAI', key: '', model: 'gpt-4o', icon: '⚡', description: 'gpt-4o' },
  { name: 'anthropic', label: 'Anthropic', key: '', model: 'claude-sonnet-4-20250514', icon: '🅰', description: 'claude-sonnet-4-20250514' },
  { name: 'ollama', label: 'Ollama', key: '', model: 'llama3.1', icon: '🦙', description: 'llama3.1 · http://localhost:11434' },
  { name: 'qwen', label: 'Qwen', key: '', model: 'qwen-max', icon: '🇶', description: 'qwen-max' },
  { name: 'kimi', label: 'Kimi (Moonshot)', key: '', model: 'kimi-k2', icon: '🇰', description: 'kimi-k2' },
  { name: 'minimax', label: 'MiniMax', key: '', model: 'MiniMax-Text-01', icon: 'Ⓜ️', description: 'MiniMax-Text-01' },
])

const defaultProvider = ref('openrouter')
const saving = ref(false)
const error = ref('')
const success = ref(false)

const expanded = ref<Set<string>>(new Set(['openrouter']))

const settingsNav = [
  { label: 'AI Providers', icon: 'i-heroicons-cog-6-tooth', active: true },
  { label: 'Database', icon: 'i-heroicons-circle-stack' },
  { label: 'Security', icon: 'i-heroicons-lock-closed' },
  { label: 'Backup', icon: 'i-heroicons-shield-check' },
  { label: 'Appearance', icon: 'i-heroicons-computer-desktop' },
]

const ollamaModelDisplay = computed(() => 'llama3.1 · http://localhost:11434')

function toggleExpand(name: string) {
  const next = new Set(expanded.value)
  if (next.has(name)) next.delete(name)
  else next.add(name)
  expanded.value = next
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = false
  try {
    const body: Record<string, any> = {
      default_provider: defaultProvider.value,
    }
    for (const p of providers.value) {
      body[`${p.name}_api_key`] = p.key
      body[`${p.name}_model`] = p.model
    }
    await $fetch('/api/v1/setup/initialize', {
      baseURL: apiBase,
      method: 'POST',
      body,
    })
    success.value = true
  } catch (exc: any) {
    error.value = exc?.data?.detail || exc?.message || 'Failed to save settings'
  } finally {
    saving.value = false
  }
}

function defaultProviderLabel() {
  return providers.value.find(p => p.name === defaultProvider.value)?.label || defaultProvider.value
}
</script>

<template>
  <div class="min-h-screen bg-[#111111] text-[#eeeeee] flex">
    <!-- Global Navigation (52px) -->
    <AppSidebar />

    <!-- Settings sidebar -->
    <aside class="w-[255px] bg-[#191919] border-r border-white/[0.08] flex flex-col shrink-0 h-screen">
      <div class="h-11 flex items-center px-4 border-b border-white/[0.08] shrink-0">
        <span class="font-semibold text-sm">EntelekX</span>
      </div>
      <nav class="flex-1 overflow-y-auto scrollbar-hide px-2 py-3 min-h-0">
        <button
          v-for="item in settingsNav"
          :key="item.label"
          class="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] text-left transition-colors"
          :class="item.active ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon :name="item.icon" class="w-4 h-4" />
          {{ item.label }}
        </button>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0 bg-[#090909] h-screen overflow-hidden">
      <!-- Top bar -->
      <div class="h-11 bg-[#111111] border-b border-white/[0.08] flex items-center justify-between px-4 shrink-0">
        <div class="flex items-center gap-2 text-sm">
          <span class="text-[#b4b4b4]">Settings</span>
          <span class="text-[#7b7b7b]">/</span>
          <span class="font-medium text-[#eeeeee]">AI Providers</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn-ghost">Cancel</button>
          <button class="btn-primary" :disabled="saving" @click="save">
            {{ saving ? 'Saving...' : 'Save settings' }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto scrollbar-hide p-8 overflow-x-hidden">
        <div class="max-w-2xl mx-auto">
          <div class="mb-8">
            <h1 class="text-3xl font-semibold mb-2 text-[#eeeeee]">AI Providers</h1>
            <div class="text-sm text-[#b4b4b4]">Connect at least one model to start chatting. OpenRouter is recommended.</div>
          </div>

          <!-- Default provider -->
          <div class="card mb-6">
            <div class="text-sm font-medium text-[#eeeeee] mb-3">Default provider</div>
            <select v-model="defaultProvider" class="input">
              <option v-for="p in providers" :key="p.name" :value="p.name">{{ p.label }}</option>
            </select>
          </div>

          <!-- Providers -->
          <div class="space-y-3">
            <div
              v-for="(p, idx) in providers"
              :key="p.name"
              class="card relative overflow-hidden transition-colors"
              :class="p.name === 'openrouter' ? 'border-[#7b68ee]/30' : ''"
            >
              <div
                v-if="p.name === 'openrouter'"
                class="absolute top-4 right-4 text-2xs px-3 py-1 rounded-full bg-[#7b68ee] text-white font-medium"
              >
                Recommended
              </div>

              <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-4">
                  <div
                    class="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                    :class="p.name === defaultProvider ? 'bg-[#7b68ee] text-white' : 'bg-[#090909] border border-white/[0.08]'"
                  >
                    {{ p.icon }}
                  </div>
                  <div>
                    <div class="font-semibold text-[#eeeeee]">{{ p.label }}</div>
                    <div class="text-2xs text-[#7b7b7b]">
                      {{ p.name === 'openrouter'
                        ? p.description
                        : p.name === 'ollama'
                          ? ollamaModelDisplay
                          : p.model }}
                    </div>
                  </div>
                </div>
                <span
                  class="text-2xs px-2.5 py-1 rounded-full"
                  :class="p.key ? 'bg-[#10b981]/15 text-[#10b981]' : 'bg-[#090909] text-[#7b7b7b]'"
                >
                  {{ p.key ? 'Connected' : 'Not configured' }}
                </span>
              </div>

              <div v-if="expanded.has(p.name)" class="space-y-4">
                <div class="space-y-2">
                  <label class="block text-xs text-[#7b7b7b]">API key</label>
                  <input v-model="p.key" type="password" class="input" />
                </div>
                <div class="space-y-2">
                  <label class="block text-xs text-[#7b7b7b]">Default model</label>
                  <input v-model="p.model" class="input" />
                </div>
              </div>
            </div>
          </div>

          <!-- Feedback -->
          <div class="flex items-center justify-end gap-3 mt-10">
            <div v-if="error" class="flex-1 mr-4 p-3 rounded-lg bg-[#e5484d]/10 border border-[#e5484d]/30 text-[#eeeeee] text-sm flex items-center gap-2">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-[#e5484d] shrink-0" />
              {{ error }}
            </div>
            <div v-if="success" class="flex-1 mr-4 p-3 rounded-lg bg-[#10b981]/10 border border-[#10b981]/30 text-[#eeeeee] text-sm flex items-center gap-2">
              <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-[#10b981] shrink-0" />
              Settings saved
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
