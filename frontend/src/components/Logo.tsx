interface LogoProps {
  size?: number
  showNetwork?: boolean
}

export function Logo({ size = 24, showNetwork = true }: LogoProps) {
  const height = size * 0.9
  return (
    <svg width={size} height={height} viewBox="0 0 100 90" className="flex-shrink-0">
      <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#818CF8" />
          <stop offset="100%" stopColor="#22D3EE" />
        </linearGradient>
      </defs>
      {showNetwork && (
        <>
          <line x1="35" y1="46" x2="65" y2="46" stroke="#6366F1" strokeWidth="0.6" strokeOpacity="0.35" />
          <line x1="18" y1="18" x2="65" y2="46" stroke="#6366F1" strokeWidth="0.6" strokeOpacity="0.25" />
          <line x1="82" y1="18" x2="35" y2="46" stroke="#22D3EE" strokeWidth="0.6" strokeOpacity="0.25" />
        </>
      )}
      <path
        d="M18,18 L35,46 L47,64 A7,7 0 1,1 53,64 L65,46 L82,18"
        fill="none"
        stroke="url(#logoGrad)"
        strokeWidth="7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {showNetwork && (
        <>
          <circle cx="18" cy="18" r="3.5" fill="#818CF8" />
          <circle cx="82" cy="18" r="3.5" fill="#22D3EE" />
          <circle cx="35" cy="46" r="2.6" fill="#818CF8" />
          <circle cx="65" cy="46" r="2.6" fill="#22D3EE" />
        </>
      )}
    </svg>
  )
}
