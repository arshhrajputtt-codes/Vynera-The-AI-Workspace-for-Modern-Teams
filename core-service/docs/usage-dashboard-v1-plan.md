# Usage Dashboard — v1 Plan

## Goal
Give a workspace admin a single screen answering: "how much are we using
Nexora, and what is it costing us?"

## Data source
Entirely powered by `usage_events` (one row per LLM call — chat completion
or embedding), already written by:
- `ChatService.stream_reply` — one event per assistant reply
- `ApprovalService.create_draft` — one event per generated draft

Both go through `UsageRepository`, which already exposes:
- `summarize_for_workspace(workspace_id, since, until)` → totals
- `summarize_by_employee(workspace_id)` → per-employee breakdown

Both are exposed today via `GET /workspaces/{id}/analytics/usage` and
`GET /workspaces/{id}/analytics/usage/by-employee`.

## v1 screen layout
1. **Top strip — 4 numbers, current billing period:**
   messages sent, total tokens (input+output split on hover), estimated
   cost (USD), active employees.
2. **Time-series chart:** daily message count + daily cost, last 30 days.
   Needs one new query: `usage_events` grouped by `date_trunc('day',
   created_at)` — not built yet, straightforward addition to
   `UsageRepository` when the frontend needs it.
3. **Per-employee table:** sourced directly from `/usage/by-employee` —
   employee name (join against `core-service`'s own `employees` table),
   message count, tokens, cost. Sortable by cost descending by default,
   since that's the number admins actually act on.
4. **Approval funnel (ties Module 6 into the same screen):** pending /
   approved / rejected counts for the period, from `approvals` grouped by
   `status`. Not built yet — same shape of query as the daily chart above.

## Explicitly out of scope for v1
- Per-user (as opposed to per-employee) cost breakdown — needs a decision
  on whether individual usage is something admins should see, which is a
  product/privacy call, not an engineering one.
- Budget alerts / spend caps — needs a notification channel (email?
  in-app?) that doesn't exist yet.
- Real provider billing reconciliation — v1 cost is an *estimate* from the
  static rate table in `usage_event.py`. Fine for relative comparisons
  (which employee is expensive) but will drift from the actual invoice;
  revisit once real spend is non-trivial.

## Why usage_events and not deriving from messages/approvals directly
Messages and approvals get edited/deleted independently of billing history
(e.g. Module 6 could later let admins purge old drafts). Usage events are
written once, never mutated, and are the only table this dashboard should
ever read from — keeps the cost numbers stable even if conversation data
changes shape later.
