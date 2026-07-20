import { create } from 'zustand'
import type { Workspace } from './types'

interface WorkspaceState {
  current: Workspace | null
  setCurrent: (workspace: Workspace) => void
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  current: null,
  setCurrent: (workspace) => set({ current: workspace }),
}))
