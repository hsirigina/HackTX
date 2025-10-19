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

  // Race selection state
  const [showSelection, setShowSelection] = useState(true)
  const [availableRaces, setAvailableRaces] = useState([])
  const [selectedRace, setSelectedRace] = useState(null)
  const [selectedPosition, setSelectedPosition] = useState(3)
  const [selectedTire, setSelectedTire] = useState('SOFT')
  const [selectedDriver, setSelectedDriver] = useState('VER')
  const [loadingRaces, setLoadingRaces] = useState(true)
  const [raceStarted, setRaceStarted] = useState(false)
  const [lastRaceResults, setLastRaceResults] = useState(null)
  const [showF1Lights, setShowF1Lights] = useState(false)
  const [lightsSequence, setLightsSequence] = useState(0)

  // Load available races on mount
  useEffect(() => {
    loadAvailableRaces()
  }, [])

  // Poll gesture server for hand gestures
  useEffect(() => {
    let lastGestureTime = 0
    const GESTURE_COOLDOWN = 1000 // 1 second cooldown between gestures

    const pollGestures = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/gesture')
        const data = await response.json()

        // Log all gestures for debugging
        if (data.gesture !== 'No Gesture') {
          console.log('Gesture received:', data.gesture, 'Current index:', currentScenarioIndex, 'Total scenarios:', scenarios.length)
        }

        const now = Date.now()

        // Check if enough time has passed since last gesture
        if (now - lastGestureTime < GESTURE_COOLDOWN) {
          return
        }

        // Only handle gestures when not showing F1 lights and scenarios are available
        if (!showF1Lights && scenarios.length > 0) {
          if (data.gesture === 'Swipe Left' && currentScenarioIndex < scenarios.length - 1) {
            console.log('✅ Detected Swipe Left - Moving to next scenario')
            goToNextScenario()
            lastGestureTime = now
            // Clear the gesture
            await fetch('http://localhost:5001/api/gesture/clear', { method: 'POST' })
          } else if (data.gesture === 'Swipe Right' && currentScenarioIndex > 0) {
            console.log('✅ Detected Swipe Right - Moving to previous scenario')
            goToPrevScenario()
            lastGestureTime = now
            // Clear the gesture
            await fetch('http://localhost:5001/api/gesture/clear', { method: 'POST' })
          } else if (data.gesture === 'Peace Sign' || data.gesture === 'V Sign') {
            console.log('✌️ Detected Peace Sign - Selecting current strategy option')
            const currentScenario = scenarios[currentScenarioIndex]
            if (currentScenario) {
              handleScenarioSelect(currentScenario)
            }
            lastGestureTime = now
            // Clear the gesture
            await fetch('http://localhost:5001/api/gesture/clear', { method: 'POST' })
          } else if (data.gesture !== 'No Gesture') {
            console.log('❌ Gesture not triggering navigation. Gesture:', data.gesture, 'CanGoNext:', currentScenarioIndex < scenarios.length - 1, 'CanGoPrev:', currentScenarioIndex > 0)
          }
        } else if (data.gesture !== 'No Gesture') {
          console.log('⏸️ Gesture ignored - F1 lights active or no scenarios available')
        }
      } catch (error) {
        // Gesture server not running, that's okay
        console.debug('Gesture server not available')
      }
    }

    // Poll every 300ms for gestures
    const interval = setInterval(pollGestures, 300)
    return () => clearInterval(interval)
  }, [currentScenarioIndex, scenarios.length, showF1Lights])

  const loadAvailableRaces = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/races/available`)
      const data = await response.json()
      if (data.success && data.data && data.data.races) {
        setAvailableRaces(data.data.races)
        // Set Bahrain as default
        const bahrain = data.data.races.find(r => r.id === 'bahrain')
        setSelectedRace(bahrain || data.data.races[0])
      } else {
        // Fallback races if API fails
        const fallbackRaces = [
          { id: 'bahrain', name: 'Bahrain Grand Prix', laps: 57, country: 'Bahrain' },
          { id: 'monaco', name: 'Monaco Grand Prix', laps: 78, country: 'Monaco' }
        ]
        setAvailableRaces(fallbackRaces)
        setSelectedRace(fallbackRaces[0])
      }
      setLoadingRaces(false)
      setInitialLoading(false)
    } catch (error) {
      console.error('Failed to load races:', error)
      // Fallback races if API fails
      const fallbackRaces = [
        { id: 'bahrain', name: 'Bahrain Grand Prix', laps: 57, country: 'Bahrain' },
        { id: 'monaco', name: 'Monaco Grand Prix', laps: 78, country: 'Monaco' }
      ]
      setAvailableRaces(fallbackRaces)
      setSelectedRace(fallbackRaces[0])
      setLoadingRaces(false)
      setInitialLoading(false)
    }
  }

  const startRace = async () => {
    if (!selectedRace) return

    setLoading(true)
    setShowSelection(false)
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

      // Ensure minimum 2 seconds of loading
      const elapsedTime = Date.now() - startTime
      const remainingTime = Math.max(0, 2000 - elapsedTime)

      setTimeout(() => {
        setInitialLoading(false)
        setLoading(false)
        // Start F1 lights sequence after loading
        startF1LightsSequence()
      }, remainingTime)
    } catch (error) {
      console.error('Failed to start race:', error)

      // Still wait minimum 2 seconds even on error
      const elapsedTime = Date.now() - startTime
      const remainingTime = Math.max(0, 2000 - elapsedTime)

      setTimeout(() => {
        alert('Failed to connect to backend API. Make sure the backend is running on port 8000. Error: ' + error.message)
        setInitialLoading(false)
        setLoading(false)
      }, remainingTime)
    }
  }

  // F1 Lights sequence function
  const startF1LightsSequence = () => {
    setShowF1Lights(true)
    setLightsSequence(0)
    
    // F1 lights sequence: 5 lights, each 1 second apart, then 2-4 second random delay
    const lightTimings = [1000, 2000, 3000, 4000, 5000] // 5 lights
    const randomDelay = 2000 + Math.random() * 2000 // 2-4 seconds random delay
    
    lightTimings.forEach((timing, index) => {
      setTimeout(() => {
        setLightsSequence(index + 1)
      }, timing)
    })
    
    // Lights out after random delay
    setTimeout(() => {
      setLightsSequence(6) // All lights off
      setTimeout(() => {
        setShowF1Lights(false)
        console.log('🏁 F1 Lights complete - Scenarios available:', scenarios.length)
      }, 1000)
    }, 5000 + randomDelay)
  }

  // Parse agent insights from race state
  const parseInsights = () => {
    const avgLapTime = raceState.totalRaceTime / Math.max(currentLap || 1, 1)
    
    // Calculate tire degradation percentage based on compound max laps
    const maxLaps = {
      'SOFT': 25,
      'MEDIUM': 40,
      'HARD': 60
    }
    const tireMaxLaps = maxLaps[raceState.tireCompound] || 40
    const tireDegradationPct = Math.min(100, ((raceState.tireAge || 0) / tireMaxLaps * 100))
    
    // Format degradation display: show seconds if available, otherwise percentage
    const degradationDisplay = raceState.tireDegradation !== undefined 
      ? `+${raceState.tireDegradation.toFixed(2)}s (${tireDegradationPct.toFixed(0)}%)`
      : `${tireDegradationPct.toFixed(0)}%`

    return {
      tire: {
        compound: raceState.tireCompound || 'SOFT',
        tire_age: raceState.tireAge || 0,
        degradation: degradationDisplay,
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
    tire: { compound: '--', tire_age: 0, degradation: '0%', status: 'active', triggers: [] },
    laptime: { current_time: '--', avg_time: '--', trend: '--', status: 'active', triggers: [] },
    position: { position: '--', gap_ahead: '--', gap_behind: '--', status: 'active', triggers: [] },
    competitor: { threats: 0, pit_status: '--', status: 'active', triggers: [] }
  }

  // Handle strategy selection and progress race
  const handleScenarioSelect = async (scenario) => {
    if (loading || !scenario) return

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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Decision result:', data)
      console.log('Race finished?', data.raceFinished)
      console.log('Final results:', data.finalResults)
      
      if (data.finalResults && data.finalResults.full_leaderboard) {
        console.log('🏁 Leaderboard received:')
        console.log(`   Total finishers: ${data.finalResults.full_leaderboard.length}`)
        console.log(`   Winner: ${data.finalResults.full_leaderboard[0]?.driver} - ${data.finalResults.full_leaderboard[0]?.time?.toFixed(1)}s`)
        console.log(`   Your position: P${data.finalResults.leaderboard_position} / ${data.finalResults.total_drivers}`)
      }

      setApiCalls(apiCalls + 1)

      // Add event to timeline
      setEvents(prev => [{
        lap_number: currentLap,
        recommendation_type: scenario.title || 'Decision',
        reasoning: scenario.description || 'Strategy selected'
      }, ...prev.slice(0, 4)])

      // Update race state
      if (data.raceFinished) {
        console.log('🏁 RACE FINISHED! Setting final results...')
        setRaceFinished(true)
        setCurrentLap(data.currentLap || selectedRace?.laps || 57)
        setScenarios([])
        setFinalResults(data.finalResults || null)
        setRaceState(data.state || raceState)
        setEvents(prev => [{
          lap_number: data.currentLap || selectedRace?.laps || 57,
          recommendation_type: 'RACE FINISHED',
          reasoning: 'Race completed!'
        }, ...prev])
      } else {
        setCurrentLap(data.currentLap || currentLap)
        setScenarios(data.strategies || [])
        setRaceState(data.state || raceState)
        setCurrentScenarioIndex(0)
      }

      setLoading(false)
    } catch (error) {
      console.error('Failed to make decision:', error)
      alert(`Error making decision: ${error.message}. Please check that the backend is running.`)
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
    console.log('🔄 goToPrevScenario called - Current:', currentScenarioIndex, 'Scenarios:', scenarios.length, 'IsSliding:', isSliding)
    if (currentScenarioIndex > 0) {
      setIsSliding(true)
      setCurrentScenarioIndex(currentScenarioIndex - 1)
      console.log('✅ Moving to previous scenario:', currentScenarioIndex - 1)
      setTimeout(() => {
        setIsSliding(false)
      }, 150) // Much faster timeout
    } else {
      console.log('❌ Cannot go to previous - Current:', currentScenarioIndex)
    }
  }

  const goToNextScenario = () => {
    console.log('🔄 goToNextScenario called - Current:', currentScenarioIndex, 'Scenarios:', scenarios.length, 'IsSliding:', isSliding)
    if (currentScenarioIndex < scenarios.length - 1) {
      setIsSliding(true)
      setCurrentScenarioIndex(currentScenarioIndex + 1)
      console.log('✅ Moving to next scenario:', currentScenarioIndex + 1)
      setTimeout(() => {
        setIsSliding(false)
      }, 150) // Much faster timeout
    } else {
      console.log('❌ Cannot go to next - Current:', currentScenarioIndex, 'Max:', scenarios.length - 1)
    }
  }

  if (initialLoading && !showSelection) {
    return (
      <div className="loading-container">
        <div className="loading-apex-title"></div>
        <div className="loading-spinner"></div>
        <div className="loading-text">INITIALIZING RACE SIMULATION...</div>
      </div>
    )
  }

  if (showF1Lights) {
    return (
      <div className="agent-dashboard">
        {/* Top Header */}
        <div className="dash-header">
          <div className="apex-header-title"></div>
        </div>

        {/* Main Content Grid */}
        <div className="dash-main">
          {/* Left Column - Tire & LapTime Agents */}
          <div className="agents-column">
            {/* Tire Data Agent */}
            <div className="agent-card">
              <div className="agent-header">
                <div className="agent-icon"><img src="/tireagent.png" alt="Tire Agent" /></div>
                <div className="agent-name">TIRE DATA AGENT</div>
                <div className="agent-status active">ACTIVE</div>
              </div>
              <div className="agent-metrics">
                <div className="metric">
                  <span className="metric-label">COMPOUND</span>
                  <span className="metric-value">SOFT</span>
                </div>
                <div className="metric">
                  <span className="metric-label">TIRE AGE</span>
                  <span className="metric-value">0 laps</span>
                </div>
                <div className="metric">
                  <span className="metric-label">DEGRADATION</span>
                  <span className="metric-value">+0.0s</span>
                </div>
              </div>
            </div>

            {/* LapTime Agent */}
            <div className="agent-card">
              <div className="agent-header">
                <div className="agent-icon"><img src="/stopwatch agent.png" alt="Laptime Agent" /></div>
                <div className="agent-name">LAPTIME AGENT</div>
                <div className="agent-status active">ACTIVE</div>
              </div>
              <div className="agent-metrics">
                <div className="metric">
                  <span className="metric-label">CURRENT LAP</span>
                  <span className="metric-value">1:22.5s</span>
                </div>
                <div className="metric">
                  <span className="metric-label">AVG (5 LAPS)</span>
                  <span className="metric-value">1:22.8s</span>
                </div>
                <div className="metric">
                  <span className="metric-label">TREND</span>
                  <span className="metric-value">STABLE</span>
                </div>
              </div>
            </div>
          </div>

          {/* Center Column - F1 Lights */}
          <div className="coordinator-column">
            <div className="coordinator-header">
              <div className="coord-title">AI COORDINATOR</div>
              <div className="coord-model">Gemini 2.0 Flash</div>
            </div>

            <div className="lap-display">
              <div className="lap-label">CURRENT LAP</div>
              <div className="lap-number">1<span>/57</span></div>
            </div>

            {/* F1 Lights in Strategy Area */}
            <div className="f1-lights-strategy-box">
              <div className="f1-lights-grid-20">
                {[1, 2, 3, 4, 5].map((column) => (
                  <div key={column} className="f1-lights-column">
                    {[1, 2, 3, 4].map((row) => (
                      <div 
                        key={`${column}-${row}`}
                        className={`f1-light-small ${lightsSequence >= column ? 'active' : ''} ${lightsSequence === 6 ? 'lights-out' : ''}`}
                      />
                    ))}
                  </div>
                ))}
              </div>

              <div className="f1-timer-display">
                <div className="f1-timer">00.000</div>
              </div>
            </div>
          </div>

          {/* Right Column - Position & Competitor Agents */}
          <div className="agents-column">
            {/* Position Agent */}
            <div className="agent-card">
              <div className="agent-header">
                <div className="agent-icon"><img src="/flagAgent.png" alt="Position Agent" /></div>
                <div className="agent-name">POSITION AGENT</div>
                <div className="agent-status active">ACTIVE</div>
              </div>
              <div className="agent-metrics">
                <div className="metric">
                  <span className="metric-label">POSITION</span>
                  <span className="metric-value">P3</span>
                </div>
                <div className="metric">
                  <span className="metric-label">GAP AHEAD</span>
                  <span className="metric-value">+0.5s</span>
                </div>
                <div className="metric">
                  <span className="metric-label">GAP BEHIND</span>
                  <span className="metric-value">-1.2s</span>
                </div>
              </div>
            </div>

            {/* Competitor Agent */}
            <div className="agent-card">
              <div className="agent-header">
                <div className="agent-icon"><img src="/trackagent.png" alt="Competitor Agent" /></div>
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
                  <span className="metric-value">0</span>
                </div>
                <div className="metric">
                  <span className="metric-label">PIT STATUS</span>
                  <span className="metric-value">NONE</span>
                </div>
              </div>
            </div>
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
              <div className="agent-icon"><img src="/tireagent.png" alt="Tire Agent" /></div>
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
                <span className="metric-value">{insights.tire.degradation || '0%'}</span>
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
                )) || <div className="trigger low">{raceStarted ? 'Tires in good condition' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>

          {/* LapTime Agent */}
          <div className="agent-card" onClick={() => setIsLaptimeModalOpen(true)} style={{ cursor: 'pointer' }}>
            <div className="agent-header">
              <div className="agent-icon"><img src="/stopwatch agent.png" alt="Laptime Agent" /></div>
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
                )) || <div className="trigger low">{raceStarted ? 'Pace stable' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>
        </div>

        {/* Center Column - AI Coordinator */}
        <div className="coordinator-column">
          <div className="coordinator-header">
            <div className="coord-title">AI COORDINATOR</div>
            <div className="coord-model">Gemini 2.0 Flash</div>
            {raceStarted && (
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
            )}
          </div>

          <div className="lap-display">
            <div className="lap-label">CURRENT LAP</div>
            <div className="lap-number">{currentLap || '--'}<span>/{selectedRace?.laps || '--'}</span></div>
          </div>

          {/* Swipable Scenario Carousel OR Final Results OR Race Selection */}
          {!raceStarted && showSelection ? (
            /* Race Selection Screen */
            <div style={{ 
              padding: '20px', 
              pointerEvents: 'auto',
              userSelect: 'auto',
              WebkitUserSelect: 'auto',
              position: 'relative',
              zIndex: 10
            }}>
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

              {loadingRaces || initialLoading ? (
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
                      onChange={(e) => {
                        e.stopPropagation();
                        setSelectedRace(availableRaces.find(r => r.id === e.target.value));
                      }}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        backgroundColor: '#0d1117',
                        color: '#fff',
                        border: '1px solid #2d3748',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        pointerEvents: 'auto',
                        userSelect: 'auto',
                        WebkitAppearance: 'menulist',
                        appearance: 'auto'
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
                      onChange={(e) => {
                        e.stopPropagation();
                        setSelectedPosition(parseInt(e.target.value));
                      }}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        backgroundColor: '#0d1117',
                        color: '#fff',
                        border: '1px solid #2d3748',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        pointerEvents: 'auto',
                        userSelect: 'auto',
                        WebkitAppearance: 'menulist',
                        appearance: 'auto'
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
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTire(compound);
                          }}
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
                            justifyContent: 'space-between',
                            pointerEvents: 'auto',
                            userSelect: 'none'
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
                      onChange={(e) => {
                        e.stopPropagation();
                        setSelectedDriver(e.target.value);
                      }}
                      style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '16px',
                        backgroundColor: '#0d1117',
                        color: '#fff',
                        border: '1px solid #2d3748',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        pointerEvents: 'auto',
                        userSelect: 'auto',
                        WebkitAppearance: 'menulist',
                        appearance: 'auto'
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
                  onClick={(e) => {
                    e.stopPropagation();
                    startRace();
                  }}
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
                    transition: 'all 0.2s',
                    pointerEvents: 'auto',
                    userSelect: 'none'
                  }}
                >
                  {loading ? 'Starting Race...' : '🏁 Start Race'}
                </button>
              </div>
            </div>
          ) : raceFinished ? (
            <div className="final-results-container">
              {finalResults ? (
                <div className="race-performance-section">
                  <div className="section-header">🏆 YOUR RACE PERFORMANCE</div>
                  <div className="performance-grid">
                    <div className="perf-stat">
                      <span className="perf-label">Your time:</span>
                      <span className="perf-value">{finalResults.user_time ? finalResults.user_time.toFixed(1) : '--'}s</span>
                    </div>
                    <div className="perf-stat">
                      <span className="perf-label">Winner's time:</span>
                      <span className="perf-value">{finalResults.full_leaderboard?.[0]?.time ? finalResults.full_leaderboard[0].time.toFixed(1) : '--'}s</span>
                    </div>
                    <div className="perf-stat">
                      <span className="perf-label">Gap to winner:</span>
                      <span className="perf-value highlight">+{finalResults.gap_to_winner ? finalResults.gap_to_winner.toFixed(1) : '--'}s</span>
                    </div>
                    <div className="perf-stat">
                      <span className="perf-label">Final position:</span>
                      <span className="perf-value highlight">P{finalResults.leaderboard_position || '--'} / {finalResults.total_drivers || '--'}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="race-performance-section">
                  <div className="section-header">🏆 RACE COMPLETE!</div>
                  <div style={{ textAlign: 'center', padding: '40px', color: '#889aab' }}>
                    Race finished! Final results are being calculated...
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
                        onClick={(e) => {
                          e.stopPropagation();
                          handleScenarioSelect(scenario);
                        }}
                        style={{ cursor: loading ? 'wait' : 'pointer' }}
                      >
                        <div className="rec-header">
                          <span className="rec-label">
                            {scenario.option || `Option ${index + 1}`}
                          </span>
                          <span className={`rec-urgency ${scenario.confidence?.toLowerCase() || 'recommended'}`}>
                            {scenario.confidence || 'RECOMMENDED'}
                          </span>
                        </div>

                        <div className="rec-type">{scenario.title || 'Strategy Decision'}</div>
                        <div className="rec-message">{scenario.description || 'Make a strategic decision'}</div>
                        <div className="rec-reasoning">{scenario.reasoning || ''}</div>

                        <div className="rec-meta">
                          <div className="rec-metrics">
                            <div className="metric-item">
                              <span>Race Impact:</span>
                              <span>{scenario.raceTimeImpact || '--'}</span>
                            </div>
                            <div className="metric-item">
                              <span>Lap Impact:</span>
                              <span>{scenario.lapTimeImpact || '--'}</span>
                            </div>
                            <div className="metric-item">
                              <span>Tire Wear:</span>
                              <span>{scenario.tireWear || '--'}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : lastRaceResults ? (
                  <div className="recommendation-box" style={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    gap: '20px',
                    padding: '40px'
                  }}>
                    <div className="rec-empty" style={{ marginBottom: '10px' }}>
                      Previous race completed
                    </div>
                    <button
                      onClick={() => {
                        setFinalResults(lastRaceResults);
                        setRaceFinished(true);
                      }}
                      style={{
                        padding: '14px 30px',
                        fontSize: '14px',
                        fontWeight: 'bold',
                        backgroundColor: 'rgba(0, 191, 255, 0.1)',
                        color: '#00bfff',
                        border: '1px solid rgba(0, 191, 255, 0.3)',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        textTransform: 'uppercase',
                        letterSpacing: '1px'
                      }}
                      onMouseOver={(e) => {
                        e.target.style.backgroundColor = 'rgba(0, 191, 255, 0.2)';
                        e.target.style.borderColor = 'rgba(0, 191, 255, 0.5)';
                        e.target.style.boxShadow = '0 0 20px rgba(0, 191, 255, 0.3)';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.backgroundColor = 'rgba(0, 191, 255, 0.1)';
                        e.target.style.borderColor = 'rgba(0, 191, 255, 0.3)';
                        e.target.style.boxShadow = 'none';
                      }}
                    >
                      📊 View Last Race Results
                    </button>
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
              <div className="agent-icon"><img src="/flagAgent.png" alt="Position Agent" /></div>
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
                )) || <div className="trigger low">{raceStarted ? 'Position stable' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>

          {/* Competitor Agent */}
          <div 
            className="agent-card" 
            onClick={() => navigate('/monitor', { 
              state: { 
                selectedRace: { id: 'bahrain', name: 'Bahrain Grand Prix', laps: 57 },
                selectedDriver: 'VER',
                currentLap: currentLap,
                raceState: raceState
              } 
            })} 
            style={{cursor: 'pointer'}}
          >
            <div className="agent-header">
              <div className="agent-icon"><img src="/trackagent.png" alt="Competitor Agent" /></div>
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
                )) || <div className="trigger low">{raceStarted ? 'No threats detected' : 'Waiting for race start...'}</div>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dash-footer">
        <div className="footer-right">
          {raceStarted ? (
            <span>RACE: {selectedRace?.name} 2024 • POSITION: P{raceState.position} • TIRES: {raceState.tireCompound} ({raceState.tireAge} laps) • STYLE: {raceState.drivingStyle}</span>
          ) : (
            <span>MULTI-AGENT SYSTEM • {selectedRace ? `${selectedRace.name} selected` : 'Ready to configure...'}</span>
          )}
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

      {/* Race Complete Modal */}
      {raceFinished && finalResults && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)'
        }}>
          <div style={{
            backgroundColor: 'rgba(13, 17, 23, 0.95)',
            border: '1px solid rgba(0, 191, 255, 0.3)',
            borderRadius: '8px',
            maxWidth: '700px',
            width: '100%',
            maxHeight: 'fit-content',
            boxShadow: '0 0 50px rgba(0, 191, 255, 0.2)',
            position: 'relative'
          }}>
            {/* Close Button */}
            <button
              onClick={() => {
                setLastRaceResults(finalResults);
                setRaceFinished(false);
              }}
              style={{
                position: 'absolute',
                top: '20px',
                right: '20px',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: 'rgba(13, 17, 23, 0.8)',
                border: '1px solid rgba(136, 154, 171, 0.3)',
                color: '#889aab',
                fontSize: '24px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                zIndex: 10
              }}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = 'rgba(136, 154, 171, 0.2)';
                e.target.style.color = '#fff';
                e.target.style.borderColor = 'rgba(0, 191, 255, 0.5)';
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = 'rgba(13, 17, 23, 0.8)';
                e.target.style.color = '#889aab';
                e.target.style.borderColor = 'rgba(136, 154, 171, 0.3)';
              }}
            >
              ×
            </button>

            {/* Header */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(0, 191, 255, 0.1) 0%, rgba(0, 191, 255, 0.05) 100%)',
              padding: '25px 20px 20px',
              borderBottom: '1px solid rgba(0, 191, 255, 0.2)',
              textAlign: 'center',
              position: 'relative'
            }}>
              <div style={{ fontSize: '36px', marginBottom: '8px' }}>🏁</div>
              <h2 style={{ 
                fontSize: '24px', 
                fontWeight: 'bold', 
                color: '#00bfff',
                margin: '0 0 8px 0',
                textTransform: 'uppercase',
                letterSpacing: '2px',
                textShadow: '0 0 20px rgba(0, 191, 255, 0.5)'
              }}>
                Race Complete!
              </h2>
              <p style={{ 
                fontSize: '13px', 
                color: '#889aab',
                margin: 0,
                letterSpacing: '0.5px'
              }}>
                {selectedRace?.name} • {new Date().getFullYear()}
              </p>
            </div>

            {/* Your Performance */}
            <div style={{
              padding: '20px',
              borderBottom: '1px solid rgba(0, 191, 255, 0.1)'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#00bfff',
                marginBottom: '15px',
                textAlign: 'center',
                textTransform: 'uppercase',
                letterSpacing: '1.5px'
              }}>
                🏆 Your Performance
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '12px'
              }}>
                <div style={{
                  backgroundColor: 'rgba(13, 17, 23, 0.6)',
                  padding: '15px',
                  borderRadius: '6px',
                  textAlign: 'center',
                  border: '1px solid rgba(0, 191, 255, 0.2)',
                  transition: 'all 0.3s'
                }}>
                  <div style={{ fontSize: '11px', color: '#889aab', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Final Position</div>
                  <div style={{ 
                    fontSize: '32px', 
                    fontWeight: 'bold', 
                    color: '#00bfff',
                    textShadow: '0 0 20px rgba(0, 191, 255, 0.5)',
                    lineHeight: '1'
                  }}>
                    P{finalResults.leaderboard_position || '--'}
                  </div>
                  <div style={{ fontSize: '10px', color: '#667788', marginTop: '6px' }}>out of {finalResults.total_drivers || '--'} finishers</div>
                </div>
                <div style={{
                  backgroundColor: 'rgba(13, 17, 23, 0.6)',
                  padding: '15px',
                  borderRadius: '6px',
                  textAlign: 'center',
                  border: '1px solid rgba(0, 191, 255, 0.2)',
                  transition: 'all 0.3s'
                }}>
                  <div style={{ fontSize: '11px', color: '#889aab', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Gap to Winner</div>
                  <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#00ff88', lineHeight: '1' }}>
                    +{finalResults.gap_to_winner ? finalResults.gap_to_winner.toFixed(1) : '--'}s
                  </div>
                  <div style={{ fontSize: '10px', color: '#667788', marginTop: '6px' }}>Time difference</div>
                </div>
              </div>
            </div>

            {/* Final Leaderboard */}
            <div style={{ padding: '20px' }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#00bfff',
                marginBottom: '8px',
                textAlign: 'center',
                textTransform: 'uppercase',
                letterSpacing: '1.5px'
              }}>
                📊 Final Classification
              </h3>
              <p style={{
                fontSize: '10px',
                color: '#667788',
                textAlign: 'center',
                marginBottom: '12px',
                marginTop: '0'
              }}>
                Drivers who completed the full race distance
              </p>
              <div style={{
                backgroundColor: 'rgba(13, 17, 23, 0.4)',
                borderRadius: '6px',
                overflow: 'hidden',
                border: '1px solid rgba(0, 191, 255, 0.1)',
                maxHeight: '300px',
                overflowY: 'auto'
              }}>
                {/* Leaderboard Header */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '60px 1fr 120px 100px',
                  padding: '10px 15px',
                  backgroundColor: 'rgba(0, 191, 255, 0.05)',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  color: '#889aab',
                  borderBottom: '1px solid rgba(0, 191, 255, 0.2)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  <div>Pos</div>
                  <div>Driver</div>
                  <div>Time</div>
                  <div>Gap</div>
                </div>
                
                {/* Leaderboard Rows */}
                {finalResults.full_leaderboard?.slice(0, 15).map((driver, index) => {
                  const isUser = driver.driver === 'YOU';
                  const winnerTime = finalResults.full_leaderboard[0]?.time || 0;
                  const gap = index === 0 ? 0 : driver.time - winnerTime;
                  
                  return (
                    <div 
                      key={index}
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '60px 1fr 120px 100px',
                        padding: '12px 15px',
                        backgroundColor: isUser ? 'rgba(0, 191, 255, 0.15)' : (index % 2 === 0 ? 'rgba(0, 191, 255, 0.02)' : 'transparent'),
                        borderLeft: isUser ? '3px solid #00bfff' : '3px solid transparent',
                        borderBottom: index < 14 ? '1px solid rgba(0, 191, 255, 0.1)' : 'none',
                        transition: 'all 0.2s',
                        fontSize: '12px'
                      }}
                    >
                      <div style={{ 
                        fontWeight: 'bold', 
                        fontSize: '13px',
                        color: index === 0 ? '#ffd700' : index === 1 ? '#c0c0c0' : index === 2 ? '#cd7f32' : '#00bfff'
                      }}>
                        {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `P${index + 1}`}
                      </div>
                      <div style={{ 
                        fontWeight: isUser ? 'bold' : 'normal',
                        color: isUser ? '#00bfff' : '#fff',
                        fontSize: '12px'
                      }}>
                        {driver.driver}
                        {driver.team && (
                          <div style={{ fontSize: '9px', color: '#667788', marginTop: '2px' }}>
                            {driver.team}
                          </div>
                        )}
                      </div>
                      <div style={{ color: '#889aab', fontFamily: 'monospace', fontSize: '11px' }}>
                        {driver.time ? driver.time.toFixed(1) : '--'}s
                      </div>
                      <div style={{ 
                        color: index === 0 ? '#00ff88' : '#889aab',
                        fontFamily: 'monospace',
                        fontWeight: '500',
                        fontSize: '11px'
                      }}>
                        {index === 0 ? '—' : `+${gap.toFixed(1)}s`}
                      </div>
                    </div>
                  );
                })}
              </div>
              {finalResults.full_leaderboard?.length > 15 && (
                <div style={{
                  textAlign: 'center',
                  padding: '8px',
                  fontSize: '10px',
                  color: '#667788'
                }}>
                  + {finalResults.full_leaderboard.length - 15} more drivers
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div style={{ 
              padding: '15px 20px',
              textAlign: 'center',
              display: 'flex',
              gap: '12px',
              justifyContent: 'center',
              borderTop: '1px solid rgba(0, 191, 255, 0.1)'
            }}>
              <button
                onClick={() => {
                  setLastRaceResults(finalResults);
                  setRaceFinished(false);
                }}
                style={{
                  padding: '12px 24px',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  backgroundColor: 'rgba(13, 17, 23, 0.8)',
                  color: '#889aab',
                  border: '1px solid rgba(136, 154, 171, 0.3)',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}
                onMouseOver={(e) => {
                  e.target.style.backgroundColor = 'rgba(136, 154, 171, 0.2)';
                  e.target.style.color = '#fff';
                  e.target.style.borderColor = 'rgba(0, 191, 255, 0.5)';
                }}
                onMouseOut={(e) => {
                  e.target.style.backgroundColor = 'rgba(13, 17, 23, 0.8)';
                  e.target.style.color = '#889aab';
                  e.target.style.borderColor = 'rgba(136, 154, 171, 0.3)';
                }}
              >
                Close
              </button>
              <button
                onClick={() => {
                  setRaceFinished(false);
                  setFinalResults(null);
                  setLastRaceResults(null);
                  setShowSelection(true);
                  setRaceStarted(false);
                  setCurrentLap(null);
                  setScenarios([]);
                }}
                style={{
                  padding: '12px 28px',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  backgroundColor: '#00bfff',
                  color: '#0d1117',
                  border: '1px solid #00bfff',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  boxShadow: '0 0 20px rgba(0, 191, 255, 0.3)'
                }}
                onMouseOver={(e) => {
                  e.target.style.backgroundColor = '#00d4ff';
                  e.target.style.boxShadow = '0 0 30px rgba(0, 191, 255, 0.5)';
                }}
                onMouseOut={(e) => {
                  e.target.style.backgroundColor = '#00bfff';
                  e.target.style.boxShadow = '0 0 20px rgba(0, 191, 255, 0.3)';
                }}
              >
                🏁 Start New Race
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentDashboard
