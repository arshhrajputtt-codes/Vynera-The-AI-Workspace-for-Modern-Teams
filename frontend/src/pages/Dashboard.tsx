import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import { useAuthStore } from '../lib/auth-store'
import { useWorkspaceStore } from '../lib/workspace-store'
import type { Workspace } from '../lib/types'

function timeGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}

export function Dashboard() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const user = useAuthStore((s) => s.user)
  const setCurrentWorkspace = useWorkspaceStore((s) => s.setCurrent)

  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')

  const { data: workspaces, isLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: api.listWorkspaces,
  })

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newName.trim()) return
    await api.createWorkspace(newName.trim())
    setNewName('')
    setCreating(false)
    queryClient.invalidateQueries({ queryKey: ['workspaces'] })
  }

  function openWorkspace(workspace: Workspace) {
    setCurrentWorkspace(workspace)
    navigate('/app/workspace')
  }

  const displayName = user?.email?.split('@')[0] ?? 'there'

  return (
    <div>
      <div className="mb-11">
        <h1 className="font-display font-semibold text-[26px] mb-2">
          {timeGreeting()}, {displayName} 👋
        </h1>
        <p className="text-text-dim text-sm">
          {isLoading
            ? 'Loading your workspaces…'
            : `${workspaces?.length ?? 0} workspace${workspaces?.length === 1 ? '' : 's'}`}
        </p>
      </div>

      <div className="text-xs uppercase tracking-wider text-text-faint mb-3">Your Workspaces</div>
      <div className="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-4">
        {workspaces?.map((ws) => (
          <button
            key={ws.id}
            onClick={() => openWorkspace(ws)}
            className="glass rounded-xl p-6 text-left hover:border-border-hover hover:bg-glass-hover transition-all"
          >
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xl mb-4">
              🏢
            </div>
            <div className="font-display font-semibold text-base mb-1">{ws.name}</div>
            <div className="text-accent text-xs font-semibold">Open →</div>
          </button>
        ))}

        {creating ? (
          <form onSubmit={handleCreate} className="glass rounded-xl p-6 flex flex-col gap-2">
            <input
              autoFocus
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Workspace name"
              className="bg-bg/60 border border-border rounded-lg px-3 py-2 text-[13px] outline-none"
            />
            <div className="flex gap-2">
              <button type="submit" className="flex-1 bg-primary rounded-lg py-2 text-xs font-semibold">
                Create
              </button>
              <button type="button" onClick={() => setCreating(false)} className="text-text-dim text-xs px-2">
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setCreating(true)}
            className="border-[1.5px] border-dashed border-border rounded-xl min-h-[150px] flex items-center justify-center text-text-dim text-sm font-medium hover:border-primary hover:text-primary-soft transition-colors"
          >
            + Create New
          </button>
        )}
      </div>
    </div>
  )
}
