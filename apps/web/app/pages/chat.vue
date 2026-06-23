<script setup lang="ts">
definePageMeta({ layout: false })

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
const messagesContainer = ref<HTMLElement | null>(null)

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

const conversations = [
  { id: '1', title: 'API design discussion', active: true, time: 'Today' },
  { id: '2', title: 'Refactor vector store', active: false, time: 'Today' },
  { id: '3', title: 'Landing page copy', active: false, time: 'Yesterday' },
]

const suggestions = [
  { title: 'Design REST endpoints', subtitle: 'for a task app' },
  { title: 'Review this schema', subtitle: 'for correctness' },
]

onMounted(async () => {
  await ensureSession()
})

async function ensureSession() {
  if (sessionId.value) return
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

function scrollToBottom() {
  nextTick(() => {
    messagesContainer.value?.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: 'smooth' })
  })
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
  scrollToBottom()

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

        if (event.event === 'message.delta') {
          if (!currentAssistant) {
            currentAssistant = { role: 'assistant', content: '', pending: true }
            messages.value.push(currentAssistant)
          }
          currentAssistant.content += event.data.delta || ''
          scrollToBottom()
        } else if (event.event === 'message.complete') {
          if (currentAssistant) {
            currentAssistant.id = event.data.id
            currentAssistant.pending = false
            currentAssistant = null
          } else {
            messages.value.push({ role: 'assistant', content: event.data.content || '', id: event.data.id })
          }
          scrollToBottom()
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
          scrollToBottom()
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

function riskColor(risk: string) {
  if (risk === 'high') return 'bg-[#e5484d]/15 text-[#e5484d]'
  if (risk === 'medium') return 'bg-[#f59e0b]/15 text-[#f59e0b]'
  return 'bg-[#10b981]/15 text-[#10b981]'
}

function triggerSuggestion(suggestion: { title: string; subtitle: string }) {
  input.value = `${suggestion.title} ${suggestion.subtitle}`
  sendMessage()
}
</script>

<template>
  <div class="min-h-screen bg-[#111111] text-[#eeeeee] flex">
    <!-- Global Navigation (52px) -->
    <AppSidebar />

    <!-- Chat sidebar -->
    <aside class="w-[255px] bg-[#191919] border-r border-white/[0.08] flex flex-col shrink-0 h-screen">
      <div class="h-11 flex items-center px-4 border-b border-white/[0.08] shrink-0">
        <span class="font-semibold text-sm">EntelekX</span>
      </div>
      <div class="p-3 shrink-0">
        <button class="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.09] text-[#eeeeee] text-sm transition-colors">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          New chat
        </button>
      </div>
      <nav class="flex-1 overflow-y-auto scrollbar-hide px-2 min-h-0 pb-3">
        <div class="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-[#7b7b7b]">Today</div>
        <button
          v-for="conv in conversations.filter(c => c.time === 'Today')"
          :key="conv.id"
          class="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] text-left transition-colors"
          :class="conv.active ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
          {{ conv.title }}
        </button>

        <div class="px-3 py-1 mt-3 text-[11px] font-semibold uppercase tracking-wider text-[#7b7b7b]">Yesterday</div>
        <button
          v-for="conv in conversations.filter(c => c.time === 'Yesterday')"
          :key="conv.id"
          class="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-[13px] text-left transition-colors"
          :class="conv.active ? 'bg-white/[0.08] text-[#eeeeee]' : 'text-[#b4b4b4] hover:text-[#eeeeee] hover:bg-white/[0.06]'"
        >
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
          {{ conv.title }}
        </button>
      </nav>
    </aside>

    <!-- Chat main area -->
    <div class="flex-1 flex flex-col min-w-0 bg-[#090909] h-screen overflow-hidden">
      <!-- Top bar -->
      <div class="h-11 bg-[#111111] border-b border-white/[0.08] flex items-center justify-between px-4 shrink-0">
        <div class="flex items-center gap-2 text-sm">
          <span class="text-[#b4b4b4]">Chat</span>
          <span class="text-[#7b7b7b]">/</span>
          <span class="font-medium text-[#eeeeee]">API design discussion</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn-ghost">Rename</button>
          <select v-model="model" class="bg-[#111111] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[13px] text-[#eeeeee] focus:outline-none focus:border-white/[0.18]">
            <option v-for="opt in providerOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
      </div>

      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto scrollbar-hide px-6 py-8 overflow-x-hidden">
        <div class="max-w-3xl mx-auto">
          <!-- Empty state -->
          <div v-if="messages.length === 0" class="text-center py-16">
            <div class="w-14 h-14 rounded-2xl bg-[#111111] border border-white/[0.08] flex items-center justify-center mx-auto mb-5 text-[#7b68ee]">
              <UIcon name="i-heroicons-chat-bubble-left-right" class="w-7 h-7" />
            </div>
            <h3 class="text-xl font-semibold text-[#eeeeee] mb-2">How can I help?</h3>
            <p class="text-sm text-[#b4b4b4] mb-8">Ask me to design endpoints, review code, or plan the schema.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md mx-auto">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion.title"
                class="text-left px-4 py-3 rounded-xl bg-[#111111] border border-white/[0.08] hover:border-white/[0.18] transition-colors"
                @click="triggerSuggestion(suggestion)"
              >
                <div class="text-[#eeeeee] font-medium text-sm">{{ suggestion.title }}</div>
                <div class="text-2xs text-[#7b7b7b] mt-1">{{ suggestion.subtitle }}</div>
              </button>
            </div>
          </div>

          <!-- Message list -->
          <div v-else class="space-y-5">
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="flex"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                class="text-sm"
                :class="[
                  msg.role === 'user'
                    ? 'max-w-[80%] bg-[#7b68ee] text-white rounded-[14px] rounded-br-sm px-4 py-3'
                    : msg.role === 'tool'
                      ? 'max-w-[85%] bg-[#090909] border border-white/[0.08] rounded-[14px] rounded-bl-sm px-4 py-3 font-mono text-2xs w-full'
                      : 'max-w-[85%] bg-[#111111] border border-white/[0.08] rounded-[14px] rounded-bl-sm px-4 py-3',
                ]"
              >
                <div v-if="msg.toolCalls" class="space-y-2">
                  <div v-for="tc in msg.toolCalls" :key="tc.id" class="text-2xs">
                    <div class="font-semibold text-[#eeeeee]">Tool: {{ tc.name }}</div>
                    <pre class="mt-1 opacity-80">{{ tc.arguments }}</pre>
                  </div>
                </div>
                <div v-else-if="msg.role === 'tool'" class="whitespace-pre-wrap text-[#b4b4b4]">{{ formatToolOutput(msg.content) }}</div>
                <div v-else class="whitespace-pre-wrap text-[#eeeeee] leading-relaxed">{{ msg.content }}</div>
                <div v-if="msg.pending" class="mt-2">
                  <span class="inline-block w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Inline error -->
          <div v-if="error" class="mt-6 p-3 rounded-lg bg-[#e5484d]/10 border border-[#e5484d]/30 text-[#eeeeee] text-sm flex items-center gap-2">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-[#e5484d] shrink-0" />
            {{ error }}
          </div>
        </div>
      </div>

      <!-- Tool approval -->
      <div v-if="pendingTool" class="border-t border-white/[0.08] px-6 py-4">
        <div class="max-w-3xl mx-auto bg-[#111111] border border-[#f59e0b]/30 rounded-2xl rounded-bl-sm p-4">
          <div class="flex items-start justify-between gap-4">
            <div class="space-y-2 flex-1">
              <div class="font-semibold text-[#eeeeee]">Approve tool call: {{ pendingTool.name }}</div>
              <span :class="['text-2xs px-2 py-0.5 rounded-full', riskColor(pendingTool.risk)]">
                {{ pendingTool.risk }} risk
              </span>
              <pre class="text-2xs bg-[#090909] border border-white/[0.08] p-2 rounded-lg text-[#b4b4b4] overflow-x-auto">{{ JSON.stringify(pendingTool.arguments, null, 2) }}</pre>
            </div>
            <div class="flex gap-2">
              <button class="btn-ghost text-xs" @click="approveTool(false)">Reject</button>
              <button class="btn-primary text-xs" @click="approveTool(true)">Approve</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="border-t border-white/[0.08] px-6 py-4">
        <div class="max-w-3xl mx-auto">
          <div class="bg-[#111111] border border-white/[0.08] rounded-[14px] p-3 focus-within:border-white/[0.18] transition-colors">
            <textarea
              v-model="input"
              placeholder="Ask EntelekX anything..."
              rows="2"
              class="w-full bg-transparent text-sm text-[#eeeeee] placeholder-[#7b7b7b] resize-none outline-none"
              @keydown.enter.prevent="sendMessage"
            ></textarea>
            <div class="flex items-center justify-between mt-3">
              <div class="flex items-center gap-1">
                <button class="icon-btn">
                  <UIcon name="i-heroicons-paper-clip" class="w-4 h-4" />
                </button>
                <button class="icon-btn">
                  <UIcon name="i-heroicons-code-bracket" class="w-4 h-4" />
                </button>
              </div>
              <button
                class="btn-primary flex items-center gap-2"
                :disabled="loading"
                @click="sendMessage"
              >
                Send
                <UIcon name="i-heroicons-paper-airplane" class="w-4 h-4" />
              </button>
            </div>
          </div>
          <p class="text-center text-2xs text-[#7b7b7b] mt-2">EntelekX can make mistakes. Review important work.</p>
        </div>
      </div>
    </div>
  </div>
</template>
