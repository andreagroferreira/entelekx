<script setup lang="ts">
interface Message {
  id?: string
  role: 'user' | 'assistant' | 'tool' | 'system'
  content: string
  toolCalls?: any[]
  toolCallId?: string
  pending?: boolean
}

interface PendingTool {
  toolCallId: string
  name: string
  arguments: Record<string, any>
  risk: string
}

const apiBase = useRuntimeConfig().public.apiBase

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const error = ref('')
const pendingTool = ref<PendingTool | null>(null)
const model = ref('echo')
const sessionId = ref('')

const providerOptions = [
  { label: 'Echo (test)', value: 'echo' },
  { label: 'OpenRouter', value: 'openrouter' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'Ollama', value: 'ollama' },
  { label: 'Qwen', value: 'qwen' },
  { label: 'Kimi', value: 'kimi' },
  { label: 'MiniMax', value: 'minimax' },
]

onMounted(async () => {
  await ensureSession()
})

async function ensureSession() {
  if (sessionId.value) return
  // Create a default project/session for the demo.
  try {
    const project = await $fetch('/api/v1/projects', {
      baseURL: apiBase,
      method: 'POST',
      body: { name: 'Default', slug: 'default' },
    })
    const chatSession = await $fetch('/api/v1/sessions', {
      baseURL: apiBase,
      method: 'POST',
      body: { project_id: project.id, title: 'Chat', model: model.value },
    })
    sessionId.value = chatSession.id
  } catch (exc: any) {
    error.value = exc?.data?.detail || exc?.message || 'Could not create session'
  }
}

