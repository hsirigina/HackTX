import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './HomePage.css'

const API_BASE_URL = 'http://localhost:8000'
const SESSION_ID = 'race-session-' + Date.now()

function HomePage() {
  const navigate = useNavigate()
  const [currentLap, setCurrentLap] = useState(1)
  const [selectedOption, setSelectedOption] = useState(null)
  const [strategies, setStrategies] = useState([])
  const [loading, setLoading] = useState(true)
  const [raceFinished, setRaceFinished] = useState(false)
  const [finalResults, setFinalResults] = useState(null)
  const [raceState, setRaceState] = useState({
    position: 3,
    tireCompound: 'SOFT',
    tireAge: 1,
    drivingStyle: 'BALANCED',
    totalRaceTime: 0,
    pitStops: 0
  })

  // Start race on component mount
  useEffect(() => {
    startRace()
  }, [])

  const startRace = async () => {
    setLoading(true)
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
      setStrategies(data.strategies)
      setRaceState(data.state)
      setLoading(false)
    } catch (error) {
      console.error('Failed to start race:', error)
      setLoading(false)
    }
  }

  const handleStrategyClick = async (strategy) => {
    console.log('Selected strategy:', strategy)
    setSelectedOption(strategy)

    try {
      const response = await fetch(`${API_BASE_URL}/api/race/decision`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: SESSION_ID,
          option_id: strategy.id
        })
      })

      const data = await response.json()
      console.log('Decision result:', data)

      // Animate transition
      setTimeout(() => {
        if (data.raceFinished) {
          setRaceFinished(true)
          setCurrentLap(57)
          setStrategies([])
          setFinalResults(data.finalResults)
        } else {
          setCurrentLap(data.currentLap)
          setStrategies(data.strategies)
          setRaceState(data.state)
        }
        setSelectedOption(null)
      }, 500)

    } catch (error) {
      console.error('Failed to make decision:', error)
      setSelectedOption(null)
    }
  }

  // Agent configuration
  const agents = [
    {
      name: 'Compound',
      subtitle: 'Tire Strategist',
      icon: 'tire',
      color: 'red',
      route: '/monitor'
    },
    {
      name: 'Scout',
      subtitle: 'Competitor Tracker',
      icon: 'flag',
      color: 'green',
      route: '/monitor'
    },
    {
      name: 'Track',
      subtitle: 'Position Agent',
      icon: 'track',
      color: 'red',
      route: '/monitor'
    },
    {
      name: 'Tempo',
      subtitle: 'Lap Agent',
      icon: 'stopwatch',
      color: 'red',
      route: '/simulator'
    }
  ]

  // Simple icon renderer using SVG
  const renderAgentIcon = (iconType) => {
    const iconMap = {
      tire: (
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="12" stroke="white" strokeWidth="2"/>
          <circle cx="16" cy="16" r="8" stroke="white" strokeWidth="2"/>
          <circle cx="16" cy="16" r="4" stroke="white" strokeWidth="2"/>
        </svg>
      ),
      flag: (
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect x="8" y="6" width="16" height="12" stroke="white" strokeWidth="2"/>
          <line x1="8" y1="6" x2="8" y2="26" stroke="white" strokeWidth="2"/>
          <line x1="12" y1="6" x2="12" y2="18" stroke="white" strokeWidth="1.5"/>
          <line x1="16" y1="6" x2="16" y2="18" stroke="white" strokeWidth="1.5"/>
          <line x1="20" y1="6" x2="20" y2="18" stroke="white" strokeWidth="1.5"/>
        </svg>
      ),
      track: (
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <path d="M16 8 L24 12 L24 20 L16 24 L8 20 L8 12 Z" stroke="white" strokeWidth="2"/>
          <circle cx="16" cy="16" r="3" fill="white"/>
        </svg>
      ),
      stopwatch: (
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="18" r="10" stroke="white" strokeWidth="2"/>
          <line x1="16" y1="18" x2="16" y2="12" stroke="white" strokeWidth="2"/>
          <line x1="16" y1="18" x2="20" y2="18" stroke="white" strokeWidth="2"/>
          <rect x="13" y="6" width="6" height="3" stroke="white" strokeWidth="1.5"/>
        </svg>
      )
    }
    return iconMap[iconType] || null
  }


  return (
    <div className="apex-container">
      {/* Header */}
      <div className="apex-header">
        <div className="apex-branding">
          <h1 className="apex-title">
            APE<span className="apex-x">X</span>
          </h1>
          <div className="lap-info">
            <div className="lap-counter">LAP {currentLap}/57</div>
            <div className="track-name">Track: Bahrain</div>
            {currentLap > 1 && currentLap < 57 && (
              <div className="race-state-info">
                <div className="state-item">P{raceState.position}</div>
                <div className="state-item">{raceState.tireCompound} ({raceState.tireAge} laps)</div>
                <div className="state-item">{raceState.drivingStyle}</div>
                <div className="state-item">Pits: {raceState.pitStops}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="apex-content">
        {/* Left Side - Agents */}
        <div className="agents-panel">
          {agents.map((agent, index) => (
            <div
              key={index}
              className={`agent-card agent-${agent.color}`}
              onClick={() => navigate(agent.route)}
            >
              <div className="agent-status-dot"></div>
              <div className="agent-icon">{renderAgentIcon(agent.icon)}</div>
              <div className="agent-info">
                <div className="agent-name">{agent.name}</div>
                <div className="agent-subtitle">{agent.subtitle}</div>
              </div>
              <div className="agent-arrow">›</div>
            </div>
          ))}
        </div>

        {/* Center - Coordinator */}
        <div className="coordinator-section">
          <svg className="flow-arrows" width="400" height="600">
            {/* Arrows from agents to coordinator */}
            <path d="M 0 80 L 150 250" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)"/>
            <path d="M 0 200 L 150 270" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)"/>
            <path d="M 0 320 L 150 290" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)"/>
            <path d="M 0 440 L 150 310" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)"/>

            {/* Arrow from coordinator back up */}
            <path d="M 200 200 Q 250 100 200 50" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)"/>

            {/* Arrow from coordinator back down */}
            <path d="M 200 350 Q 250 450 200 500" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)"/>

            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="rgba(255,255,255,0.2)" />
              </marker>
            </defs>
          </svg>

          <div className="coordinator-node">
            <div className="coordinator-icon">
              <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                <circle cx="40" cy="20" r="15" stroke="white" strokeWidth="2"/>
                <path d="M 25 35 Q 40 30 55 35" stroke="white" strokeWidth="2" fill="none"/>
                <line x1="40" y1="35" x2="40" y2="50" stroke="white" strokeWidth="2"/>
                <line x1="40" y1="50" x2="25" y2="70" stroke="white" strokeWidth="2"/>
                <line x1="40" y1="50" x2="55" y2="70" stroke="white" strokeWidth="2"/>
              </svg>
            </div>
            <div className="coordinator-title">APEX</div>
            <div className="coordinator-subtitle">Coordinator</div>
          </div>
        </div>

        {/* Right Side - Strategy */}
        <div className="strategy-panel">
          <div className="strategy-header">Strategy</div>
          <div className="strategy-boxes">
            {loading ? (
              <div className="no-strategies">
                <div className="no-strategies-message">Loading race data...</div>
              </div>
            ) : raceFinished || currentLap === 57 ? (
              // Race finished state
              <div className="race-finished">
                <div className="race-finished-icon">🏁</div>
                <div className="race-finished-title">RACE FINISHED</div>

                {finalResults ? (
                  <>
                    <div className="race-performance">
                      <div className="performance-header">🏆 YOUR RACE PERFORMANCE</div>
                      <div className="performance-stats">
                        <div className="perf-stat">
                          <span className="label">Your time:</span>
                          <span className="value">{finalResults.user_time.toFixed(1)}s</span>
                        </div>
                        <div className="perf-stat">
                          <span className="label">Winner's time:</span>
                          <span className="value">{finalResults.full_leaderboard[0].time.toFixed(1)}s ({finalResults.full_leaderboard[0].driver})</span>
                        </div>
                        <div className="perf-stat">
                          <span className="label">Gap to winner:</span>
                          <span className="value">+{finalResults.gap_to_winner.toFixed(1)}s</span>
                        </div>
                        <div className="perf-stat highlight">
                          <span className="label">Final position:</span>
                          <span className="value">P{finalResults.leaderboard_position} / {finalResults.total_drivers}</span>
                        </div>
                      </div>
                    </div>

                    <div className="leaderboard-section">
                      <div className="section-header">📊 LEADERBOARD (Your Position)</div>
                      <div className="leaderboard">
                        {finalResults.nearby_drivers.map((driver, idx) => (
                          <div key={idx} className={`leaderboard-row ${driver.driver === 'YOU' ? 'your-position' : ''}`}>
                            <span className="driver-marker">{driver.driver === 'YOU' ? '👉' : ''}</span>
                            <span className="driver-code">{driver.driver}</span>
                            <span className="team-name">{driver.team}</span>
                            <span className="time">{driver.time.toFixed(1)}s</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="strategy-summary">
                      <div className="section-header">📋 YOUR STRATEGY</div>
                      <div className="summary-content">
                        <div className="summary-item">
                          <strong>Pit stops:</strong> {finalResults.pit_stops}
                        </div>
                        {finalResults.pit_stop_details.map((pit, idx) => (
                          <div key={idx} className="pit-detail">
                            Pit {idx + 1}: Lap {pit.lap} → {pit.compound} tires
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="decision-timeline-section">
                      <div className="section-header">📋 DECISION TIMELINE</div>
                      <div className="timeline">
                        {finalResults.decision_timeline.map((decision, idx) => (
                          <div key={idx} className="timeline-item">
                            <span className="lap-num">Lap {decision.lap}:</span>
                            <span className="decision-text">{decision.title}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="race-finished-message">
                    Bahrain Grand Prix complete. All strategic decisions made through lap 55.
                  </div>
                )}
              </div>
            ) : strategies.length === 0 ? (
              <div className="no-strategies">
                <div className="no-strategies-message">No strategic decisions at this lap</div>
              </div>
            ) : (
              strategies.map((strategy) => (
                <div
                  key={strategy.id}
                  className={`strategy-box strategy-${strategy.confidence.toLowerCase()} ${
                    selectedOption?.id === strategy.id ? 'selected' : ''
                  }`}
                  onClick={() => handleStrategyClick(strategy)}
                >
                  <div className="strategy-content">
                    <div className="strategy-option">
                      {selectedOption?.id === strategy.id ? '✓ ' : ''}
                      {strategy.option}
                    </div>
                    <div className="strategy-title">{strategy.title}</div>
                    <div className="strategy-description">{strategy.description}</div>
                    <div className="strategy-reasoning">💭 {strategy.reasoning}</div>
                    <div className="strategy-metrics">
                      <span className="metric">📊 {strategy.raceTimeImpact}</span>
                      <span className="metric">⏱️ {strategy.lapTimeImpact}</span>
                      <span className="metric">🔥 {strategy.tireWear}</span>
                    </div>
                    <div className="strategy-confidence-badge">🤖 {strategy.confidence}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
