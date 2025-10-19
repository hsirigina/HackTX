import { useState } from 'react'
import AgentDashboard from './AgentDashboard'
import RaceComparison from './RaceComparison'
import './DashboardLayout.css'

function DashboardLayout() {
  const [activeTab, setActiveTab] = useState('agents')

  return (
    <div className="dashboard-layout">
      {/* Navigation Tabs */}
      <div className="nav-tabs">
        <button 
          className={`nav-tab ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          <span className="tab-icon">🤖</span>
          <span className="tab-label">AGENT DASHBOARD</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'comparison' ? 'active' : ''}`}
          onClick={() => setActiveTab('comparison')}
        >
          <span className="tab-icon">🏁</span>
          <span className="tab-label">RACE COMPARISON</span>
        </button>
      </div>

      {/* Active View */}
      <div className="view-container">
        {activeTab === 'agents' && <AgentDashboard />}
        {activeTab === 'comparison' && <RaceComparison />}
      </div>
    </div>
  )
}

export default DashboardLayout

