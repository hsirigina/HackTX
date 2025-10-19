import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import AgentDashboard from './AgentDashboard.jsx'
import McLarenDashboard from './McLarenDashboard.jsx'
import LiveSim from './LiveSim.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AgentDashboard />} />
        <Route path="/monitor" element={<McLarenDashboard />} />
        <Route path="/livesim" element={<LiveSim />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
