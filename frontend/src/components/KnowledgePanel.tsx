import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, ApiError } from '../lib/api'

interface KnowledgePanelProps {
  workspaceId: number
  employeeId: number
}

const statusStyles: Record<string, string> = {
  ready: 'bg-success/10 text-success',
  processing: 'bg-warn/10 text-warn',
  pending: 'bg-white/5 text-text-dim',
  failed: 'bg-red-500/10 text-red-400',
}

export function KnowledgePanel({ workspaceId, employeeId }: KnowledgePanelProps) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', workspaceId, employeeId],
    queryFn: () => api.listDocuments(workspaceId, employeeId),
    refetchInterval: (query) => {
      const docs = query.state.data
      const stillWorking = docs?.some((d) => d.status === 'pending' || d.status === 'processing')
      return stillWorking ? 2000 : false
    },
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadDocument(workspaceId, employeeId, file),
    onSuccess: () => {
      setUploadError(null)
      queryClient.invalidateQueries({ queryKey: ['documents', workspaceId, employeeId] })
    },
    onError: (err) => {
      setUploadError(err instanceof ApiError ? err.message : 'Upload failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (documentId: number) => api.deleteDocument(workspaceId, employeeId, documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', workspaceId, employeeId] })
    },
  })

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) uploadMutation.mutate(file)
    e.target.value = ''
  }

  return (
    <div className="w-[260px] p-6 border-l border-border overflow-y-auto">
      <div className="text-xs uppercase tracking-wider text-text-faint mb-3">Knowledge Base</div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx"
        onChange={handleFileSelect}
        className="hidden"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploadMutation.isPending}
        className="w-full border-[1.5px] border-dashed border-border rounded-lg py-3 text-xs text-text-dim hover:border-primary hover:text-primary-soft transition-colors disabled:opacity-60 mb-3"
      >
        {uploadMutation.isPending ? 'Uploading…' : '+ Upload PDF or DOCX'}
      </button>

      {uploadError && <p className="text-[11px] text-red-400 mb-3">{uploadError}</p>}

      {isLoading && <p className="text-[11px] text-text-faint">Loading…</p>}

      {documents?.length === 0 && !isLoading && (
        <p className="text-[11px] text-text-faint">
          No documents yet — upload one so this employee can cite real sources.
        </p>
      )}

      <div className="flex flex-col gap-2">
        {documents?.map((doc) => (
          <div key={doc.id} className="glass rounded-lg p-3 text-xs">
            <div className="flex items-start justify-between gap-2">
              <span className="font-medium break-all">{doc.filename}</span>
              <button
                onClick={() => deleteMutation.mutate(doc.id)}
                className="text-text-faint hover:text-red-400 flex-shrink-0"
                aria-label="Delete document"
              >
                ×
              </button>
            </div>
            <span
              className={`inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full ${
                statusStyles[doc.status] ?? statusStyles.pending
              }`}
            >
              {doc.status}
            </span>
            {doc.status === 'failed' && doc.error_message && (
              <p className="text-[10px] text-red-400 mt-1.5">{doc.error_message}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}