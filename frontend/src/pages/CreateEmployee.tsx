import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useWorkspaceStore } from '../lib/workspace-store'

const inputClass =
  'w-full bg-bg/60 border border-border rounded-lg px-3.5 py-2.5 text-[13.5px] outline-none focus:border-primary text-text'

export function CreateEmployee() {
  const navigate = useNavigate()
  const workspace = useWorkspaceStore((s) => s.current)

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful assistant.')
  const [model, setModel] = useState('llama3')
  const [temperature, setTemperature] = useState(0.7)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (!workspace) return <Navigate to="/app" replace />

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const employee = await api.createEmployee(workspace!.id, {
        name,
        description: description || undefined,
        system_prompt: systemPrompt,
        model,
        temperature,
      })
      navigate(`/app/chat/${employee.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create employee')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <h1 className="font-display font-semibold text-[26px] mb-1.5">Create AI Employee</h1>
      <p className="text-text-dim text-[13.5px] mb-7">Configure a new AI employee for this workspace.</p>

      <form onSubmit={handleSubmit} className="glass rounded-xl p-7 max-w-[520px]">
        <Field label="Name">
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Customer Support AI"
            className={inputClass}
          />
        </Field>

        <Field label="Description">
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Drafts customer replies for review"
            className={inputClass}
          />
        </Field>

        <Field label="System prompt">
          <textarea
            required
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={3}
            className={`${inputClass} resize-none`}
          />
        </Field>

        <Field label="Model">
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="llama3 (or claude-sonnet-4-6 with a paid key)"
            className={inputClass}
          />
        </Field>

        <Field label={`Temperature: ${temperature.toFixed(1)}`}>
          <input
            type="range"
            min={0}
            max={1}
            step={0.1}
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            className="w-full accent-primary"
          />
        </Field>

        {error && <p className="text-[12.5px] text-red-400 mb-3">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-gradient-to-br from-primary to-indigo-600 text-white rounded-lg py-3 font-semibold text-sm mt-2 disabled:opacity-60"
        >
          {submitting ? 'Creating…' : 'Create Employee'}
        </button>
      </form>

    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-[18px]">
      <label className="block text-[12.5px] text-text-dim mb-1.5 font-medium">{label}</label>
      {children}
    </div>
  )
}
