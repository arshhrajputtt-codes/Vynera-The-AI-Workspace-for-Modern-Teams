import { useEffect, useRef, useState } from 'react'
import { Navigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { useWorkspaceStore } from '../lib/workspace-store'
import { KnowledgePanel } from '../components/KnowledgePanel'
import type { Citation } from '../lib/types'

interface DisplayMessage {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  streaming?: boolean
}

export function Chat() {
  const { employeeId } = useParams<{ employeeId: string }>()
  const workspace = useWorkspaceStore((s) => s.current)
  const employeeIdNum = Number(employeeId)

  const [messages, setMessages] = useState<DisplayMessage[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [sending, setSending] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data: employee } = useQuery({
    queryKey: ['employee', workspace?.id, employeeIdNum],
    queryFn: () => api.getEmployee(workspace!.id, employeeIdNum),
    enabled: !!workspace,
  })

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  if (!workspace) return <Navigate to="/app" replace />

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setMessages((prev) => [...prev, { role: 'assistant', content: '', streaming: true }])
    setSending(true)

    try {
      await api.streamChat(workspace!.id, employeeIdNum, text, conversationId, (event) => {
        if (event.type === 'conversation_id') {
          setConversationId(event.conversation_id)
        } else if (event.type === 'delta') {
          setMessages((prev) => {
            const next = [...prev]
            const lastIndex = next.length - 1
            const last = next[lastIndex]
            if (last?.streaming) {
              next[lastIndex] = { ...last, content: last.content + event.text }
            }
            return next
          })
        } else if (event.type === 'done') {
          setMessages((prev) => {
            const next = [...prev]
            const lastIndex = next.length - 1
            const last = next[lastIndex]
            if (last?.streaming) {
              next[lastIndex] = { ...last, streaming: false, citations: event.citations }
            }
            return next
          })
        }
      })
    } catch {
      setMessages((prev) => {
        const next = [...prev]
        const lastIndex = next.length - 1
        const last = next[lastIndex]
        if (last?.streaming) {
          next[lastIndex] = {
            ...last,
            content: 'Something went wrong generating a response. Try again.',
            streaming: false,
          }
        }
        return next
      })
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-60px)] -m-9">
      <div className="flex flex-col flex-1 min-w-0">
        <div className="px-7 py-4 border-b border-border flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-sm">
            🤖
          </div>
          <div>
            <div className="font-semibold text-[14.5px]">{employee?.name ?? 'Loading…'}</div>
            <div className="text-[11.5px] text-text-dim">{employee?.model}</div>
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-7 py-6 flex flex-col gap-4">
          {messages.length === 0 && (
            <p className="text-text-faint text-sm text-center mt-10">
              Start a conversation with {employee?.name ?? 'this employee'}.
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : ''}`}>
              <div
                className={`max-w-[520px] px-4 py-2.5 rounded-xl text-[13.5px] leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-gradient-to-br from-primary to-indigo-600 text-white rounded-br-sm'
                    : 'glass rounded-bl-sm'
                }`}
              >
                {m.content || (m.streaming ? '…' : '')}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-2.5 pt-2.5 border-t border-white/10 flex flex-col gap-1">
                    {m.citations.map((c, ci) => (
                      <div key={ci} className="text-[11px] text-text-dim">
                        [{ci + 1}] {c.filename} — {c.snippet.slice(0, 90)}…
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={handleSend} className="px-7 py-5 border-t border-border flex gap-2.5">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Message ${employee?.name ?? '...'}`}
            disabled={sending}
            className="flex-1 glass rounded-xl px-4 py-3 text-[13.5px] outline-none"
          />
          <button
            type="submit"
            disabled={sending}
            className="bg-gradient-to-br from-primary to-indigo-600 text-white rounded-xl px-5 font-semibold text-[13px] disabled:opacity-60"
          >
            Send
          </button>
        </form>
      </div>

      {workspace && <KnowledgePanel workspaceId={workspace.id} employeeId={employeeIdNum} />}
    </div>
  )
}