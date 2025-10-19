import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './AgentDashboard.css'

const API_BASE_URL = 'http://localhost:8000'
const SESSION_ID = 'live-sim-' + Date.now()

function LiveSim() {
  const navigate = useNavigate()
  const [currentLap, setCurrentLap] = useState(null)
  const [scenarios, setScenarios] = useState([])
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0)
  const [events, setEvents] = useState([])
  const [apiCalls, setApiCalls] = useState(0)
  const [raceState, setRaceState] = useState({
    position: 3,
    tireCompound: 'SOFT',
    tireAge: 0,
    drivingStyle: 'BALANCED',
    totalRaceTime: 0,
    pitStops: 0
  })
  const [loading, setLoading] = useState(false)
  const [raceStarted, setRaceStarted] = useState(false)
  const [raceFinished, setRaceFinished] = useState(false)
  const [finalResults, setFinalResults] = useState(null)

  // Race selection state
  const [showSelection, setShowSelection] = useState(true)
  const [availableRaces, setAvailableRaces] = useState([])
  const [selectedRace, setSelectedRace] = useState(null)
  const [selectedPosition, setSelectedPosition] = useState(3)
  const [selectedTire, setSelectedTire] = useState('SOFT')
  const [selectedDriver, setSelectedDriver] = useState('VER')
  const [loadingRaces, setLoadingRaces] = useState(true)

  // Swipe state
  const [touchStart, setTouchStart] = useState(0)
  const [touchEnd, setTouchEnd] = useState(0)
  const [isSliding, setIsSliding] = useState(false)

  // Load available races on mount
  useEffect(() => {
    loadAvailableRaces()
  }, [])

  const loadAvailableRaces = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/races/available`)
      const data = await response.json()
      if (data.success) {
        setAvailableRaces(data.data.races)
        // Set Bahrain as default
        const bahrain = data.data.races.find(r => r.id === 'bahrain')
        setSelectedRace(bahrain || data.data.races[0])
      }
      setLoadingRaces(false)
    } catch (error) {
      console.error('Failed to load races:', error)
      setLoadingRaces(false)
    }
  }

  // Start the race simulation
  const startRace = async () => {
    if (!selectedRace) return

    setLoading(true)
    setShowSelection(false)
    try {
      const response = await fetch(`${API_BASE_URL}/api/race/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: SESSION_ID,
          race_year: 2024,
          race_name: selectedRace.id,
          comparison_driver: selectedDriver,
          starting_position: selectedPosition,
          starting_compound: selectedTire
        })
      })

      const data = await response.json()
      console.log('Race started:', data)

      setCurrentLap(data.currentLap)
      setScenarios(data.strategies)
      setRaceState(data.state)
      setApiCalls(1)
      setRaceStarted(true)

      // Update selected race with actual total laps from backend if available
      if (data.totalLaps && selectedRace) {
        setSelectedRace({...selectedRace, laps: data.totalLaps})
      }

      // Add initial event
      setEvents([{
        lap_number: data.currentLap,
        recommendation_type: 'RACE START',
        reasoning: `Starting from P${data.state.position} on ${data.state.tireCompound} tires`
      }])

      setLoading(false)
    } catch (error) {
      console.error('Failed to start race:', error)
      alert('Failed to connect to backend API. Make sure the backend is running on port 8000.')
      setLoading(false)
    }
  }

  // Handle decision selection
  const handleScenarioSelect = async (scenario) => {
    if (loading) return

    try {
      setLoading(true)

      // Add event for decision made
      setEvents(prev => [{
        lap_number: currentLap,
        recommendation_type: scenario.title,
        reasoning: scenario.description
      }, ...prev.slice(0, 4)])

      // Clear current scenarios while processing
      setScenarios([])

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

      // If race finished
      if (data.raceFinished) {
        setRaceFinished(true)
        setCurrentLap(data.currentLap || 57)
        setScenarios([])
        setFinalResults(data.finalResults)
        setRaceState(data.state)
        setEvents(prev => [{
          lap_number: data.currentLap || 57,
          recommendation_type: 'RACE FINISHED',
          reasoning: 'Race completed!'
        }, ...prev])
      } else {
        // Update state immediately - no lap-by-lap animation
        // (position data only exists at decision points, not per-lap)
        setCurrentLap(data.currentLap)
        setScenarios(data.strategies)
        setRaceState(data.state)
        setCurrentScenarioIndex(0)
        setLoading(false)
      }

      if (data.raceFinished) {
        setLoading(false)
      }
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

  // Parse agent insights from race state
  const parseInsights = () => {
    const avgLapTime = raceState.totalRaceTime / Math.max(currentLap || 1, 1)

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
        gap_ahead: raceState.gapAhead || '--',
        gap_behind: raceState.gapBehind || '--',
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

  const insights = raceStarted ? parseInsights() : {
    tire: { compound: '--', tire_age: 0, degradation: '--', status: 'active', triggers: [] },
    laptime: { current_time: '--', avg_time: '--', trend: '--', status: 'active', triggers: [] },
    position: { position: '--', gap_ahead: '--', gap_behind: '--', status: 'active', triggers: [] },
    competitor: { threats: 0, pit_status: '--', status: 'active', triggers: [] }
  }

  return (
    <div className="agent-dashboard">
      {/* Top Header */}
      <div className="dash-header">
        <div className="header-left">LIVE SIMULATION MODE</div>
        <div className="header-right">REAL-TIME RACE MONITORING</div>
      </div>

      {/* Main Content Grid */}
      <div className="dash-main">
        {/* Left Column - Placeholder Agents */}
        <div className="agents-column">
          {/* Tire Data Agent */}
          <div className="agent-card">
            <div className="agent-header">
              <div className="agent-icon">🛞</div>
              <div className="agent-name">TIRE DATA AGENT</div>
              <div className="agent-status active">ACTIVE</div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">COMPOUND</span>
                <span className="metric-value">{insights.tire.compound}</span>
              </div>
              <div className="metric">
                <span className="metric-label">TIRE AGE</span>
                <span className="metric-value">{insights.tire.tire_age} laps</span>
              </div>
              <div className="metric">
                <span className="metric-label">DEGRADATION</span>
                <span className="metric-value">{insights.tire.degradation}</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.tire.triggers.length > 0 ? insights.tire.triggers.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message}
                  </div>
                )) : <div className="trigger low">{raceStarted ? 'Tires in good condition' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>

          {/* LapTime Agent */}
          <div className="agent-card">
            <div className="agent-header">
              <div className="agent-icon">⏱️</div>
              <div className="agent-name">LAPTIME AGENT</div>
              <div className="agent-status active">ACTIVE</div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">CURRENT LAP</span>
                <span className="metric-value">{insights.laptime.current_time}s</span>
              </div>
              <div className="metric">
                <span className="metric-label">AVG (5 LAPS)</span>
                <span className="metric-value">{insights.laptime.avg_time}s</span>
              </div>
              <div className="metric">
                <span className="metric-label">TREND</span>
                <span className="metric-value">{insights.laptime.trend}</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.laptime.triggers.length > 0 ? insights.laptime.triggers.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message}
                  </div>
                )) : <div className="trigger low">{raceStarted ? 'Pace stable' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Center Column - Live Sim Info */}
        <div className="coordinator-column">
          <div className="coordinator-header">
            <div className="coord-title">LIVE SIM COORDINATOR</div>
            <div className="coord-model">Real-time Mode</div>
            <button
              className="back-button"
              onClick={() => navigate('/')}
              style={{
                marginLeft: 'auto',
                padding: '8px 16px',
                backgroundColor: '#667788',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#556677'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#667788'}
            >
              ← Back
            </button>
          </div>

          <div className="lap-display">
            <div className="lap-label">CURRENT LAP</div>
            <div className="lap-number">{currentLap || '--'}<span>/{selectedRace?.laps || '--'}</span></div>
          </div>

          {/* Main content area */}
          {!raceStarted ? (
            showSelection ? (
              /* Race Selection Screen */
              <div style={{ padding: '20px' }}>
                <div style={{
                  textAlign: 'center',
                  marginBottom: '30px'
                }}>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>
                    🏎️ Race Configuration
                  </div>
                  <div style={{ fontSize: '16px', color: '#889aab' }}>
                    Select your race parameters
                  </div>
                </div>

                {loadingRaces ? (
                  <div style={{ textAlign: 'center', color: '#889aab', padding: '40px' }}>
                    Loading races...
                  </div>
                ) : (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '20px',
                    marginBottom: '30px'
                  }}>
                    {/* Race Selection */}
                    <div style={{
                      backgroundColor: '#1a2332',
                      padding: '20px',
                      borderRadius: '8px',
                      border: '2px solid #2d3748'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#889aab', marginBottom: '12px' }}>
                        🏁 RACE
                      </div>
                      <select
                        value={selectedRace?.id || ''}
                        onChange={(e) => setSelectedRace(availableRaces.find(r => r.id === e.target.value))}
                        style={{
                          width: '100%',
                          padding: '12px',
                          fontSize: '16px',
                          backgroundColor: '#0d1117',
                          color: '#fff',
                          border: '1px solid #2d3748',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        {availableRaces.map(race => (
                          <option key={race.id} value={race.id}>
                            {race.name} ({race.laps} laps)
                          </option>
                        ))}
                      </select>
                      {selectedRace && (
                        <div style={{ marginTop: '8px', fontSize: '12px', color: '#667788' }}>
                          📍 {selectedRace.country}
                        </div>
                      )}
                    </div>

                    {/* Starting Position */}
                    <div style={{
                      backgroundColor: '#1a2332',
                      padding: '20px',
                      borderRadius: '8px',
                      border: '2px solid #2d3748'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#889aab', marginBottom: '12px' }}>
                        🎯 STARTING POSITION
                      </div>
                      <select
                        value={selectedPosition}
                        onChange={(e) => setSelectedPosition(parseInt(e.target.value))}
                        style={{
                          width: '100%',
                          padding: '12px',
                          fontSize: '16px',
                          backgroundColor: '#0d1117',
                          color: '#fff',
                          border: '1px solid #2d3748',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        {Array.from({length: 20}, (_, i) => i + 1).map(pos => (
                          <option key={pos} value={pos}>P{pos}</option>
                        ))}
                      </select>
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#667788' }}>
                        Grid position at race start
                      </div>
                    </div>

                    {/* Tire Compound */}
                    <div style={{
                      backgroundColor: '#1a2332',
                      padding: '20px',
                      borderRadius: '8px',
                      border: '2px solid #2d3748'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#889aab', marginBottom: '12px' }}>
                        🛞 STARTING TIRE
                      </div>
                      <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
                        {['SOFT', 'MEDIUM', 'HARD'].map(compound => (
                          <button
                            key={compound}
                            onClick={() => setSelectedTire(compound)}
                            style={{
                              padding: '12px',
                              fontSize: '14px',
                              fontWeight: 'bold',
                              backgroundColor: selectedTire === compound ? '#ff1e00' : '#0d1117',
                              color: '#fff',
                              border: selectedTire === compound ? '2px solid #ff1e00' : '1px solid #2d3748',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between'
                            }}
                          >
                            <span>{compound === 'SOFT' ? '🔴' : compound === 'MEDIUM' ? '🟡' : '⚪'} {compound}</span>
                            <span style={{ fontSize: '11px', color: '#889aab' }}>
                              {compound === 'SOFT' ? 'Fast/Fragile' : compound === 'MEDIUM' ? 'Balanced' : 'Durable/Slow'}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Comparison Driver */}
                    <div style={{
                      backgroundColor: '#1a2332',
                      padding: '20px',
                      borderRadius: '8px',
                      border: '2px solid #2d3748'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#889aab', marginBottom: '12px' }}>
                        👤 COMPARE WITH
                      </div>
                      <select
                        value={selectedDriver}
                        onChange={(e) => setSelectedDriver(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '12px',
                          fontSize: '16px',
                          backgroundColor: '#0d1117',
                          color: '#fff',
                          border: '1px solid #2d3748',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        {['VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'NOR', 'PIA', 'ALO', 'STR'].map(driver => (
                          <option key={driver} value={driver}>{driver}</option>
                        ))}
                      </select>
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#667788' }}>
                        Benchmark driver for lap times
                      </div>
                    </div>
                  </div>
                )}

                <div style={{ textAlign: 'center' }}>
                  <button
                    onClick={startRace}
                    disabled={loading || loadingRaces || !selectedRace}
                    style={{
                      padding: '16px 48px',
                      fontSize: '18px',
                      fontWeight: 'bold',
                      backgroundColor: (loading || loadingRaces || !selectedRace) ? '#667788' : '#ff1e00',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: (loading || loadingRaces || !selectedRace) ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    {loading ? 'Starting Race...' : '🏁 Start Race'}
                  </button>
                </div>
              </div>
            ) : (
              /* Loading state between selection and race start */
              <div className="scenario-carousel">
                <div className="recommendation-box">
                  <div style={{
                    textAlign: 'center',
                    padding: '60px 20px',
                    color: '#889aab'
                  }}>
                    <div style={{ fontSize: '64px', marginBottom: '20px' }}>⏳</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: '#fff' }}>
                      Initializing Race...
                    </div>
                    <div style={{ fontSize: '16px' }}>
                      Loading {selectedRace?.name}
                    </div>
                  </div>
                </div>
              </div>
            )
          ) : (
            <div className="scenario-carousel"
                 onTouchStart={handleTouchStart}
                 onTouchMove={handleTouchMove}
                 onTouchEnd={handleTouchEnd}>

              {/* Navigation Arrows */}
              {scenarios.length > 1 && (
                <>
                  <button
                    className="carousel-arrow left"
                    onClick={(e) => {
                      e.stopPropagation();
                      goToPrevScenario();
                    }}
                    disabled={currentScenarioIndex === 0}
                    aria-label="Previous scenario"
                    style={{ pointerEvents: 'auto', zIndex: 10 }}>
                    ←
                  </button>
                  <button
                    className="carousel-arrow right"
                    onClick={(e) => {
                      e.stopPropagation();
                      goToNextScenario();
                    }}
                    disabled={currentScenarioIndex === scenarios.length - 1}
                    aria-label="Next scenario"
                    style={{ pointerEvents: 'auto', zIndex: 10 }}>
                    →
                  </button>
                </>
              )}

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
                        onClick={() => {
                          console.log('Clicked scenario:', scenario);
                          handleScenarioSelect(scenario);
                        }}
                        style={{
                          cursor: 'pointer',
                          userSelect: 'none',
                          WebkitUserSelect: 'none',
                          MozUserSelect: 'none',
                          msUserSelect: 'none'
                        }}
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
                    <div className="rec-empty">{loading ? 'Processing...' : 'No decisions needed at this lap'}</div>
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
                  <span className="event-text">{raceStarted ? 'No recent events' : 'Waiting for race start...'}</span>
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
                <div className="stat-num">{currentLap > 0 ? Math.round((1 - (apiCalls / currentLap)) * 100) : 0}%</div>
                <div className="stat-label">Cost Saved</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Position & Competitor Agents */}
        <div className="agents-column">
          {/* Position Agent */}
          <div className="agent-card">
            <div className="agent-header">
              <div className="agent-icon">🏁</div>
              <div className="agent-name">POSITION AGENT</div>
              <div className="agent-status active">ACTIVE</div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">POSITION</span>
                <span className="metric-value">P{insights.position.position}</span>
              </div>
              <div className="metric">
                <span className="metric-label">GAP AHEAD</span>
                <span className="metric-value">{insights.position.gap_ahead}s</span>
              </div>
              <div className="metric">
                <span className="metric-label">GAP BEHIND</span>
                <span className="metric-value">{insights.position.gap_behind}s</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.position.triggers.length > 0 ? insights.position.triggers.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message}
                  </div>
                )) : <div className="trigger low">{raceStarted ? 'Position stable' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>

          {/* Competitor Agent */}
          <div className="agent-card">
            <div className="agent-header">
              <div className="agent-icon">🎯</div>
              <div className="agent-name">COMPETITOR AGENT</div>
              <div className="agent-status active">ACTIVE</div>
            </div>

            <div className="agent-metrics">
              <div className="metric">
                <span className="metric-label">MONITORING</span>
                <span className="metric-value">P±2</span>
              </div>
              <div className="metric">
                <span className="metric-label">THREATS</span>
                <span className="metric-value">{insights.competitor.threats}</span>
              </div>
              <div className="metric">
                <span className="metric-label">PIT STATUS</span>
                <span className="metric-value">{insights.competitor.pit_status}</span>
              </div>
            </div>

            <div className="agent-triggers">
              <div className="trigger-title">ACTIVE TRIGGERS</div>
              <div className="triggers-list">
                {insights.competitor.triggers.length > 0 ? insights.competitor.triggers.map((trigger, i) => (
                  <div key={i} className={`trigger ${trigger.urgency?.toLowerCase()}`}>
                    <span className="trigger-dot"></span>
                    {trigger.message}
                  </div>
                )) : <div className="trigger low">{raceStarted ? 'No threats detected' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dash-footer">
        <div className="footer-right">
          {raceStarted ? (
            <span>
              RACE: {selectedRace?.name} 2024 • POSITION: P{raceState.position} • TIRES: {raceState.tireCompound} ({raceState.tireAge} laps) • STYLE: {raceState.drivingStyle}
            </span>
          ) : (
            <span>LIVE SIM MODE • {selectedRace ? `${selectedRace.name} selected` : 'Ready to configure...'}</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default LiveSim
