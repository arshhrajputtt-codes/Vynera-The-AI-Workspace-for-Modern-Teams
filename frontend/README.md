# Vynera frontend

React + Vite + TypeScript + Tailwind, wired to `identity-service` (port 8000) and `core-service` (port 8001).

## Setup

```
npm install
copy .env.example .env
npm run dev
```

Opens on http://localhost:5173. Both backend services need to be running (same as during backend testing) — this won't work standalone.

## What's real vs. what's still mock

- **Landing, Login, Dashboard, Workspace, Create Employee, Chat** — fully wired to the real APIs, no mock data.
- **Approvals and Analytics pages** — not built yet. The API client (`src/lib/api.ts`) already has every function needed (`createDraft`, `listApprovals`, `approveApproval`, `rejectApproval`, `getUsageSummary`, `getUsageByEmployee`) — just no page UI consuming them yet.
- **Document upload UI** — same situation: `api.uploadDocument` exists and works, no page wires it in yet.
- **Employee creation form** uses the real backend fields (name, description, system prompt, model, temperature) — not the mockup's Personality/Capabilities fields, which don't exist in the API.

## Known rough edges

- No loading skeletons — just plain "Loading…" text in a couple of spots.
- No toast notifications — errors show as inline red text under forms.
- Chat doesn't load previous conversation history when reopening an employee (starts fresh each time you navigate to `/app/chat/:employeeId`). The API for it exists (`getConversationHistory`) — just not called on mount yet.
- Mobile responsiveness is inherited from Tailwind's defaults, not deliberately tuned screen-by-screen like the HTML mockup was.

None of this was tested against a live `npm install` — no network access in the environment that built this. First real test is on your machine.
