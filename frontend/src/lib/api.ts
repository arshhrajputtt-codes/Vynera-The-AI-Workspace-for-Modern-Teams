import { useAuthStore } from './auth-store'
import type {
  Approval,
  AuditLogEntry,
  ChatStreamEvent,
  Employee,
  EmployeeUsage,
  KnowledgeDocument,
  Message,
  Token,
  User,
  UsageSummary,
  Workspace,
  WorkspaceMember,
} from './types'

const IDENTITY_URL = import.meta.env.VITE_IDENTITY_API_URL ?? 'http://localhost:8000'
const CORE_URL = import.meta.env.VITE_CORE_API_URL ?? 'http://localhost:8001'

class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(baseUrl: string, path: string, options: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().token
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) ?? {}),
  }

  const response = await fetch(`${baseUrl}${path}`, { ...options, headers })

  if (response.status === 401) {
    // Token expired or invalid — same handling everywhere a call fails auth,
    // rather than every page having to remember to check this itself.
    useAuthStore.getState().logout()
    throw new ApiError(401, 'Session expired — please log in again')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new ApiError(response.status, body.detail ?? 'Request failed')
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

const identity = <T,>(path: string, options?: RequestInit) => request<T>(IDENTITY_URL, path, options)
const core = <T,>(path: string, options?: RequestInit) => request<T>(CORE_URL, path, options)

export const api = {
  // --- Auth (identity-service) ---
  register: (email: string, password: string) =>
    identity<User>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) }),

  login: (email: string, password: string) =>
    identity<Token>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  me: () => identity<User>('/auth/me'),

  // --- Workspaces (identity-service) ---
  createWorkspace: (name: string, description?: string) =>
    identity<Workspace>('/workspaces', { method: 'POST', body: JSON.stringify({ name, description }) }),

  listWorkspaces: () => identity<Workspace[]>('/workspaces'),

  getWorkspace: (workspaceId: number) => identity<Workspace>(`/workspaces/${workspaceId}`),

  listMembers: (workspaceId: number) => identity<WorkspaceMember[]>(`/workspaces/${workspaceId}/members`),

  inviteMember: (workspaceId: number, email: string, role: string) =>
    identity<WorkspaceMember>(`/workspaces/${workspaceId}/members/invite`, {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    }),

  // --- Employees (core-service) ---
  listEmployees: (workspaceId: number) => core<Employee[]>(`/workspaces/${workspaceId}/employees`),

  getEmployee: (workspaceId: number, employeeId: number) =>
    core<Employee>(`/workspaces/${workspaceId}/employees/${employeeId}`),

  createEmployee: (
    workspaceId: number,
    data: { name: string; description?: string; system_prompt: string; model?: string; temperature?: number }
  ) => core<Employee>(`/workspaces/${workspaceId}/employees`, { method: 'POST', body: JSON.stringify(data) }),

  updateEmployee: (workspaceId: number, employeeId: number, data: Partial<Employee>) =>
    core<Employee>(`/workspaces/${workspaceId}/employees/${employeeId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteEmployee: (workspaceId: number, employeeId: number) =>
    core<void>(`/workspaces/${workspaceId}/employees/${employeeId}`, { method: 'DELETE' }),

  // --- Knowledge base (core-service) ---
  listDocuments: (workspaceId: number, employeeId: number) =>
    core<KnowledgeDocument[]>(`/workspaces/${workspaceId}/employees/${employeeId}/documents`),

  uploadDocument: async (workspaceId: number, employeeId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return core<KnowledgeDocument>(`/workspaces/${workspaceId}/employees/${employeeId}/documents`, {
      method: 'POST',
      body: formData,
    })
  },

  deleteDocument: (workspaceId: number, employeeId: number, documentId: number) =>
    core<void>(`/workspaces/${workspaceId}/employees/${employeeId}/documents/${documentId}`, {
      method: 'DELETE',
    }),

  // --- Conversations (core-service) ---
  listConversations: (workspaceId: number, employeeId: number) =>
    core(`/workspaces/${workspaceId}/employees/${employeeId}/conversations`),

  getConversationHistory: (workspaceId: number, employeeId: number, conversationId: number) =>
    core<Message[]>(`/workspaces/${workspaceId}/employees/${employeeId}/conversations/${conversationId}/messages`),

  // --- Chat streaming (core-service) — hand-rolled SSE, see comment below ---
  streamChat: async (
    workspaceId: number,
    employeeId: number,
    message: string,
    conversationId: number | null,
    onEvent: (event: ChatStreamEvent) => void
  ) => {
    const token = useAuthStore.getState().token
    const response = await fetch(`${CORE_URL}/workspaces/${workspaceId}/employees/${employeeId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    })

    if (!response.ok || !response.body) {
      const body = await response.json().catch(() => ({ detail: response.statusText }))
      throw new ApiError(response.status, body.detail ?? 'Chat request failed')
    }

    // Native EventSource can't send an Authorization header, so the backend's
    // SSE stream has to be parsed by hand here: read raw bytes, decode, and
    // split on the blank line that separates each "data: {...}" frame —
    // same format we were reading manually in curl during backend testing.
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const frames = buffer.split('\n\n')
      buffer = frames.pop() ?? ''

      for (const frame of frames) {
        const line = frame.trim()
        if (!line.startsWith('data:')) continue
        const jsonStr = line.slice(5).trim()
        if (!jsonStr) continue
        try {
          onEvent(JSON.parse(jsonStr) as ChatStreamEvent)
        } catch {
          // A partial/malformed frame — skip rather than crash the stream.
        }
      }
    }
  },

  // --- Approvals (core-service) ---
  createDraft: (workspaceId: number, employeeId: number, prompt: string, conversationId?: number) =>
    core<Approval>(`/workspaces/${workspaceId}/employees/${employeeId}/drafts`, {
      method: 'POST',
      body: JSON.stringify({ prompt, conversation_id: conversationId }),
    }),

  listApprovals: (workspaceId: number, status?: string) =>
    core<Approval[]>(`/workspaces/${workspaceId}/approvals${status ? `?status=${status}` : ''}`),

  approveApproval: (workspaceId: number, approvalId: number, note?: string) =>
    core<Approval>(`/workspaces/${workspaceId}/approvals/${approvalId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    }),

  rejectApproval: (workspaceId: number, approvalId: number, note?: string) =>
    core<Approval>(`/workspaces/${workspaceId}/approvals/${approvalId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    }),

  getAuditLog: (workspaceId: number) => core<AuditLogEntry[]>(`/workspaces/${workspaceId}/audit-log`),

  // --- Analytics (core-service) ---
  getUsageSummary: (workspaceId: number) => core<UsageSummary>(`/workspaces/${workspaceId}/analytics/usage`),

  getUsageByEmployee: (workspaceId: number) =>
    core<EmployeeUsage[]>(`/workspaces/${workspaceId}/analytics/usage/by-employee`),
}

export { ApiError }
