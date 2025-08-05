// src/App.tsx
import { useRoutes } from "react-router-dom"
import { AppRoutes } from "./routes"
import { ChatProvider } from "./contexts/ChatContext"
import { AuthProvider } from "./contexts/AuthContext"

function App() {
  const routing = useRoutes(AppRoutes)

  return (
    <AuthProvider>
      <ChatProvider>
        {routing}
      </ChatProvider>
    </AuthProvider>
  )
}

export default App
