import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuthStore } from '../lib/auth-store'
import { Logo } from '../components/Logo'

export function Login() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const token = await api.login(email, password)
      // Login only returns the token; fetch the user separately with it.
      useAuthStore.setState({ token: token.access_token })
      const user = await api.me()
      setAuth(token.access_token, user)
      navigate('/app')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative">
      <Link to="/" className="absolute top-6 left-7 text-text-faint text-[13px]">
        ← Back
      </Link>
      <div className="glass w-[380px] p-9 rounded-xl">
        <div className="flex justify-center mb-4">
          <Logo size={32} />
        </div>
        <h1 className="font-display font-semibold text-2xl text-center mb-1.5">Welcome back</h1>
        <p className="text-center text-text-dim text-[13px] mb-7">Log in to your workspace</p>

        <form onSubmit={handleSubmit}>
          <div className="mb-3.5">
            <label className="block text-xs text-text-dim mb-1.5">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full bg-bg/60 border border-border rounded-lg px-3.5 py-2.5 text-[13.5px] outline-none focus:border-primary"
            />
          </div>
          <div className="mb-3.5">
            <label className="block text-xs text-text-dim mb-1.5">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-bg/60 border border-border rounded-lg px-3.5 py-2.5 text-[13.5px] outline-none focus:border-primary"
            />
          </div>

          {error && <p className="text-[12.5px] text-red-400 mb-3">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-br from-primary to-indigo-600 text-white rounded-lg py-3 font-semibold text-sm mt-2 disabled:opacity-60"
          >
            {loading ? 'Logging in…' : 'Log In'}
          </button>
        </form>

        <p className="text-center text-[12.5px] text-text-dim mt-5">
          Don't have an account? <span className="text-accent">Register below</span>
        </p>
        <RegisterInline onRegistered={() => navigate('/login')} />
      </div>
    </div>
  )
}

// Kept lightweight and inline rather than a separate route — the backend
// treats register/login as two calls to the same auth flow, not two pages.
function RegisterInline({ onRegistered }: { onRegistered: () => void }) {
  const [open, setOpen] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState<string | null>(null)

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault()
    setStatus(null)
    try {
      await api.register(email, password)
      setStatus('Account created — log in above.')
      onRegistered()
    } catch (err) {
      setStatus(err instanceof ApiError ? err.message : 'Registration failed')
    }
  }

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="w-full text-center text-[12px] text-text-faint mt-2">
        Create an account
      </button>
    )
  }

  return (
    <form onSubmit={handleRegister} className="mt-4 pt-4 border-t border-border">
      <input
        type="email"
        required
        placeholder="New account email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full bg-bg/60 border border-border rounded-lg px-3.5 py-2 text-[13px] outline-none mb-2"
      />
      <input
        type="password"
        required
        minLength={8}
        placeholder="Password (min 8 characters)"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full bg-bg/60 border border-border rounded-lg px-3.5 py-2 text-[13px] outline-none mb-2"
      />
      {status && <p className="text-[12px] text-text-dim mb-2">{status}</p>}
      <button type="submit" className="w-full bg-white/5 border border-border rounded-lg py-2 text-[12.5px]">
        Create account
      </button>
    </form>
  )
}
