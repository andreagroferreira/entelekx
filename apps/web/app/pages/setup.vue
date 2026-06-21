<script setup lang="ts">
definePageMeta({
  layout: 'setup',
})

const apiBase = useRuntimeConfig().public.apiBase

const step = ref(0)
const loading = ref(false)
const error = ref('')

const steps = [
  { title: 'Welcome', description: 'Get started', icon: 'i-heroicons-sparkles' },
  { title: 'Database', description: 'Choose storage', icon: 'i-heroicons-circle-stack' },
  { title: 'Account', description: 'Create admin', icon: 'i-heroicons-user' },
  { title: 'Backup', description: 'Protect data', icon: 'i-heroicons-shield-check' },
  { title: 'AI', description: 'Connect models', icon: 'i-heroicons-chat-bubble-left-right' },
  { title: 'Finish', description: 'Review & open', icon: 'i-heroicons-check' },
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
    })
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
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex flex-col">
    <header class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
      <div class="max-w-3xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold">
            E
          </div>
          <span class="font-semibold text-lg">EntelekX</span>
        </div>
        <UButton
          variant="ghost"
          color="gray"
          size="xs"
          @click="skipToDashboard"
        >
          Skip setup
        </UButton>
      </div>
    </header>


    <main class="flex-1 flex flex-col max-w-3xl mx-auto w-full p-6">
      <div class="flex items-center justify-between mb-8">
        <div
          v-for="(s, idx) in steps"
          :key="idx"
          class="flex flex-col items-center text-center flex-1"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold mb-2"
            :class="step >= idx ? 'bg-primary text-white' : 'bg-gray-200 dark:bg-gray-800 text-gray-500 dark:text-gray-400'"
          >
            <UIcon v-if="step > idx" name="i-heroicons-check" class="w-4 h-4" />
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <span class="text-xs" :class="step >= idx ? 'text-primary font-medium' : 'text-gray-500 dark:text-gray-400'">
            {{ s.title }}
          </span>
        </div>
      </div>

      <div class="flex-1">
        <!-- Welcome -->
        <div v-if="step === 0" class="text-center py-10 space-y-6">
          <div class="w-20 h-20 rounded-2xl bg-primary mx-auto flex items-center justify-center text-white text-3xl font-bold">
            E
          </div>
          <div>
            <h1 class="text-3xl font-bold mb-2">Welcome to EntelekX</h1>
            <p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
              Your personal AI operating system for thinking, building, deciding and shipping — in one place.
            </p>
          </div>
          <UButton size="lg" trailing-icon="i-heroicons-arrow-right" @click="next">
            Get started
          </UButton>
        </div>

        <!-- Database -->
        <div v-if="step === 1" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Choose your database</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              EntelekX works best with PostgreSQL + pgvector, but SQLite is fine to start.
            </p>
          </div>

          <URadioGroup v-model="db.mode" :options="databaseOptions" />

          <div v-if="db.mode === 'managed'" class="space-y-2">
            <label class="text-sm font-medium">Postgres connection string</label>
            <UInput
              v-model="db.managedUrl"
              placeholder="postgresql://user:pass@host:5432/db"
            />
          </div>

          <div v-if="db.mode === 'sqlite'" class="p-4 rounded-lg bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 text-sm">
            SQLite is perfect for solo testing. You can migrate to Postgres later from Settings.
          </div>
        </div>

        <!-- Account -->
        <div v-if="step === 2" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Create your admin account</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              This is the owner account for this EntelekX instance.
            </p>
          </div>

          <div class="space-y-4">
            <UFormGroup label="Username">
              <UInput v-model="account.username" placeholder="founder" />
            </UFormGroup>
            <UFormGroup label="Password">
              <UInput v-model="account.password" type="password" placeholder="At least 8 characters" />
            </UFormGroup>
            <UFormGroup label="Confirm password">
              <UInput v-model="account.confirm" type="password" placeholder="Repeat password" />
            </UFormGroup>
          </div>
        </div>

        <!-- Backup -->
        <div v-if="step === 3" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Backup configuration</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Keep your data safe with automatic local backups.
            </p>
          </div>

          <div class="flex items-center gap-3">
            <UToggle v-model="backup.enabled" />
            <span class="text-sm font-medium">Enable automatic backups</span>
          </div>

          <div v-if="backup.enabled" class="space-y-4">
            <UFormGroup label="Backup folder">
              <UInput v-model="backup.path" placeholder="~/.entelekx/backups" />
            </UFormGroup>
            <UFormGroup label="Frequency">
              <USelect v-model="backup.frequency" :options="backupFrequencies" option-attribute="label" value-attribute="value" />
            </UFormGroup>
            <div class="flex items-center gap-3">
              <UToggle v-model="backup.encrypted" />
              <span class="text-sm font-medium">Encrypt backup archives</span>
            </div>
          </div>
        </div>

        <!-- AI -->
        <div v-if="step === 4" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">Connect your AI providers</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              OpenRouter is recommended: one key, many models. You can skip and add keys later.
            </p>
          </div>

          <div class="space-y-4">
            <UFormGroup label="Default provider">
              <USelect v-model="ai.provider" :options="aiProviders" option-attribute="label" value-attribute="value" />
            </UFormGroup>
            <UFormGroup v-if="ai.provider === 'openrouter'" label="OpenRouter API key">
              <UInput v-model="ai.openrouterKey" type="password" placeholder="sk-or-..." />
            </UFormGroup>
            <UFormGroup v-if="ai.provider === 'ollama'" label="Ollama base URL">
              <UInput v-model="ai.ollamaUrl" placeholder="http://localhost:11434" />
            </UFormGroup>
          </div>
        </div>

        <!-- Finish -->
        <div v-if="step === 5" class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-1">You're ready</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Review your choices and finish setup.
            </p>
          </div>

          <div class="rounded-xl border border-gray-200 dark:border-gray-800 divide-y divide-gray-200 dark:divide-gray-800">
            <div class="p-4 flex justify-between text-sm">
              <span class="text-gray-600 dark:text-gray-400">Database</span>
              <span class="font-medium">{{ db.mode === 'managed' ? 'Managed Postgres' : 'SQLite' }}</span>
            </div>
            <div class="p-4 flex justify-between text-sm">
              <span class="text-gray-600 dark:text-gray-400">Admin</span>
              <span class="font-medium">{{ account.username || '-' }}</span>
            </div>
            <div class="p-4 flex justify-between text-sm">
              <span class="text-gray-600 dark:text-gray-400">Backups</span>
              <span class="font-medium">{{ backup.enabled ? backup.frequency : 'Disabled' }}</span>
            </div>
            <div class="p-4 flex justify-between text-sm">
              <span class="text-gray-600 dark:text-gray-400">Default AI</span>
              <span class="font-medium capitalize">{{ ai.provider }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 space-y-4">
        <UAlert
          v-if="error"
          color="red"
          variant="soft"
          :title="error"
          icon="i-heroicons-exclamation-triangle"
        />

        <div class="flex items-center justify-between">
          <UButton
            variant="ghost"
            color="gray"
            :disabled="step === 0 || loading"
            @click="prev"
          >
            Back
          </UButton>
          <UButton
            v-if="step < steps.length - 1"
            trailing-icon="i-heroicons-arrow-right"
            :disabled="!canAdvance || loading"
            :loading="loading"
            @click="next"
          >
            Next
          </UButton>
          <UButton
            v-else
            trailing-icon="i-heroicons-check"
            :loading="loading"
            @click="finish"
          >
            Finish setup
          </UButton>
        </div>
      </div>
    </main>
  </div>
</template>

