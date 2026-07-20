import { Routes, Route } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AppShell } from './components/AppShell'
import { Landing } from './pages/Landing'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { WorkspacePage } from './pages/Workspace'
import { CreateEmployee } from './pages/CreateEmployee'
import { Chat } from './pages/Chat'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="workspace" element={<WorkspacePage />} />
          <Route path="workspace/employees/new" element={<CreateEmployee />} />
          <Route path="chat/:employeeId" element={<Chat />} />
        </Route>
      </Route>
    </Routes>
  )
}
