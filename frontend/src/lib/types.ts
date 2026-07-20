export interface User {
  id: number
  email: string
  is_active: boolean
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Workspace {
  id: number
  name: string
  slug: string
  description: string | null
  owner_id: number
}

export type WorkspaceRole = 'owner' | 'admin' | 'member'
export type MembershipStatus = 'pending' | 'active'

export interface WorkspaceMember {
  id: number
  workspace_id: number
  user_id: number | null
  invited_email: string
  role: WorkspaceRole
  status: MembershipStatus
  created_at: string
}

export interface Employee {
  id: number
  workspace_id: number
  created_by: number
  name: string
  description: string | null
  system_prompt: string
  model: string
  temperature: number
  is_active: boolean
  created_at: string
}

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'failed'
export type DocumentType = 'pdf' | 'docx'

export interface KnowledgeDocument {
  id: number
  workspace_id: number
  employee_id: number
  uploaded_by: number
  filename: string
  file_type: DocumentType
  status: DocumentStatus
  error_message: string | null
  created_at: string
}

export interface Conversation {
  id: number
  workspace_id: number
  employee_id: number
  user_id: number
  title: string | null
  created_at: string
}

export type MessageRole = 'user' | 'assistant'

export interface Citation {
  document_id: number
  chunk_id: number
  filename: string
  snippet: string
}

export interface Message {
  id: number
  conversation_id: number
  role: MessageRole
  content: string
  citations: Citation[] | null
  created_at: string
}

export type ApprovalStatus = 'pending' | 'approved' | 'rejected'

export interface Approval {
  id: number
  workspace_id: number
  employee_id: number
  conversation_id: number | null
  prompt: string
  draft_content: string
  status: ApprovalStatus
  requested_by: number
  reviewed_by: number | null
  review_note: string | null
  created_at: string
  reviewed_at: string | null
}

export interface AuditLogEntry {
  id: number
  workspace_id: number
  actor_id: number
  action: string
  entity_type: string
  entity_id: number
  event_metadata: Record<string, unknown> | null
  created_at: string
}

export interface UsageSummary {
  message_count: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  cost_usd: number
}

export interface EmployeeUsage extends UsageSummary {
  employee_id: number | null
}

// Streaming chat events — matches the SSE payloads chat_service.stream_reply yields
export type ChatStreamEvent =
  | { type: 'conversation_id'; conversation_id: number }
  | { type: 'delta'; text: string }
  | { type: 'done'; message_id: number; content: string; citations: Citation[] }
