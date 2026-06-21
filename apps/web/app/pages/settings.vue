<script setup lang="ts">
const apiBase = useRuntimeConfig().public.apiBase

const providers = ref([
  { name: 'openrouter', label: 'OpenRouter', key: '', model: 'openrouter/anthropic/claude-sonnet-4' },
  { name: 'openai', label: 'OpenAI', key: '', model: 'gpt-4o' },
  { name: 'anthropic', label: 'Anthropic', key: '', model: 'claude-sonnet-4-20250514' },
  { name: 'ollama', label: 'Ollama', key: '', model: 'llama3.1' },
  { name: 'qwen', label: 'Qwen', key: '', model: 'qwen-max' },
  { name: 'kimi', label: 'Kimi (Moonshot)', key: '', model: 'kimi-k2' },
  { name: 'minimax', label: 'MiniMax', key: '', model: 'MiniMax-Text-01' },
])

const defaultProvider = ref('openrouter')
const saving = ref(false)
const error = ref('')
const success = ref(false)

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
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-8">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Settings</h1>
      <UButton :loading="saving" color="primary" @click="save">Save</UButton>
    </div>

    <UCard class="space-y-4">
      <UFormGroup label="Default provider">
        <USelect v-model="defaultProvider" :options="providers.map(p => ({ label: p.label, value: p.name }))" option-attribute="label" value-attribute="value" />
      </UFormGroup>
    </UCard>

    <UCard v-for="p in providers" :key="p.name" class="space-y-4">
      <div class="font-semibold mb-2">{{ p.label }}</div>
      <UFormGroup label="API key">
        <UInput v-model="p.key" type="password" placeholder="Leave empty to use environment value" />
      </UFormGroup>
      <UFormGroup label="Default model">
        <UInput v-model="p.model" />
      </UFormGroup>
    </UCard>

    <UAlert v-if="error" color="red" variant="soft" :title="error" icon="i-heroicons-exclamation-triangle" />
    <UAlert v-if="success" color="green" variant="soft" title="Settings saved" icon="i-heroicons-check-circle" />
  </div>
</template>
