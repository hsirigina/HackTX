import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import McLarenDashboard from './McLarenDashboard.jsx'
import DashboardLayout from './DashboardLayout.jsx'

// Switch between dashboards by commenting/uncommenting:
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <DashboardLayout />
    {/* <McLarenDashboard /> */}
    {/* <App /> */}
  </StrictMode>,
)
