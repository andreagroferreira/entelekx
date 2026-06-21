export interface HealthResponse {
  status: 'ok' | 'degraded'
  version: string
  database: 'connected' | 'unreachable'
}

export interface Project {
  id: string
  name: string
  slug: string
  stack: string
  createdAt: string
  updatedAt: string
}

export interface Session {
  id: string
  projectId: string
  title: string
  model: string
  createdAt: string
  updatedAt: string
}

export interface ChatMessage {
  id: string
  sessionId: string
  role: 'system' | 'user' | 'assistant' | 'tool'
  content: string
  createdAt: string
}
