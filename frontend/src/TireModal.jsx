import { useState, useEffect } from 'react'
import './TireModal.css'

function TireModal({ isOpen, onClose, tireData }) {
  const [animateIn, setAnimateIn] = useState(false)
  const [animateWear, setAnimateWear] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setAnimateIn(true)
      // Trigger wear bar animation after modal opens
      setTimeout(() => setAnimateWear(true), 300)
    } else {
      setAnimateWear(false)
    }
  }, [isOpen])

  const handleClose = () => {
    setAnimateIn(false)
    setTimeout(onClose, 300)
  }

  if (!isOpen) return null

  // Mock data for tire metrics - McLaren style
  const mockData = {
    compound: tireData?.compound || 'MEDIUM',
    age: tireData?.age || 24,
    degradation: tireData?.degradation || '+1.2s',
    laps: 8,
    nextPitWindow: '36-39',
    
    // Tire pressure data
    tires: [
      { position: 'FL', psi: 22.5, temp: 98, wear: 72, bar: 1.03 },
      { position: 'FR', psi: 22.3, temp: 96, wear: 75, bar: 1.02 },
      { position: 'RL', psi: 21.8, temp: 102, wear: 68, bar: 1.03 },
      { position: 'RR', psi: 21.9, temp: 101, wear: 70, bar: 1.04 }
    ],
    
    // Telemetry data
    avgPressure: 22.1,
    avgTemp: 99,
    avgWear: 71,
    pitStopTime: '3.024 sec',
    onLap: 21
  }

  const getCompoundColor = (compound) => {
    switch(compound) {
      case 'SOFT': return '#ff0040'
      case 'MEDIUM': return '#ffd700'
      case 'HARD': return '#ffffff'
      default: return '#00bfff'
    }
  }

  return (
    <div className={`tire-modal-overlay ${animateIn ? 'active' : ''}`} onClick={handleClose}>
      <div className={`tire-modal-container ${animateIn ? 'active' : ''}`} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="tire-modal-header">
          <div className="tire-modal-title">
            <span className="tire-icon"><img src="/tireagent.png" alt="Tire Agent" /></span>
            TIRE DATA ANALYSIS
          </div>
          <button className="tire-close-btn" onClick={handleClose}>✕</button>
        </div>

        {/* Content Grid - McLaren Style */}
        <div className="tire-modal-content">
          {/* Left Side - Tire Visual & Info */}
          <div className="tire-visual-section">
            <div className="tire-stats-header">
              <div className="stat-item">
                <div className="stat-label">TYRES AND LAPS RACED</div>
                <div className="stat-value-large">{mockData.laps} <span className="stat-unit">LAPS</span></div>
              </div>
              <div className="stat-item">
                <div className="stat-label">NEXT PIT WINDOW / LAPS</div>
                <div className="stat-value-large">{mockData.nextPitWindow}</div>
              </div>
            </div>

            {/* Tire Image */}
            <div className="tire-image-container">
              <img src="/tire.png" alt="F1 Tire" className="tire-image-spin" />
            </div>

            {/* Circular Gauges - McLaren Style */}
            <div className="circular-gauges">
              {mockData.tires.map((tire, idx) => (
                <div key={tire.position} className="gauge-container">
                  <div className="gauge-wrapper">
                    <svg viewBox="0 0 120 120" className="gauge-svg">
                      {/* Background circle */}
                      <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3"/>
                      {/* Progress circle */}
                      <circle 
                        cx="60" 
                        cy="60" 
                        r="52" 
                        fill="none" 
                        stroke={tire.bar > 1.02 ? '#00bfff' : '#667788'}
                        strokeWidth="6"
                        strokeDasharray="327"
                        strokeDashoffset={327 - (327 * (tire.bar - 0.9) / 0.2)}
                        strokeLinecap="round"
                        transform="rotate(-90 60 60)"
                        className="gauge-progress"
                      />
                    </svg>
                    <div className="gauge-content">
                      <div className="gauge-position">{tire.position}</div>
                      <div className="gauge-value">{tire.bar.toFixed(2)}</div>
                      <div className="gauge-unit">bar</div>
                    </div>
                  </div>
                  <div className="gauge-label">{tire.bar.toFixed(2)} bar</div>
                </div>
              ))}
            </div>

            {/* Pit Stop Time */}
            <div className="pit-stop-info">
              <div className="pit-label">PIT STOP TIMES</div>
              <div className="pit-time">{mockData.pitStopTime}</div>
              <div className="pit-lap">ON LAP {mockData.onLap}</div>
            </div>
          </div>

          {/* Right Side - Telemetry Data */}
          <div className="telemetry-section">
            {/* Tire Pressure and Life Grid */}
            <div className="data-grid-mclaren">
              <div className="data-section">
                <div className="section-title">TYRE PRESSURE AND LIFE</div>
                <div className="tire-grid-layout">
                  {mockData.tires.map((tire) => (
                    <div key={tire.position} className="tire-data-box">
                      <div className="tire-position-label">{tire.position}</div>
                      <div className="tire-pressure-value">{tire.psi.toFixed(1)}</div>
                      <div className="tire-pressure-label">bar</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* RAW Telemetry Data */}
              <div className="data-section">
                <div className="section-title">RAW TELEMETRY DATA</div>
                <div className="telemetry-data-grid">
                  <div className="telemetry-row">
                    <span className="telem-label">vCar</span>
                    <span className="telem-value cyan">={mockData.avgPressure.toFixed(1)} bar</span>
                  </div>
                  <div className="telemetry-row">
                    <span className="telem-label">nGear</span>
                    <span className="telem-value cyan">=6</span>
                  </div>
                  <div className="telemetry-row">
                    <span className="telem-label">rThrottlePedal</span>
                    <span className="telem-value cyan">=100.0 %</span>
                  </div>
                  <div className="telemetry-row">
                    <span className="telem-label">pBrakeF</span>
                    <span className="telem-value cyan">=0.0 %</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Temperature Heatmap */}
            <div className="temp-heatmap-section">
              <div className="section-title">TYRE TEMPERATURE (°C)</div>
              <div className="temp-heatmap">
                {mockData.tires.map((tire) => (
                  <div key={tire.position} className="temp-indicator">
                    <div className={`temp-circle-mclaren ${tire.temp > 100 ? 'temp-hot' : 'temp-cool'}`}>
                      <div className="temp-pos">{tire.position}</div>
                      <div className="temp-val">
                        {tire.temp}°
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Wear Analysis */}
            <div className="wear-analysis-section">
              <div className="section-title">TYRE WEAR ANALYSIS (%)</div>
              <div className="wear-bars">
                {mockData.tires.map((tire) => (
                  <div key={tire.position} className="wear-bar-item">
                    <div className="wear-bar-label">{tire.position}</div>
                    <div className="wear-bar-track">
                      <div 
                        className="wear-bar-fill"
                        style={{
                          width: animateWear ? `${tire.wear}%` : '0%'
                        }}
                      >
                        <div className="wear-bar-value">{tire.wear}%</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Data Rate Info */}
            <div className="data-rate-section">
              <div className="section-title">DATA RATE</div>
              <div className="data-rate-value">
                <span className="rate-num">=3.3</span>
                <span className="rate-unit">MB/sec</span>
              </div>
              <div className="data-status">Transferring</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TireModal

