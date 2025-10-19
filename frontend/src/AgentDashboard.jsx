import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './AgentDashboard.css'
import TireModal from './TireModal'
import LaptimeModal from './LaptimeModal'
import PositionModal from './PositionModal'

const API_BASE_URL = 'http://localhost:8000'
const SESSION_ID = 'race-session-' + Date.now()

function AgentDashboard() {
  const navigate = useNavigate()
  const [scenarios, setScenarios] = useState([])
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0)
  const [currentLap, setCurrentLap] = useState(1)
  const [events, setEvents] = useState([])
  const [apiCalls, setApiCalls] = useState(0)
  const [touchStart, setTouchStart] = useState(0)
  const [touchEnd, setTouchEnd] = useState(0)
  const [isSliding, setIsSliding] = useState(false)
  const [raceState, setRaceState] = useState({
    position: 3,
    tireCompound: 'SOFT',
    tireAge: 0,
    drivingStyle: 'BALANCED',
    totalRaceTime: 0,
    pitStops: 0
  })
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [raceFinished, setRaceFinished] = useState(false)
  const [finalResults, setFinalResults] = useState(null)
  const [isTireModalOpen, setIsTireModalOpen] = useState(false)
  const [isLaptimeModalOpen, setIsLaptimeModalOpen] = useState(false)
  const [isPositionModalOpen, setIsPositionModalOpen] = useState(false)

  // Start race and fetch backend data
  useEffect(() => {
    startRace()
  }, [])

  const startRace = async () => {
    setInitialLoading(true)
    const startTime = Date.now()

    try {
      const response = await fetch(`${API_BASE_URL}/api/race/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: SESSION_ID,
          race_year: 2024,
          race_name: 'Bahrain',
          total_laps: 57,
          starting_position: 3,
          starting_compound: 'SOFT'
        })
      })

      const data = await response.json()
      console.log('Race started:', data)

      setCurrentLap(data.currentLap)
      setScenarios(data.strategies)
      setRaceState(data.state)
      setApiCalls(1)

      // Add initial event
      setEvents([{
        lap_number: data.currentLap,
        recommendation_type: 'RACE START',
        reasoning: `Starting from P${data.state.position} on ${data.state.tireCompound} tires`
      }])

      // Ensure minimum 5 seconds of loading
      const elapsedTime = Date.now() - startTime
      const remainingTime = Math.max(0, 5000 - elapsedTime)

      setTimeout(() => {
        setInitialLoading(false)
      }, remainingTime)
    } catch (error) {
      console.error('Failed to start race:', error)

      // Still wait minimum 5 seconds even on error
      const elapsedTime = Date.now() - startTime
      const remainingTime = Math.max(0, 5000 - elapsedTime)

      setTimeout(() => {
        alert('Failed to connect to backend API. Make sure the backend is running on port 8000. Error: ' + error.message)
        setInitialLoading(false)
      }, remainingTime)
    }
  }

  // Parse agent insights from race state
  const parseInsights = () => {
    const avgLapTime = raceState.totalRaceTime / Math.max(currentLap, 1)

    return {
      tire: {
        compound: raceState.tireCompound || 'SOFT',
        tire_age: raceState.tireAge || 0,
        degradation: '+0.0',
        status: 'active',
        triggers: raceState.tireAge > 20 ? [
          { message: `High tire wear (${raceState.tireAge} laps)`, urgency: 'HIGH' }
        ] : raceState.tireAge > 15 ? [
          { message: `Tire degradation increasing`, urgency: 'MEDIUM' }
        ] : []
      },
      laptime: {
        current_time: avgLapTime.toFixed(3),
        avg_time: avgLapTime.toFixed(3),
        trend: raceState.drivingStyle,
        status: 'active',
        triggers: []
      },
      position: {
        position: raceState.position || 3,
        gap_ahead: '+0.5',
        gap_behind: '-1.2',
        status: 'active',
        triggers: []
      },
      competitor: {
        threats: 0,
        pit_status: raceState.pitStops > 0 ? `${raceState.pitStops} STOPS` : 'NO STOPS',
        status: 'active',
        triggers: []
      }
    }
  }

  const insights = parseInsights()

  // Handle strategy selection and progress race
  const handleScenarioSelect = async (scenario) => {
    if (loading) return

    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/race/decision`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: SESSION_ID,
          option_id: scenario.id
        })
      })

      const data = await response.json()
      console.log('Decision result:', data)

      setApiCalls(apiCalls + 1)

      // Add event to timeline
      setEvents(prev => [{
        lap_number: currentLap,
        recommendation_type: scenario.title,
        reasoning: scenario.description
      }, ...prev.slice(0, 4)])

      // Update race state
      if (data.raceFinished) {
        setRaceFinished(true)
        setCurrentLap(57)
        setScenarios([])
        setFinalResults(data.finalResults)
        setEvents(prev => [{
          lap_number: 57,
          recommendation_type: 'RACE FINISHED',
          reasoning: 'Race completed!'
        }, ...prev])
      } else {
        setCurrentLap(data.currentLap)
        setScenarios(data.strategies)
        setRaceState(data.state)
        setCurrentScenarioIndex(0)
      }

      setLoading(false)
    } catch (error) {
      console.error('Failed to make decision:', error)
      setLoading(false)
    }
  }

  // Swipe handlers
  const handleTouchStart = (e) => {
    setTouchStart(e.targetTouches[0].clientX)
  }

  const handleTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return

    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > 50
    const isRightSwipe = distance < -50

    if (isLeftSwipe && currentScenarioIndex < scenarios.length - 1) {
      goToNextScenario()
    }
    if (isRightSwipe && currentScenarioIndex > 0) {
      goToPrevScenario()
    }

    setTouchStart(0)
    setTouchEnd(0)
  }

  const goToPrevScenario = () => {
    if (currentScenarioIndex > 0 && !isSliding) {
      setIsSliding(true)
      setCurrentScenarioIndex(currentScenarioIndex - 1)
      setTimeout(() => {
        setIsSliding(false)
      }, 400)
    }
  }

  const goToNextScenario = () => {
    if (currentScenarioIndex < scenarios.length - 1 && !isSliding) {
      setIsSliding(true)
      setCurrentScenarioIndex(currentScenarioIndex + 1)
      setTimeout(() => {
        setIsSliding(false)
      }, 400)
    }
  }

  if (initialLoading) {
    return (
      <div className="loading-road-container">
        {/* Road */}
        <div className="road">
          {/* Animated lane divider lines */}
          <div className="road-lines">
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
            <div className="road-line"></div>
          </div>
          {/* Car moving lane to lane */}
          <div className="loading-car-wrapper">
            <img src="/samller2.png" alt="Racing car" className="loading-car-image" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="agent-dashboard">
      {/* Top Header */}
      <div className="dash-header">
        <div className="header-left">F1 MULTI-AGENT STRATEGY SYSTEM V2</div>
        <div className="header-right">4 DATA AGENTS + AI COORDINATOR</div>
      </div>

      {/* Main Content Grid */}
      <div className="dash-main">
        {/* Left Column - Tire & LapTime Agents */}
        <div className="agents-column">
          {/* Tire Data Agent */}
          <div className="agent-card" onClick={() => setIsTireModalOpen(true)} style={{cursor: 'pointer'}}>
            <div className="agent-header">
              <div className="agent-icon">🛞</div>
              <div className="agent-name">TIRE DATA AGENT</div>
              <div className={`agent-status ${insights.tire.status || 'active'}`}>
                {insights.tire.status || 'ACTIVE'}
              </div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">COMPOUND</span>
                <span className="metric-value">{insights.tire.compound || 'HARD'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">TIRE AGE</span>
                <span className="metric-value">{insights.tire.tire_age || '0'} laps</span>
              </div>
              <div className="metric">
                <span className="metric-label">DEGRADATION</span>
                <span className="metric-value">{insights.tire.degradation || '+0.0'}s</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.tire.triggers?.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message || trigger}
                  </div>
                )) || <div className="trigger low">No active triggers</div>}
              </div>
            </div>
          </div>

          {/* LapTime Agent */}
          <div className="agent-card" onClick={() => setIsLaptimeModalOpen(true)} style={{ cursor: 'pointer' }}>
            <div className="agent-header">
              <div className="agent-icon">⏱️</div>
              <div className="agent-name">LAPTIME AGENT</div>
              <div className={`agent-status ${insights.laptime.status || 'active'}`}>
                {insights.laptime.status || 'ACTIVE'}
              </div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">CURRENT LAP</span>
                <span className="metric-value">{insights.laptime.current_time || '1:22.5'}s</span>
              </div>
              <div className="metric">
                <span className="metric-label">AVG (5 LAPS)</span>
                <span className="metric-value">{insights.laptime.avg_time || '1:22.8'}s</span>
              </div>
              <div className="metric">
                <span className="metric-label">TREND</span>
                <span className="metric-value">{insights.laptime.trend || 'STABLE'}</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.laptime.triggers?.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message || trigger}
                  </div>
                )) || <div className="trigger low">Pace stable</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Center Column - AI Coordinator */}
        <div className="coordinator-column">
          <div className="coordinator-header">
            <div className="coord-title">AI COORDINATOR</div>
            <div className="coord-model">Gemini 2.0 Flash</div>
            <button
              className="live-sim-button"
              onClick={() => navigate('/livesim')}
              style={{
                marginLeft: 'auto',
                padding: '8px 16px',
                backgroundColor: '#ff1e00',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#cc1800'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#ff1e00'}
            >
              🎮 Live Sim
            </button>
          </div>

          <div className="lap-display">
            <div className="lap-label">CURRENT LAP</div>
            <div className="lap-number">{currentLap || '--'}<span>/57</span></div>
          </div>

          {/* Swipable Scenario Carousel OR Final Results */}
          {raceFinished ? (
            <div className="final-results-container">
              {finalResults && (
                <div className="race-performance-section">
                  <div className="section-header">🏆 YOUR RACE PERFORMANCE</div>
                  <div className="performance-grid">
                    <div className="perf-stat">
                      <span className="perf-label">Your time:</span>
                      <span className="perf-value">{finalResults.user_time.toFixed(1)}s</span>
                    </div>
                    <div className="perf-stat">
                      <span className="perf-label">Winner's time:</span>
                      <span className="perf-value">{finalResults.full_leaderboard[0].time.toFixed(1)}s</span>
                    </div>
                    <div className="perf-stat">
                      <span className="perf-label">Gap to winner:</span>
                      <span className="perf-value highlight">+{finalResults.gap_to_winner.toFixed(1)}s</span>
                    </div>
                    <div className="perf-stat">
                      <span className="perf-label">Final position:</span>
                      <span className="perf-value highlight">P{finalResults.leaderboard_position} / {finalResults.total_drivers}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="scenario-carousel"
                 onTouchStart={handleTouchStart}
                 onTouchMove={handleTouchMove}
                 onTouchEnd={handleTouchEnd}>

              {/* Navigation Arrows */}
              <button
                className="carousel-arrow left"
                onClick={goToPrevScenario}
                disabled={currentScenarioIndex === 0}
                aria-label="Previous scenario">
                ←
              </button>
              <button
                className="carousel-arrow right"
                onClick={goToNextScenario}
                disabled={currentScenarioIndex === scenarios.length - 1}
                aria-label="Next scenario">
                →
              </button>

              <div className="carousel-track">
                {scenarios.length > 0 ? (
                  <div
                    className="carousel-inner"
                    style={{
                      transform: `translateX(-${currentScenarioIndex * 100}%)`,
                      transition: isSliding ? 'transform 0.4s ease-in-out' : 'none'
                    }}
                  >
                    {scenarios.map((scenario, index) => (
                      <div
                        key={index}
                        className="recommendation-box"
                        onClick={() => handleScenarioSelect(scenario)}
                        style={{ cursor: 'pointer' }}
                      >
                        <div className="rec-header">
                          <span className="rec-label">
                            {scenario.option}
                          </span>
                          <span className={`rec-urgency ${scenario.confidence?.toLowerCase() || 'recommended'}`}>
                            {scenario.confidence || 'RECOMMENDED'}
                          </span>
                        </div>

                        <div className="rec-type">{scenario.title}</div>
                        <div className="rec-message">{scenario.description}</div>
                        <div className="rec-reasoning">{scenario.reasoning}</div>

                        <div className="rec-meta">
                          <div className="rec-metrics">
                            <div className="metric-item">
                              <span>Race Impact:</span>
                              <span>{scenario.raceTimeImpact}</span>
                            </div>
                            <div className="metric-item">
                              <span>Lap Impact:</span>
                              <span>{scenario.lapTimeImpact}</span>
                            </div>
                            <div className="metric-item">
                              <span>Tire Wear:</span>
                              <span>{scenario.tireWear}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="recommendation-box">
                    <div className="rec-empty">Waiting for scenarios...</div>
                  </div>
                )}
              </div>

              {/* Scenario Indicators */}
              {scenarios.length > 1 && (
                <div className="scenario-indicators">
                  {scenarios.map((_, index) => (
                    <div
                      key={index}
                      className={`indicator-dot ${index === currentScenarioIndex ? 'active' : ''}`}
                      onClick={() => setCurrentScenarioIndex(index)}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="event-feed">
            <div className="feed-title">RECENT EVENTS</div>
            <div className="feed-list">
              {events.length > 0 ? events.map((event, i) => (
                <div key={i} className="event-item">
                  <span className="event-time">Lap {event.lap_number}</span>
                  <span className="event-text">{event.recommendation_type || event.reasoning?.substring(0, 50)}</span>
                </div>
              )) : (
                <div className="event-item">
                  <span className="event-text">No recent events</span>
                </div>
              )}
            </div>
          </div>

          <div className="api-efficiency">
            <div className="efficiency-title">API EFFICIENCY</div>
            <div className="efficiency-stats">
              <div className="stat-box">
                <div className="stat-num">{apiCalls}</div>
                <div className="stat-label">API Calls</div>
              </div>
              <div className="stat-box">
                <div className="stat-num">{currentLap || 0}</div>
                <div className="stat-label">Laps Analyzed</div>
              </div>
              <div className="stat-box">
                <div className="stat-num">{Math.round((1 - (apiCalls / (currentLap || 1))) * 100)}%</div>
                <div className="stat-label">Cost Saved</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Position & Competitor Agents */}
        <div className="agents-column">
          {/* Position Agent */}
          <div className="agent-card" onClick={() => setIsPositionModalOpen(true)} style={{ cursor: 'pointer' }}>
            <div className="agent-header">
              <div className="agent-icon">🏁</div>
              <div className="agent-name">POSITION AGENT</div>
              <div className={`agent-status ${insights.position.status || 'active'}`}>
                {insights.position.status || 'ACTIVE'}
              </div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">POSITION</span>
                <span className="metric-value">P{insights.position.position || '1'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">GAP AHEAD</span>
                <span className="metric-value">{insights.position.gap_ahead || '+0.0'}s</span>
              </div>
              <div className="metric">
                <span className="metric-label">GAP BEHIND</span>
                <span className="metric-value">{insights.position.gap_behind || '+0.0'}s</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.position.triggers?.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message || trigger}
                  </div>
                )) || <div className="trigger low">Position stable</div>}
              </div>
            </div>
          </div>

          {/* Competitor Agent */}
          <div className="agent-card">
            <div className="agent-header">
              <div className="agent-icon">🎯</div>
              <div className="agent-name">COMPETITOR AGENT</div>
              <div className={`agent-status ${insights.competitor.status || 'active'}`}>
                {insights.competitor.status || 'ACTIVE'}
              </div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">MONITORING</span>
                <span className="metric-value">P±2</span>
              </div>
              <div className="metric">
                <span className="metric-label">THREATS</span>
                <span className="metric-value">{insights.competitor.threats || '0'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">PIT STATUS</span>
                <span className="metric-value">{insights.competitor.pit_status || 'NONE'}</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.competitor.triggers?.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message || trigger}
                  </div>
                )) || <div className="trigger low">No threats detected</div>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dash-footer">
        <div className="footer-right">
          <span>RACE: Bahrain 2024 • POSITION: P{raceState.position} • TIRES: {raceState.tireCompound} ({raceState.tireAge} laps) • STYLE: {raceState.drivingStyle}</span>
        </div>
      </div>

      {/* Tire Modal */}
      <TireModal
        isOpen={isTireModalOpen}
        onClose={() => setIsTireModalOpen(false)}
        tireData={{
          compound: raceState.tireCompound,
          age: raceState.tireAge,
          degradation: insights?.tire?.degradation
        }}
      />

      {/* Laptime Modal */}
      <LaptimeModal
        isOpen={isLaptimeModalOpen}
        onClose={() => setIsLaptimeModalOpen(false)}
        laptimeData={{
          current_time: insights?.laptime?.current_time,
          avg_time: insights?.laptime?.avg_time,
          trend: insights?.laptime?.trend
        }}
      />

      {/* Position Modal */}
      <PositionModal
        isOpen={isPositionModalOpen}
        onClose={() => setIsPositionModalOpen(false)}
        positionData={{
          position: insights?.position?.position,
          gap_ahead: insights?.position?.gap_ahead,
          gap_behind: insights?.position?.gap_behind
        }}
        currentLap={currentLap}
      />
    </div>
  )
}

export default AgentDashboard
