import { useState, useEffect } from 'react'
import './LaptimeModal.css'

function LaptimeModal({ isOpen, onClose, laptimeData, selectedRace }) {
  const [animateIn, setAnimateIn] = useState(false)
  const [animateBars, setAnimateBars] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setAnimateIn(true)
      // Trigger bar animations after modal opens
      setTimeout(() => setAnimateBars(true), 300)
    } else {
      setAnimateBars(false)
    }
  }, [isOpen])

  const handleClose = () => {
    setAnimateIn(false)
    setTimeout(onClose, 300)
  }

  if (!isOpen) return null

  // Mock data for laptime metrics
  const mockData = {
    currentLap: laptimeData?.current_time || '1:32.456',
    avgLap: laptimeData?.avg_time || '1:32.678',
    bestLap: '1:31.447',
    trend: laptimeData?.trend || 'BALANCED',

    // Sector times
    sectors: [
      { name: 'SECTOR 1', time: '29.234', percent: 85, color: 'linear-gradient(90deg, #00bfff, #0088cc)' },
      { name: 'SECTOR 2', time: '36.789', percent: 92, color: 'linear-gradient(90deg, #4caf50, #2e7d32)' },
      { name: 'SECTOR 3', time: '30.521', percent: 88, color: 'linear-gradient(90deg, #ffc107, #f57c00)' }
    ],

    // Key corners
    corners: [
      { num: 'T1', name: 'First Corner', entry: 287, apex: 95 },
      { num: 'T4', name: 'Fast Left', entry: 256, apex: 178 },
      { num: 'T10', name: 'Hairpin', entry: 223, apex: 72 },
      { num: 'T13', name: 'Final Chicane', entry: 267, apex: 142 }
    ],

    // Track info
    trackLength: '5.412',
    totalCorners: 15,
    drsZones: 3,
    lapRecord: '1:31.447 (VER)',

    // Pace comparison
    drivers: [
      { name: 'YOU', time: laptimeData?.avg_time || '1:32.456', percent: 100, color: 'linear-gradient(90deg, #ffd700, #ff8c00)' },
      { name: 'VER', time: '1:32.236', percent: 98, color: 'linear-gradient(90deg, #00bfff, #0066cc)' },
      { name: 'LEC', time: '1:32.456', percent: 96, color: 'linear-gradient(90deg, #dc143c, #8b0000)' },
      { name: 'NOR', time: '1:32.678', percent: 95, color: 'linear-gradient(90deg, #ff8c00, #ff6347)' }
    ]
  }

  return (
    <div className={`laptime-modal-overlay ${animateIn ? 'active' : ''}`} onClick={handleClose}>
      <div className={`laptime-modal-container ${animateIn ? 'active' : ''}`} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="laptime-modal-header">
          <div className="laptime-modal-title">
            <span className="laptime-icon"><img src="/stopwatch agent.png" alt="Laptime Agent" /></span>
            LAPTIME ANALYSIS
          </div>
          <button className="laptime-close-btn" onClick={handleClose}>✕</button>
        </div>

        {/* Content Grid */}
        <div className="laptime-modal-content">
          {/* Left Side - Current Performance */}
          <div className="laptime-performance-section">
            {/* Current Stats */}
            <div className="laptime-stats-header">
              <div className="laptime-stat-item">
                <div className="laptime-stat-label">CURRENT LAP TIME</div>
                <div className="laptime-stat-value-large">{mockData.currentLap}<span className="laptime-stat-unit">s</span></div>
              </div>
              <div className="laptime-stat-item">
                <div className="laptime-stat-label">BEST LAP TIME</div>
                <div className="laptime-stat-value-large">{mockData.bestLap}<span className="laptime-stat-unit">s</span></div>
              </div>
            </div>

            {/* Track Info */}
            <div className="track-info-grid">
              <div className="track-info-box">
                <div className="info-text">
                  <div className="info-label">Circuit Length</div>
                  <div className="info-value">{mockData.trackLength} km</div>
                </div>
              </div>
              <div className="track-info-box">
                <div className="info-text">
                  <div className="info-label">Total Corners</div>
                  <div className="info-value">{mockData.totalCorners} Turns</div>
                </div>
              </div>
              <div className="track-info-box">
                <div className="info-text">
                  <div className="info-label">DRS Zones</div>
                  <div className="info-value">{mockData.drsZones} Zones</div>
                </div>
              </div>
              <div className="track-info-box">
                <div className="info-text">
                  <div className="info-label">Lap Record</div>
                  <div className="info-value">{mockData.lapRecord}</div>
                </div>
              </div>
            </div>

            {/* Circuit Map */}
            <div className="circuit-map-section">
              <div className="section-title">CIRCUIT MAP</div>
              <div className="circuit-image-container">
                {selectedRace ? (
                  <img 
                    src={`/tracks/${selectedRace.id}.svg`} 
                    alt={selectedRace.name || "Circuit Map"} 
                    className="circuit-image"
                    style={{
                      filter: 'drop-shadow(0 0 10px rgba(0, 191, 255, 0.3))'
                    }}
                    onError={(e) => {
                      console.error(`Failed to load track: /tracks/${selectedRace.id}.svg`)
                      e.target.src = "/track1.png" // Fallback to generic image
                    }}
                  />
                ) : (
                  <img src="/track1.png" alt="Circuit Map" className="circuit-image" />
                )}
              </div>
            </div>
          </div>

          {/* Right Side - Corners & Pace */}
          <div className="laptime-analysis-section">
            {/* Key Corners */}
            <div className="corners-section">
              <div className="section-title">KEY CORNERS</div>
              <div className="corners-grid">
                {mockData.corners.map((corner, idx) => (
                  <div key={idx} className="corner-box">
                    <div className="corner-number">{corner.num}</div>
                    <div className="corner-details">
                      <div className="corner-name">{corner.name}</div>
                      <div className="corner-speeds">
                        <div className="speed-item">
                          <span className="speed-label">Entry: </span>
                          <span className="speed-value">{corner.entry} km/h</span>
                        </div>
                        <div className="speed-item">
                          <span className="speed-label">Apex: </span>
                          <span className="speed-value">{corner.apex} km/h</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pace Comparison */}
            <div className="pace-comparison-section">
              <div className="section-title">PACE COMPARISON</div>
              <div className="pace-bars">
                {mockData.drivers.map((driver, idx) => (
                  <div key={idx} className="pace-item">
                    <div className="pace-driver-name">{driver.name}</div>
                    <div className="pace-bar-track">
                      <div
                        className="pace-bar-fill"
                        style={{
                          width: animateBars ? `${driver.percent}%` : '0%',
                          background: driver.color
                        }}
                      >
                        <span className="pace-time-value">{driver.time}s</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Circuit Name */}
            <div className="circuit-name-section">
              <div className="circuit-label">{selectedRace?.name?.toUpperCase() || 'BAHRAIN INTERNATIONAL CIRCUIT'}</div>
              <div className="circuit-location">Sakhir, Bahrain</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LaptimeModal
