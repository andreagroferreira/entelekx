<script setup lang="ts">
definePageMeta({
  layout: 'setup',
})

const apiBase = useRuntimeConfig().public.apiBase

const step = ref(1)
const loading = ref(false)
const error = ref('')

const steps = [
  { title: 'Welcome', icon: 'i-heroicons-sparkles' },
  { title: 'Database', icon: 'i-heroicons-circle-stack' },
  { title: 'Account', icon: 'i-heroicons-user' },
  { title: 'Backup', icon: 'i-heroicons-shield-check' },
  { title: 'AI', icon: 'i-heroicons-chat-bubble-left-right' },
  { title: 'Finish', icon: 'i-heroicons-check' },
]

const db = ref({
  mode: 'auto' as 'auto' | 'managed' | 'install' | 'sqlite',
  managedUrl: '',
})

const account = ref({
  username: '',
  password: '',
  confirm: '',
})

const backup = ref({
  enabled: true,
  path: '',
  frequency: 'daily',
  encrypted: true,
})

const ai = ref({
  provider: 'openrouter',
  openrouterKey: '',
  ollamaUrl: 'http://localhost:11434',
})

const databaseOptions = [
  { value: 'auto', label: 'Auto-detect PostgreSQL', description: 'Uses Postgres.app or Homebrew Postgres if installed' },
  { value: 'managed', label: 'Use managed Postgres', description: 'Supabase, Neon, Railway, etc.' },
  { value: 'install', label: 'Install Postgres.app', description: 'Download and install PostgreSQL for macOS' },
  { value: 'sqlite', label: 'Use SQLite (fallback)', description: 'No extra setup; stored locally' },
]

const backupFrequencies = [
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
]

const aiProviders = [
  { label: 'OpenRouter', value: 'openrouter' },
  { label: 'Ollama / Local', value: 'ollama' },
]

const canAdvance = computed(() => {
  if (step.value === 1) {
    if (db.value.mode === 'managed') return !!db.value.managedUrl
    return true
  }
  if (step.value === 2) {
    return (
      account.value.username.length >= 2
      && account.value.password.length >= 8
      && account.value.password === account.value.confirm
    )
  }
  if (step.value === 3) {
    return !backup.value.enabled || backup.value.path.length > 0
  }
  return true
})

async function validateDatabase() {
  loading.value = true
  error.value = ''
  try {
    let url = ''
    if (db.value.mode === 'sqlite') {
      url = 'sqlite+aiosqlite:///'
    } else if (db.value.mode === 'managed') {
      url = db.value.managedUrl
    } else {
      url = 'sqlite+aiosqlite:///'
    }
    const res = await $fetch('/api/v1/setup/validate-database', {
      baseURL: apiBase,
      method: 'POST',
      body: { url },
    }) as any
    if (!res.valid) {
      error.value = res.message || 'Database validation failed'
      return false
    }
    return true
  } catch (exc: any) {
    error.value = exc?.data?.message || exc?.message || 'Database validation request failed'
    return false
  } finally {
    loading.value = false
  }
}

async function next() {
  if (step.value === 1) {
    const ok = await validateDatabase()
    if (!ok) return
  }
  if (step.value < steps.length - 1) {
    error.value = ''
    step.value++
  }
}

function prev() {
  if (step.value > 0) {
    error.value = ''
    step.value--
  }
}

async function finish() {
  loading.value = true
  error.value = ''
  try {
    let databaseUrl = ''
    if (db.value.mode === 'managed') {
      databaseUrl = db.value.managedUrl
    } else {
      databaseUrl = 'sqlite+aiosqlite:///'
    }

    await $fetch('/api/v1/setup/initialize', {
      baseURL: apiBase,
      method: 'POST',
      body: {
        database_url: databaseUrl,
        admin_username: account.value.username,
        admin_password: account.value.password,
        backup_enabled: backup.value.enabled,
        backup_path: backup.value.path || undefined,
        backup_frequency: backup.value.frequency,
        backup_encrypted: backup.value.encrypted,
        default_provider: ai.value.provider,
        openrouter_api_key: ai.value.openrouterKey || undefined,
        ollama_base_url: ai.value.ollamaUrl || undefined,
      },
    })

    if (typeof window !== 'undefined' && (window as any).electronAPI?.setWizardCompleted) {
      await (window as any).electronAPI.setWizardCompleted(true)
      await (window as any).electronAPI.closeWizard()
    } else {
      await navigateTo('/')
    }
  } catch (exc: any) {
    error.value = exc?.data?.detail || exc?.data?.message || exc?.message || 'Setup failed'
  } finally {
    loading.value = false
  }
}

