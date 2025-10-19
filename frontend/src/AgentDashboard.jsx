import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import './AgentDashboard.css'

function AgentDashboard() {
  const [agentStatus, setAgentStatus] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [scenarios, setScenarios] = useState([])
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0)
  const [currentLap, setCurrentLap] = useState(null)
  const [events, setEvents] = useState([])
  const [apiCalls, setApiCalls] = useState(0)
  const [touchStart, setTouchStart] = useState(0)
  const [touchEnd, setTouchEnd] = useState(0)
  const [isSliding, setIsSliding] = useState(false)
  const [lastGestureTime, setLastGestureTime] = useState(0)

  // Poll Supabase for agent status
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get latest agent status
        const { data: statusData, error: statusError } = await supabase
          .from('agent_status')
          .select('*')
          .order('lap_number', { ascending: false })
          .limit(1)

        if (statusError) throw statusError

        if (statusData && statusData.length > 0) {
          const status = statusData[0]
          setAgentStatus(status)
          setCurrentLap(status.lap_number)
        }

        // Get latest recommendation
        const { data: recData, error: recError } = await supabase
          .from('agent_recommendations')
          .select('*')
          .order('lap_number', { ascending: false })
          .limit(1)

        if (recError) throw recError

        if (recData && recData.length > 0) {
          const rec = recData[0]
          setRecommendation(rec)
        }

        // Get all scenarios (recommendations)
        const { data: scenariosData, error: scenariosError } = await supabase
          .from('agent_recommendations')
          .select('*')
          .order('lap_number', { ascending: false })
          .limit(20)

        if (!scenariosError && scenariosData) {
          setScenarios(scenariosData)
          setEvents(scenariosData.slice(0, 5))
        }

        // Count API calls (recommendations = AI calls)
        const { count } = await supabase
          .from('agent_recommendations')
          .select('*', { count: 'exact', head: true })

        setApiCalls(count || 0)

      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  // Parse agent insights from database fields
  const parseInsights = (statusData) => {
    if (!statusData) return { tire: {}, laptime: {}, position: {}, competitor: {} }
    
    try {
      return {
        tire: {
          compound: statusData.tire_compound || 'UNKNOWN',
          tire_age: statusData.tire_age || 0,
          degradation: statusData.tire_degradation_trend || '+0.0',
          status: 'active',
          triggers: statusData.tire_age > 20 ? [
            { message: `Old tires (${statusData.tire_age} laps)`, urgency: 'HIGH' }
          ] : []
        },
        laptime: {
          current_time: statusData.current_pace?.toFixed(3) || '0.000',
          avg_time: statusData.avg_lap_time?.toFixed(3) || '0.000',
          trend: statusData.pace_trend || 'STABLE',
          status: 'active',
          triggers: statusData.pace_trend === 'DEGRADING' ? [
            { message: 'Pace degrading', urgency: 'MEDIUM' }
          ] : []
        },
        position: {
          position: statusData.current_position || 1,
          gap_ahead: statusData.gap_ahead?.toFixed(1) || '+0.0',
          gap_behind: statusData.gap_behind?.toFixed(1) || '+0.0',
          status: 'active',
          triggers: []
        },
        competitor: {
          threats: Array.isArray(statusData.nearby_threats) ? statusData.nearby_threats.length : 0,
          pit_status: 'MONITORING',
          status: 'active',
          triggers: statusData.nearby_threats?.length > 0 ? [
            { message: `${statusData.nearby_threats.length} threats detected`, urgency: 'HIGH' }
          ] : []
        }
      }
    } catch (e) {
      console.error('Error parsing insights:', e)
      return { tire: {}, laptime: {}, position: {}, competitor: {} }
    }
  }

  const insights = parseInsights(agentStatus)

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

  // Poll gesture server for hand gestures
  useEffect(() => {
    const pollGestures = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/gesture')
        const data = await response.json()
        
        // Only process if it's a new gesture (different timestamp)
        if (data.timestamp > lastGestureTime && data.gesture !== 'No Gesture') {
          setLastGestureTime(data.timestamp)
          
          // Handle gestures
          if (data.gesture === 'Swipe Left' && currentScenarioIndex < scenarios.length - 1) {
            console.log('👈 Gesture detected: Swipe Left - Going to next scenario')
            goToNextScenario()
          } else if (data.gesture === 'Swipe Right' && currentScenarioIndex > 0) {
            console.log('👉 Gesture detected: Swipe Right - Going to previous scenario')
            goToPrevScenario()
          }
        }
      } catch (error) {
        // Gesture server not running, silently ignore
      }
    }

    const gestureInterval = setInterval(pollGestures, 200) // Poll 5 times per second
    return () => clearInterval(gestureInterval)
  }, [currentScenarioIndex, scenarios.length, lastGestureTime, goToNextScenario, goToPrevScenario])

  const currentScenario = scenarios[currentScenarioIndex] || recommendation

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
          <div className="agent-card">
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
          <div className="agent-card">
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
          </div>

          <div className="lap-display">
            <div className="lap-label">CURRENT LAP</div>
            <div className="lap-number">{currentLap || '--'}<span>/78</span></div>
          </div>

          {/* Swipable Scenario Carousel */}
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
                    <div key={index} className="recommendation-box">
                      <div className="rec-header">
                        <span className="rec-label">
                          SCENARIO {index + 1}/{scenarios.length}
                        </span>
                        <span className={`rec-urgency ${scenario?.urgency?.toLowerCase() || 'low'}`}>
                          {scenario?.urgency || 'LOW'}
                        </span>
                      </div>

                      <div className="rec-type">{scenario.recommendation_type || 'ANALYZING'}</div>
                      <div className="rec-message">Lap {scenario.lap_number} Strategy Update</div>
                      <div className="rec-reasoning">{scenario.reasoning || 'Analyzing race conditions...'}</div>
                      
                      <div className="rec-meta">
                        <div className="rec-confidence">
                          <span>Confidence:</span>
                          <div className="confidence-bar">
                            <div 
                              className="confidence-fill" 
                              style={{width: `${(scenario.confidence_score || 0.5) * 100}%`}}
                            ></div>
                          </div>
                          <span>{Math.round((scenario.confidence_score || 0.5) * 100)}%</span>
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
          <div className="agent-card">
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
          <span>RACE: Monaco 2024 • DRIVER: LEC • MODE: Real-time</span>
        </div>
      </div>
    </div>
  )
}

export default AgentDashboard

