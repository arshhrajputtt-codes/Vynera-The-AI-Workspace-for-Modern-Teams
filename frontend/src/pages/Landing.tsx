import { Link } from 'react-router-dom'
import { Logo } from '../components/Logo'

const features = [
  {
    title: 'Deploy AI employees that just work',
    items: [
      'Research markets and competitors',
      'Answer customers, drafted for review',
      'Analyze documents and reports',
      'Automate repetitive workflows',
    ],
    icon: '🤖',
  },
  {
    title: 'Grounded in your own knowledge',
    items: [
      'Upload PDFs, docs, and policies',
      'Every answer cites its source',
      'No hallucinated facts about your business',
    ],
    icon: '📚',
  },
  {
    title: 'Humans stay in control',
    items: ['Review drafts before they go out', 'Full audit trail on every decision', 'Roles per workspace'],
    icon: '🛡️',
  },
]

export function Landing() {
  return (
    <div className="relative overflow-x-hidden">
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 60% 40% at 20% 0%, rgba(99,102,241,0.22), transparent 60%), radial-gradient(ellipse 50% 35% at 85% 15%, rgba(34,211,238,0.14), transparent 60%)',
        }}
      />

      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-bg/70 backdrop-blur-md border-b border-border">
        <div className="flex items-center gap-2 font-display font-bold text-[17px]">
          <Logo size={20} />
          Vynera
        </div>
        <div className="hidden md:flex gap-8 text-[13.5px] text-text-dim">
          <a href="#product" className="hover:text-text">
            Product
          </a>
          <a href="#features" className="hover:text-text">
            Features
          </a>
          <a href="#pricing" className="hover:text-text">
            Pricing
          </a>
        </div>
        <div className="flex items-center gap-3.5">
          <Link to="/login" className="text-[13.5px] text-text-dim hover:text-text">
            Log in
          </Link>
          <Link
            to="/login"
            className="bg-gradient-to-br from-primary to-indigo-600 text-white text-[13px] font-semibold py-2 rounded-lg px-[18px]"
          >
            Get Started
          </Link>
        </div>
      </nav>

      <div className="relative z-10 pt-[168px] pb-16 px-6 text-center max-w-[820px] mx-auto">
        <span className="inline-flex items-center gap-1.5 text-[12.5px] text-accent bg-accent/10 border border-accent/25 px-4 py-1.5 rounded-full mb-7">
          ✨ Now in early access
        </span>
        <h1 className="font-display font-bold text-[42px] md:text-[64px] leading-[1.08] tracking-tight">
          Your AI workforce,
          <br />
          <span className="bg-gradient-to-br from-primary-soft to-accent bg-clip-text text-transparent">
            working while you sleep.
          </span>
        </h1>
        <p className="text-text-dim text-[17px] md:text-lg leading-relaxed my-6 max-w-[560px] mx-auto">
          Build AI employees that research, analyze, automate, and execute tasks — each one with its own
          knowledge, memory, and human oversight.
        </p>
        <div className="flex gap-3.5 justify-center flex-wrap mb-6">
          <Link
            to="/login"
            className="bg-gradient-to-br from-primary to-indigo-600 text-white font-semibold text-[14.5px] px-7 py-3.5 rounded-xl shadow-[0_10px_30px_rgba(99,102,241,0.4)]"
          >
            Start Building Free
          </Link>
          <a
            href="#product"
            className="bg-white/5 border border-border text-text font-semibold text-[14.5px] px-7 py-3.5 rounded-xl"
          >
            Watch Demo
          </a>
        </div>
      </div>

      <div className="relative z-10 max-w-[920px] mx-auto px-6 pb-28" id="product">
        <div className="text-center text-text-faint text-xs uppercase tracking-widest mb-5">
          Vynera Workspace
        </div>
        <div className="glass rounded-2xl p-8 grid md:grid-cols-2 gap-4 shadow-2xl">
          <div className="bg-bg/60 border border-border rounded-xl p-5">
            <div className="flex items-center gap-2.5 mb-3.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-sm">
                📊
              </div>
              <div className="font-semibold text-sm">Marketing AI</div>
            </div>
            <div className="text-[13px] text-text-dim mb-3">Analyzing competitors…</div>
            <span className="text-[11.5px] inline-flex items-center gap-1.5 bg-warn/10 text-warn px-2.5 py-1 rounded-full">
              Working
            </span>
          </div>
          <div className="bg-bg/60 border border-border rounded-xl p-5">
            <div className="flex items-center gap-2.5 mb-3.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-sm">
                🔬
              </div>
              <div className="font-semibold text-sm">Research AI</div>
            </div>
            <div className="text-[13px] text-text-dim mb-3">Generated 25 insights</div>
            <span className="text-[11.5px] inline-flex items-center gap-1.5 bg-success/10 text-success px-2.5 py-1 rounded-full">
              Done
            </span>
          </div>
        </div>
      </div>

      <div className="relative z-10 max-w-[1040px] mx-auto px-6 py-16" id="features">
        <div className="text-accent text-xs uppercase tracking-widest text-center mb-3.5">Why Vynera</div>
        <h2 className="font-display font-semibold text-3xl md:text-[38px] text-center tracking-tight mb-14">
          Your team never sleeps.
        </h2>

        {features.map((f, i) => (
          <div key={f.title} className={`flex flex-col md:flex-row items-center gap-10 mb-20 ${i % 2 ? 'md:flex-row-reverse' : ''}`}>
            <div className="flex-1">
              <h3 className="font-display font-semibold text-2xl mb-[18px]">{f.title}</h3>
              <ul className="flex flex-col gap-3">
                {f.items.map((item) => (
                  <li key={item} className="flex items-center gap-3 text-text-dim text-[15px]">
                    <span className="w-5 h-5 rounded-full bg-success/15 text-success flex items-center justify-center text-[11px] flex-shrink-0">
                      ✓
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex-1 w-full">
              <div className="glass rounded-2xl p-8 min-h-[220px] flex items-center justify-center text-[64px]">
                {f.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="relative z-10 flex justify-center gap-16 flex-wrap py-12 px-6 border-t border-b border-border text-text-dim text-[13.5px]">
        <span className="flex flex-col items-center gap-2">
          <span className="text-[22px]">🚀</span>Startups
        </span>
        <span className="flex flex-col items-center gap-2">
          <span className="text-[22px]">🏢</span>Businesses
        </span>
        <span className="flex flex-col items-center gap-2">
          <span className="text-[22px]">👨‍💻</span>Developers
        </span>
        <span className="flex flex-col items-center gap-2">
          <span className="text-[22px]">🎨</span>Creators
        </span>
      </div>

      <div className="relative z-10 max-w-[1040px] mx-auto px-6 py-20" id="pricing">
        <div className="text-accent text-xs uppercase tracking-widest text-center mb-3.5">Pricing</div>
        <h2 className="font-display font-semibold text-3xl md:text-[38px] text-center tracking-tight mb-14">
          Start free. Scale when ready.
        </h2>
        <div className="grid md:grid-cols-2 gap-5 max-w-[640px] mx-auto">
          <div className="glass rounded-2xl p-8">
            <div className="font-display font-semibold text-lg mb-1.5">Free</div>
            <div className="font-display font-bold text-[38px] mb-5">
              $0<span className="text-sm text-text-dim font-medium">/month</span>
            </div>
            <ul className="flex flex-col gap-2.5 mb-6 text-[13.5px] text-text-dim">
              <li>✓ 1 AI Employee</li>
              <li>✓ Basic tasks</li>
            </ul>
            <Link
              to="/login"
              className="block text-center w-full py-3 rounded-lg border border-border bg-white/5 font-semibold text-[13.5px]"
            >
              Get Started
            </Link>
          </div>
          <div className="glass rounded-2xl p-8 border-primary/50 relative bg-gradient-to-b from-primary/10">
            <span className="absolute -top-2.5 right-6 bg-primary text-white text-[10.5px] font-semibold px-2.5 py-0.5 rounded-full">
              Popular
            </span>
            <div className="font-display font-semibold text-lg mb-1.5">Pro</div>
            <div className="font-display font-bold text-[38px] mb-5">
              $20<span className="text-sm text-text-dim font-medium">/month</span>
            </div>
            <ul className="flex flex-col gap-2.5 mb-6 text-[13.5px] text-text-dim">
              <li>✓ Unlimited AI Employees</li>
              <li>✓ Advanced automation</li>
            </ul>
            <Link
              to="/login"
              className="block text-center w-full py-3 rounded-lg bg-gradient-to-br from-primary to-indigo-600 text-white font-semibold text-[13.5px]"
            >
              Upgrade to Pro
            </Link>
          </div>
        </div>
      </div>

      <div className="relative z-10 text-center py-24 px-6">
        <h2 className="font-display font-semibold text-3xl mb-6">Ready to build your AI workforce?</h2>
        <Link
          to="/login"
          className="inline-block bg-gradient-to-br from-primary to-indigo-600 text-white font-semibold text-[14.5px] px-7 py-3.5 rounded-xl"
        >
          Start Building Free
        </Link>
      </div>

      <footer className="relative z-10 text-center py-8 text-text-faint text-xs border-t border-border">
        © 2026 Vynera. Built for teams who want their AI working while they sleep.
      </footer>
    </div>
  )
}