async function sendMessage() {
  if (!input.value.trim() || loading.value) return
  await ensureSession()
  if (!sessionId.value) return

  const userContent = input.value
  input.value = ''
  messages.value.push({ role: 'user', content: userContent })
  loading.value = true
  error.value = ''
  pendingTool.value = null

  try {
    const response = await fetch(`${apiBase}/api/v1/sessions/${sessionId.value}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: userContent }),
    })

    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentAssistant: Message | null = null

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      for (const chunk of lines) {
        const event = parseSseChunk(chunk)
        if (!event) continue

        if (event.event === 'message.user') {
          // Already added optimistically.
        } else if (event.event === 'message.delta') {
          if (!currentAssistant) {
            currentAssistant = { role: 'assistant', content: '', pending: true }
            messages.value.push(currentAssistant)
          }
          currentAssistant.content += event.data.delta || ''
        } else if (event.event === 'message.complete') {
          if (currentAssistant) {
            currentAssistant.id = event.data.id
            currentAssistant.pending = false
            currentAssistant = null
          } else {
            messages.value.push({ role: 'assistant', content: event.data.content || '', id: event.data.id })
          }
        } else if (event.event === 'message.tool_calls') {
          messages.value.push({ role: 'assistant', content: '', toolCalls: event.data.tool_calls })
        } else if (event.event === 'tool.approval') {
          pendingTool.value = {
            toolCallId: event.data.tool_call_id,
            name: event.data.name,
            arguments: event.data.arguments,
            risk: event.data.risk,
          }
          loading.value = false
          return
        } else if (event.event === 'tool.result') {
          messages.value.push({
            role: 'tool',
            content: JSON.stringify({ status: event.data.status, output: event.data.output, error: event.data.error }),
            toolCallId: event.data.tool_call_id,
          })
        } else if (event.event === 'error') {
          error.value = event.data.detail || 'Stream error'
          loading.value = false
          return
        }
      }
    }
  } catch (exc: any) {
    error.value = exc?.message || 'Failed to send message'
  } finally {
    loading.value = false
  }
}

function parseSseChunk(chunk: string): { event: string; data: any } | null {
  const lines = chunk.split('\n')
  let event = 'message'
  let data: any = {}
  for (const line of lines) {
    if (line.startsWith('event: ')) event = line.slice(7)
    else if (line.startsWith('data: ')) {
      try { data = JSON.parse(line.slice(6)) } catch { data = line.slice(6) }
    }
  }
  return { event, data }
}

async function approveTool(approved: boolean) {
  if (!pendingTool.value || !sessionId.value) return
  loading.value = true
  const toolCallId = pendingTool.value.toolCallId
  pendingTool.value = null

  try {
    const response = await fetch(`${apiBase}/api/v1/tool-approval/${toolCallId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved }),
    })
    if (!response.ok || !response.body) throw new Error(`HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentAssistant: Message | null = null

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      for (const chunk of lines) {
        const event = parseSseChunk(chunk)
        if (!event) continue
        if (event.event === 'message.delta') {
          if (!currentAssistant) {
            currentAssistant = { role: 'assistant', content: '', pending: true }
            messages.value.push(currentAssistant)
          }
          currentAssistant.content += event.data.delta || ''
        } else if (event.event === 'message.complete') {
          if (currentAssistant) {
            currentAssistant.id = event.data.id
            currentAssistant.pending = false
            currentAssistant = null
          }
        } else if (event.event === 'tool.result') {
          messages.value.push({
            role: 'tool',
            content: JSON.stringify({ status: event.data.status, output: event.data.output, error: event.data.error }),
            toolCallId: event.data.tool_call_id,
          })
        } else if (event.event === 'error') {
          error.value = event.data.detail || 'Approval error'
        }
      }
    }
  } catch (exc: any) {
    error.value = exc?.message || 'Failed to approve tool'
  } finally {
    loading.value = false
  }
}

function formatToolOutput(content: string): string {
  try {
    const parsed = JSON.parse(content)
    if (parsed.status === 'success' && typeof parsed.output === 'string') return parsed.output
    return JSON.stringify(parsed, null, 2)
  } catch {
    return content
  }
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-80px)]">
    <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-800">
      <div class="flex items-center gap-3">
        <h1 class="font-semibold text-lg">Chat</h1>
        <UBadge v-if="loading" color="primary" variant="soft">Thinking...</UBadge>
      </div>
      <UFormGroup label="Model" class="w-48">
        <USelect v-model="model" :options="providerOptions" option-attribute="label" value-attribute="value" />
      </UFormGroup>
    </div>

    <div class="flex-1 overflow-y-auto py-4 space-y-4">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          :class="[
            'max-w-[80%] rounded-2xl px-4 py-3 text-sm',
            msg.role === 'user'
              ? 'bg-primary text-white rounded-br-none'
              : msg.role === 'tool'
                ? 'bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-bl-none font-mono text-xs'
                : 'bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-bl-none',
          ]"
        >
          <div v-if="msg.toolCalls" class="space-y-2">
            <div v-for="tc in msg.toolCalls" :key="tc.id" class="text-xs">
              <div class="font-semibold">Tool: {{ tc.name }}</div>
              <pre class="mt-1 opacity-80">{{ tc.arguments }}</pre>
            </div>
          </div>
          <div v-else-if="msg.role === 'tool'" class="whitespace-pre-wrap">{{ formatToolOutput(msg.content) }}</div>
          <div v-else class="whitespace-pre-wrap">{{ msg.content }}</div>
          <div v-if="msg.pending" class="mt-1">
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
          </div>
        </div>
      </div>

      <UAlert
        v-if="error"
        color="red"
        variant="soft"
        :title="error"
        icon="i-heroicons-exclamation-triangle"
        class="mt-4"
      />
    </div>

    <div v-if="pendingTool" class="py-3">
      <UCard class="border-yellow-400 dark:border-yellow-600">
        <div class="flex items-start justify-between gap-4">
          <div class="space-y-1">
            <div class="font-semibold">Approve tool call: {{ pendingTool.name }}</div>
            <UBadge :color="pendingTool.risk === 'high' ? 'red' : pendingTool.risk === 'medium' ? 'yellow' : 'green'" variant="soft">
              {{ pendingTool.risk }} risk
            </UBadge>
            <pre class="text-xs bg-gray-100 dark:bg-gray-900 p-2 rounded">{{ JSON.stringify(pendingTool.arguments, null, 2) }}</pre>
          </div>
          <div class="flex gap-2">
            <UButton color="red" variant="soft" @click="approveTool(false)">Reject</UButton>
            <UButton color="green" @click="approveTool(true)">Approve</UButton>
          </div>
        </div>
      </UCard>
    </div>

    <div class="pt-4 border-t border-gray-200 dark:border-gray-800">
      <UFormGroup class="flex-1">
        <div class="flex gap-2">
          <UTextarea
            v-model="input"
            placeholder="Ask EntelekX anything..."
            :rows="2"
            class="flex-1"
            @keydown.enter.prevent="sendMessage"
          />
          <UButton
            :loading="loading"
            color="primary"
            class="self-end"
            @click="sendMessage"
          >
            Send
          </UButton>
        </div>
      </UFormGroup>
    </div>
  </div>
</template>