const router = useRouter()
async function skipToDashboard() {
  if (typeof window !== 'undefined' && (window as any).electronAPI?.closeWizard) {
    await (window as any).electronAPI.closeWizard()
  } else {
    await router.push('/')
  }
}

function isStepDone(idx: number) {
  return step.value > idx
}

function isStepCurrent(idx: number) {
  return step.value === idx
}
</script>

<template>
  <div class="min-h-screen bg-[#111111] text-[#eeeeee] flex flex-col">
    <!-- Header -->
    <header class="border-b border-white/[0.08] px-6 py-4">
      <div class="max-w-3xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-[#7b68ee] flex items-center justify-center text-white font-bold">E</div>
          <span class="font-semibold text-lg">EntelekX</span>
        </div>
        <button class="btn-ghost" @click="skipToDashboard">Skip setup</button>
      </div>
    </header>

    <main class="flex-1 flex flex-col max-w-3xl mx-auto w-full p-6">
      <!-- Steps -->
      <div class="flex items-center justify-between mb-10">
        <div
          v-for="(s, idx) in steps"
          :key="idx"
          class="flex flex-col items-center text-center flex-1"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold mb-2"
            :class="isStepDone(idx) || isStepCurrent(idx) ? 'bg-[#7b68ee] text-white' : 'bg-white/[0.06] text-[#7b7b7b]'"
          >
            <UIcon v-if="isStepDone(idx)" name="i-heroicons-check" class="w-4 h-4" />
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span
            class="text-xs"
            :class="isStepCurrent(idx) ? 'text-[#eeeeee] font-medium' : isStepDone(idx) ? 'text-[#7b68ee]' : 'text-[#7b7b7b]'"
          >
            {{ s.title }}
          </span>
        </div>
      </div>

      <!-- Step content -->
      <div class="flex-1">
        <!-- Welcome -->
        <div v-if="step === 0" class="text-center py-10 space-y-6">
          <div class="w-20 h-20 rounded-2xl bg-[#7b68ee] mx-auto flex items-center justify-center text-white text-3xl font-bold">E</div>
          <div>
            <h1 class="text-3xl font-bold mb-2">Welcome to EntelekX</h1>
            <p class="text-[#b4b4b4] max-w-md mx-auto">Your personal AI operating system for thinking, building, deciding and shipping — in one place.</p>
          </div>
          <button class="bg-[#10b981] text-[#090909] px-5 py-2.5 rounded-lg text-base font-medium hover:bg-[#34d399] transition-colors" @click="next">Get started</button>
        </div>

        <!-- Database -->
        <div v-if="step === 1" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Choose your database</h2>
            <p class="text-sm text-[#b4b4b4]">EntelekX works best with PostgreSQL + pgvector, but SQLite is fine to start.</p>
          </div>

          <div class="space-y-3">
            <label
              v-for="option in databaseOptions"
              :key="option.value"
              class="radio-card"
              :class="db.mode === option.value ? 'selected' : ''"
            >
              <input
                v-model="db.mode"
                type="radio"
                :value="option.value"
                class="mt-1 w-4 h-4 accent-[#7b68ee]"
              />
              <div class="flex-1">
                <div class="font-medium text-sm">{{ option.label }}</div>
                <div class="text-xs text-[#7b7b7b] mt-0.5">{{ option.description }}</div>
              </div>
            </label>
          </div>

          <div v-if="db.mode === 'managed'" class="space-y-2">
            <label class="text-sm font-medium">Postgres connection string</label>
            <input
              v-model="db.managedUrl"
              placeholder="postgresql://user:pass@host:5432/db"
              class="input"
            />
          </div>

          <div v-if="db.mode === 'sqlite'" class="p-4 rounded-xl bg-[#f59e0b]/10 text-[#f59e0b] text-sm border border-[#f59e0b]/20">
            SQLite is perfect for solo testing. You can migrate to Postgres later from Settings.
          </div>
        </div>

        <!-- Account -->
        <div v-if="step === 2" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Create your admin account</h2>
            <p class="text-sm text-[#b4b4b4]">This is the owner account for this EntelekX instance.</p>
          </div>

          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">Username</label>
              <input v-model="account.username" placeholder="founder" class="input" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">Password</label>
              <input v-model="account.password" type="password" placeholder="At least 8 characters" class="input" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">Confirm password</label>
              <input v-model="account.confirm" type="password" placeholder="Repeat password" class="input" />
            </div>
          </div>
        </div>

        <!-- Backup -->
        <div v-if="step === 3" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Backup configuration</h2>
            <p class="text-sm text-[#b4b4b4]">Keep your data safe with automatic local backups.</p>
          </div>

          <div class="flex items-center gap-3">
            <input id="backup-enabled" v-model="backup.enabled" type="checkbox" class="w-4 h-4 accent-[#7b68ee]" />
            <label for="backup-enabled" class="text-sm font-medium">Enable automatic backups</label>
          </div>

          <div v-if="backup.enabled" class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">Backup folder</label>
              <input v-model="backup.path" placeholder="~/.entelekx/backups" class="input" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">Frequency</label>
              <select v-model="backup.frequency" class="input">
                <option v-for="f in backupFrequencies" :key="f.value" :value="f.value">{{ f.label }}</option>
              </select>
            </div>
            <div class="flex items-center gap-3">
              <input id="backup-encrypted" v-model="backup.encrypted" type="checkbox" class="w-4 h-4 accent-[#7b68ee]" />
              <label for="backup-encrypted" class="text-sm font-medium">Encrypt backup archives</label>
            </div>
          </div>
        </div>

        <!-- AI -->
        <div v-if="step === 4" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Connect your AI providers</h2>
            <p class="text-sm text-[#b4b4b4]">OpenRouter is recommended: one key, many models. You can skip and add keys later.</p>
          </div>

          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">Default provider</label>
              <select v-model="ai.provider" class="input">
                <option v-for="p in aiProviders" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </div>
            <div v-if="ai.provider === 'openrouter'" class="space-y-2">
              <label class="text-sm font-medium">OpenRouter API key</label>
              <input v-model="ai.openrouterKey" type="password" placeholder="sk-or-..." class="input" />
            </div>
            <div v-if="ai.provider === 'ollama'" class="space-y-2">
              <label class="text-sm font-medium">Ollama base URL</label>
              <input v-model="ai.ollamaUrl" placeholder="http://localhost:11434" class="input" />
            </div>
          </div>
        </div>

        <!-- Finish -->
        <div v-if="step === 5" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">You're ready</h2>
            <p class="text-sm text-[#b4b4b4]">Review your choices and finish setup.</p>
          </div>

          <div class="rounded-xl bg-[#111111] border border-white/[0.08] divide-y divide-white/[0.08]">
            <div class="p-4 flex justify-between text-sm">
              <span class="text-[#b4b4b4]">Database</span>
              <span class="font-medium">{{ db.mode === 'managed' ? 'Managed Postgres' : 'SQLite' }}</span>
            </div>
            <div class="p-4 flex justify-between text-sm">
              <span class="text-[#b4b4b4]">Admin</span>
              <span class="font-medium">{{ account.username || '-' }}</span>
            </div>
            <div class="p-4 flex justify-between text-sm">
              <span class="text-[#b4b4b4]">Backups</span>
              <span class="font-medium">{{ backup.enabled ? backup.frequency : 'Disabled' }}</span>
            </div>
            <div class="p-4 flex justify-between text-sm">
              <span class="text-[#b4b4b4]">Default AI</span>
              <span class="font-medium capitalize">{{ ai.provider }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-8 space-y-4">
        <div v-if="error" class="p-3 rounded-lg bg-[#e5484d]/10 border border-[#e5484d]/30 text-[#eeeeee] text-sm flex items-center gap-2">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-[#e5484d] shrink-0" />
          {{ error }}
        </div>

        <div class="flex items-center justify-between">
          <button
            class="btn-ghost"
            :disabled="step === 0 || loading"
            @click="prev"
          >
            Back
          </button>
          <button
            v-if="step < steps.length - 1"
            class="bg-[#10b981] text-[#090909] px-4 py-2 rounded-lg text-[13px] font-medium hover:bg-[#34d399] transition-colors disabled:opacity-50 flex items-center gap-2"
            :disabled="!canAdvance || loading"
            @click="next"
          >
            Next
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </button>
          <button
            v-else
            class="bg-[#10b981] text-[#090909] px-4 py-2 rounded-lg text-[13px] font-medium hover:bg-[#34d399] transition-colors disabled:opacity-50 flex items-center gap-2"
            :disabled="loading"
            @click="finish"
          >
            Finish setup
            <UIcon name="i-heroicons-check" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </main>
  </div>
</template>
