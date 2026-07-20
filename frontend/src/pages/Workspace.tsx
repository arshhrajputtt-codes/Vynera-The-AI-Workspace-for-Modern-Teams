import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { useWorkspaceStore } from '../lib/workspace-store'

const statusStyles: Record<string, string> = {
  online: 'bg-success/10 text-success',
  offline: 'bg-white/5 text-text-faint',
}

export function WorkspacePage() {
  const navigate = useNavigate()
  const workspace = useWorkspaceStore((s) => s.current)
  const [tab, setTab] = useState<'employees' | 'members'>('employees')

  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees', workspace?.id],
    queryFn: () => api.listEmployees(workspace!.id),
    enabled: !!workspace,
  })

  const { data: members } = useQuery({
    queryKey: ['members', workspace?.id],
    queryFn: () => api.listMembers(workspace!.id),
    enabled: !!workspace && tab === 'members',
  })

  // No workspace selected yet (e.g. direct navigation/refresh) — send back
  // to the dashboard rather than show a broken empty page.
  if (!workspace) return <Navigate to="/app" replace />

  return (
    <div>
      <h1 className="font-display font-semibold text-[26px] mb-6">{workspace.name}</h1>

      <div className="flex gap-1 border-b border-border mb-7">
        <button
          onClick={() => setTab('employees')}
          className={`px-4 py-2.5 text-[13.5px] border-b-2 -mb-px ${
            tab === 'employees' ? 'text-white border-primary' : 'text-text-dim border-transparent'
          }`}
        >
          AI Employees
        </button>
        <button
          onClick={() => setTab('members')}
          className={`px-4 py-2.5 text-[13.5px] border-b-2 -mb-px ${
            tab === 'members' ? 'text-white border-primary' : 'text-text-dim border-transparent'
          }`}
        >
          Members
        </button>
      </div>

      {tab === 'employees' && (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-4">
          {isLoading && <p className="text-text-dim text-sm">Loading employees…</p>}
          {employees?.map((emp) => (
            <button
              key={emp.id}
              onClick={() => navigate(`/app/chat/${emp.id}`)}
              className="glass rounded-xl p-5 text-left hover:border-border-hover hover:bg-glass-hover transition-all"
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-lg mb-3.5">
                🤖
              </div>
              <div className="font-semibold text-[15px] mb-1">{emp.name}</div>
              <span
                className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full mb-3 ${
                  statusStyles[emp.is_active ? 'online' : 'offline']
                }`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
                {emp.is_active ? 'Active' : 'Inactive'}
              </span>
              <div className="text-[11.5px] text-text-faint mb-3">{emp.model}</div>
              <div className="text-accent text-xs font-semibold">Open →</div>
            </button>
          ))}

          <button
            onClick={() => navigate('/app/workspace/employees/new')}
            className="border-[1.5px] border-dashed border-border rounded-xl min-h-[150px] flex items-center justify-center text-text-dim text-sm font-medium hover:border-primary hover:text-primary-soft transition-colors"
          >
            + Create AI Employee
          </button>
        </div>
      )}

      {tab === 'members' && (
        <div className="glass rounded-xl overflow-hidden">
          <table className="w-full text-[13px]">
            <thead>
              <tr className="text-left text-text-faint text-[11px] uppercase tracking-wider border-b border-border">
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {members?.map((m) => (
                <tr key={m.id} className="border-b border-border last:border-0">
                  <td className="px-4 py-3">{m.invited_email}</td>
                  <td className="px-4 py-3 capitalize">{m.role}</td>
                  <td className="px-4 py-3 capitalize">{m.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
