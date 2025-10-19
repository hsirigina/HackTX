import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import './RaceComparison.css'

function RaceComparison() {
  const [comparisonData, setComparisonData] = useState(null)
  const [currentLap, setCurrentLap] = useState(0)
  const [totalLaps, setTotalLaps] = useState(78)

  // Poll Supabase for race comparison data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data, error } = await supabase
          .from('race_comparison')
          .select('*')
          .order('lap_number', { ascending: false })
          .limit(1)

        if (error) throw error

        if (data && data.length > 0) {
          setComparisonData(data[0])
          setCurrentLap(data[0].lap_number)
        }
      } catch (error) {
        console.error('Error fetching comparison data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  // Calculate car position around track (circular)
  const getCarPosition = (lapProgress) => {
    const angle = (lapProgress * 2 * Math.PI) - Math.PI / 2 // Start at top
    return {
      top: `${50 + 35 * Math.sin(angle)}%`,
      left: `${50 + 35 * Math.cos(angle)}%`
    }
  }

  const lapProgress = comparisonData ? (comparisonData.lap_number % 1) : 0
  const timeDiff = comparisonData ? comparisonData.time_difference : 0
  const carLengths = Math.abs(timeDiff * 2).toFixed(1) // Rough conversion

  return (
    <div className="race-comparison">
      {/* Header */}
      <div className="comparison-header">
        <div className="header-left">F1 STRATEGY COMPARISON</div>
        <div className="header-right">AI vs BASELINE • LIVE SIMULATION</div>
      </div>

      {/* Progress Bar */}
      <div className="race-progress">
        <div className="progress-label">LAP {currentLap} / {totalLaps}</div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{width: `${(currentLap / totalLaps) * 100}%`}}
          />
        </div>
      </div>

      {/* Time Difference Banner */}
      <div className={`time-difference ${timeDiff > 0 ? 'ai-ahead' : 'ai-behind'}`}>
        <div className="diff-label">TIME DIFFERENCE</div>
        <div className="diff-value">
          {timeDiff > 0 ? '+' : ''}{Math.abs(timeDiff).toFixed(3)}s
        </div>
        <div className="diff-description">
          {timeDiff > 0 
            ? `AI Strategy ahead by ${carLengths} car lengths` 
            : timeDiff < 0 
            ? `AI Strategy behind by ${carLengths} car lengths`
            : 'Equal pace'}
        </div>
      </div>

      {/* Split-Screen Tracks */}
      <div className="split-screen">
        {/* AI Strategy Side */}
        <div className="race-view ai-strategy">
          <div className="view-header">
            <div className="view-title">AI STRATEGY</div>
            <div className="view-badge">OPTIMIZED</div>
          </div>

          <div className="track-container">
            <div className="track-oval">
              <div className="start-finish-line">START/FINISH</div>
              
              {/* Animated Car */}
              <div 
                className="race-car ai-car"
                style={getCarPosition(lapProgress)}
              >
                🏎️
              </div>
            </div>
          </div>

          <div className="race-stats">
            <div className="stat-item">
              <div className="stat-label">CUMULATIVE TIME</div>
              <div className="stat-value ai-color">
                {comparisonData?.ai_cumulative_time?.toFixed(3) || '0.000'}s
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">TIRE COMPOUND</div>
              <div className="stat-value">
                {comparisonData?.ai_tire_compound || 'HARD'}
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">TIRE AGE</div>
              <div className="stat-value">
                {comparisonData?.ai_tire_age || 0} laps
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">PIT STOPS</div>
              <div className="stat-value">
                {comparisonData?.ai_has_pitted ? `Yes (Lap ${comparisonData.ai_pit_lap})` : 'No'}
              </div>
            </div>
          </div>
        </div>

        {/* VS Divider */}
        <div className="vs-divider">
          <div className="vs-text">VS</div>
        </div>

        {/* Baseline Side */}
        <div className="race-view baseline">
          <div className="view-header">
            <div className="view-title">BASELINE</div>
            <div className="view-badge">NO STRATEGY</div>
          </div>

          <div className="track-container">
            <div className="track-oval">
              <div className="start-finish-line">START/FINISH</div>
              
              {/* Animated Car */}
              <div 
                className="race-car baseline-car"
                style={getCarPosition(lapProgress)}
              >
                🏎️
              </div>
            </div>
          </div>

          <div className="race-stats">
            <div className="stat-item">
              <div className="stat-label">CUMULATIVE TIME</div>
              <div className="stat-value baseline-color">
                {comparisonData?.baseline_cumulative_time?.toFixed(3) || '0.000'}s
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">TIRE COMPOUND</div>
              <div className="stat-value">
                {comparisonData?.baseline_tire_compound || 'HARD'}
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">TIRE AGE</div>
              <div className="stat-value">
                {comparisonData?.baseline_tire_age || 0} laps
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">PIT STOPS</div>
              <div className="stat-value">
                {comparisonData?.baseline_has_pitted ? `Yes (Lap ${comparisonData.baseline_pit_lap})` : 'No'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="comparison-footer">
        <span>RACE: Monaco 2024 • DRIVER: LEC • MODE: Real-time Comparison</span>
      </div>
    </div>
  )
}

export default RaceComparison

