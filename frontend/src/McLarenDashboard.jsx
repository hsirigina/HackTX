import { useState, useEffect } from 'react'
import './McLarenDashboard.css'

function McLarenDashboard() {
  return (
    <div className="mclaren-dashboard">
      {/* Top Header */}
      <div className="top-header">
        <div className="header-left">VODAFONE McLAREN MERCEDES</div>
        <div className="header-right">VODAFONE McLAREN MERCEDES</div>
      </div>

      {/* Main Container */}
      <div className="main-container">
        {/* Left Driver Section - Jenson Button */}
        <div className="driver-column left-driver">
          <div className="driver-info-header">
            <div className="label">DRIVER</div>
            <div className="label">POSITION</div>
          </div>

          <div className="driver-name-section">
            <div className="driver-name-left">
              <h2>JENSON BUTTON</h2>
              <div className="driver-badge blue">3</div>
              <div className="driver-delta blue">-1.075</div>
            </div>
            <div className="position-huge">2</div>
          </div>

          <div className="driver-stats">
            <div className="stat-line">
              <span className="stat-label">LATITUDE</span>
              <span className="stat-value">43.7301</span>
            </div>
            <div className="stat-line">
              <span className="stat-label">LONGITUDE</span>
              <span className="stat-value">9.29103</span>
            </div>
          </div>

          <div className="car-display">
            <img src="/1.png" alt="Jenson Button Car" />
          </div>

          <div className="safety-status">
            <div className="status-label">ON SAFETY CAR</div>
            <div className="status-action blue">GO TO PIT</div>
          </div>

          <div className="fuel-section">
            <div className="fuel-icon blue">⛽</div>
            <div className="fuel-info">
              <div className="fuel-lap">LAP 51</div>
              <div className="fuel-bar-container">
                <div className="fuel-bar blue" style={{width: '60%'}}></div>
              </div>
              <div className="fuel-status">DRS ON</div>
            </div>
          </div>

          <div className="zone-text">In the Zone</div>

          <div className="telemetry-row">
            <div className="telem-box">
              <div className="telem-label">TIRE LIFE</div>
              <div className="telem-value">123.052</div>
            </div>
            <div className="telem-box">
              <div className="telem-label">TIME</div>
              <div className="telem-value">1:22.565</div>
            </div>
          </div>

          <div className="speed-box">
            <div className="speed-label">TOP LAP SPEED</div>
            <div className="speed-big">287<span>km/h</span></div>
            <div className="pace-row">
              <span>PACE</span>
              <span>-312km/h</span>
            </div>
          </div>

          <div className="engine-box">
            <div className="engine-label">ENGINE</div>
            <div className="engine-gauge">
              <div className="engine-bar blue"></div>
              <div className="engine-number">6</div>
            </div>
            <div className="engine-details">
              <div className="detail-row">
                <span>BRAKES</span>
                <div className="detail-bars blue"></div>
              </div>
              <div className="detail-row">
                <span>THROTTLE</span>
                <div className="detail-bars blue"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Center Section - Track & Weather */}
        <div className="center-column">
          <div className="track-header">
            <div className="location">AUTODROMO DI MONZA</div>
          </div>

          <div className="lap-weather-row">
            <div className="lap-counter">
              <div className="lap-label">LAP</div>
              <div className="lap-number">30/53</div>
            </div>

            <div className="weather-box">
              <div className="weather-condition">Cloudy</div>
              <div className="temperature">25°<span>C</span></div>
              <div className="wind-info">
                <span className="wind-label">WIND</span>
                <span className="wind-value">3.5m/s ↓</span>
              </div>
              <div className="track-temp-info">
                <span className="temp-label">TRACK TEMP</span>
                <span className="temp-value">45°C</span>
              </div>
            </div>
          </div>

          <div className="track-map">
            <svg viewBox="0 0 800 400" className="track-svg">
              {/* Track outline */}
              <path 
                d="M 250,100 
                   L 550,100 
                   Q 650,100 650,200
                   L 650,280
                   Q 650,350 550,350
                   L 250,350
                   Q 150,350 150,280
                   L 150,200
                   Q 150,100 250,100 Z" 
                fill="none" 
                stroke="#3a4555" 
                strokeWidth="60"
              />
              <path 
                d="M 250,100 
                   L 550,100 
                   Q 650,100 650,200
                   L 650,280
                   Q 650,350 550,350
                   L 250,350
                   Q 150,350 150,280
                   L 150,200
                   Q 150,100 250,100 Z" 
                fill="none" 
                stroke="#2a5580" 
                strokeWidth="30"
              />
              
              {/* Sector markers */}
              <text x="280" y="70" fill="#667788" fontSize="14">06</text>
              <text x="370" y="70" fill="#667788" fontSize="14">07</text>
              <text x="500" y="70" fill="#667788" fontSize="14">08</text>
              <text x="680" y="130" fill="#667788" fontSize="14">09</text>
              <text x="680" y="240" fill="#667788" fontSize="14">10</text>
              <text x="680" y="320" fill="#667788" fontSize="14">11</text>
              <text x="500" y="390" fill="#667788" fontSize="14">01</text>
              <text x="370" y="390" fill="#667788" fontSize="14">02</text>
              <text x="240" y="390" fill="#667788" fontSize="14">03</text>
              <text x="100" y="320" fill="#667788" fontSize="14">04</text>
              <text x="100" y="180" fill="#667788" fontSize="14">05</text>

              {/* Car position markers */}
              <circle cx="400" cy="340" r="10" fill="#00bfff" className="car-marker">
                <animate attributeName="cx" values="400;420;400" dur="2s" repeatCount="indefinite"/>
              </circle>
              <circle cx="450" cy="340" r="10" fill="#ffd700" className="car-marker">
                <animate attributeName="cx" values="450;470;450" dur="2s" repeatCount="indefinite"/>
              </circle>
            </svg>

            <div className="drs-zone-badge">DRS ZONE</div>
          </div>

          <div className="telemetry-chart">
            <svg viewBox="0 0 1000 150" className="chart-svg">
              {/* Speed traces */}
              <path 
                d="M 0,100 Q 100,30 200,90 T 400,80 T 600,70 T 800,60 L 1000,50" 
                fill="none" 
                stroke="#00bfff" 
                strokeWidth="4"
              />
              <path 
                d="M 0,105 Q 100,35 200,95 T 400,85 T 600,75 T 800,65 L 1000,55" 
                fill="none" 
                stroke="#ffd700" 
                strokeWidth="4"
              />
              {/* Grid */}
              <line x1="0" y1="75" x2="1000" y2="75" stroke="#2a3544" strokeWidth="1"/>
            </svg>
          </div>
        </div>

        {/* Right Driver Section - Lewis Hamilton */}
        <div className="driver-column right-driver">
          <div className="driver-info-header reverse">
            <div className="label">POSITION</div>
            <div className="label">DRIVER</div>
          </div>

          <div className="driver-name-section reverse">
            <div className="position-huge">1</div>
            <div className="driver-name-right">
              <h2>LEWIS HAMILTON</h2>
              <div className="driver-badge yellow">1</div>
              <div className="driver-delta yellow">+1.075</div>
            </div>
          </div>

          <div className="driver-stats reverse">
            <div className="stat-line">
              <span className="stat-value">1:24.052</span>
              <span className="stat-label">LATITUDE</span>
            </div>
            <div className="stat-line">
              <span className="stat-value">9.28070</span>
              <span className="stat-label">LONGITUDE</span>
            </div>
          </div>

          <div className="car-display">
            <img src="/2.png" alt="Lewis Hamilton Car" />
          </div>

          <div className="safety-status reverse">
            <div className="status-action yellow">DO NOT PIT</div>
            <div className="status-label">ON SAFETY CAR</div>
          </div>

          <div className="fuel-section reverse">
            <div className="fuel-info">
              <div className="fuel-lap">END</div>
              <div className="fuel-bar-container">
                <div className="fuel-bar yellow" style={{width: '90%'}}></div>
              </div>
              <div className="fuel-status">DRS</div>
            </div>
            <div className="fuel-icon yellow">⚡</div>
          </div>

          <div className="zone-text">Not in the Zone</div>

          <div className="telemetry-row reverse">
            <div className="telem-box">
              <div className="telem-label">TIME</div>
              <div className="telem-value">1:23.781</div>
            </div>
            <div className="telem-box">
              <div className="telem-label">TIRE LIFE</div>
              <div className="telem-value">1:24.052</div>
            </div>
          </div>

          <div className="speed-box">
            <div className="speed-label">TOP LAP SPEED</div>
            <div className="speed-big">291<span>km/h</span></div>
            <div className="pace-row">
              <span>PACE</span>
              <span>-313km/h</span>
            </div>
          </div>

          <div className="engine-box">
            <div className="engine-label">ENGINE</div>
            <div className="engine-gauge">
              <div className="engine-bar yellow"></div>
              <div className="engine-number">N<sub>1</sub></div>
            </div>
            <div className="engine-details">
              <div className="detail-row">
                <span>BRAKES</span>
                <div className="detail-bars yellow"></div>
              </div>
              <div className="detail-row">
                <span>THROTTLE</span>
                <div className="detail-bars yellow"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="bottom-section">
        {/* Left Bottom */}
        <div className="bottom-left">
          <div className="section-grid">
            <div className="tire-section">
              <div className="section-title">TYRES AND LAPS PACED</div>
              <div className="tire-content">
                <div className="pirelli-logo">Pirelli</div>
                <div className="tire-circle blue">
                  <div className="tire-laps">8</div>
                  <div className="tire-label">LAPS</div>
                </div>
                <div className="tire-gauges">
                  <div className="tire-gauge">
                    <div className="gauge-label">L.Rear</div>
                    <div className="gauge-ring"></div>
                  </div>
                  <div className="tire-gauge">
                    <div className="gauge-label">L.Rear</div>
                    <div className="gauge-ring"></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="pit-window-section blue-theme">
              <div className="window-title blue">NEXT PIT WINDOW LAPS</div>
              <div className="window-laps blue-bg">36 - 39</div>
              <div className="window-stats">
                <div className="stat-group">
                  <div className="stat-name blue">PIT STOP TIMES</div>
                  <div className="stat-val blue">3:024 sec</div>
                </div>
                <div className="stat-group">
                  <div className="stat-name">OUTLAP</div>
                  <div className="stat-val">21</div>
                </div>
              </div>
            </div>

            <div className="raw-telemetry">
              <div className="section-title">RAW TELEMETRY DATA</div>
              <div className="telemetry-table">
                <div className="telem-row">
                  <span className="telem-label">vCar</span>
                  <span className="telem-blue">-259.3</span>
                  <span className="telem-yellow">+258.4</span>
                  <span className="telem-unit">kph</span>
                </div>
                <div className="telem-row">
                  <span className="telem-label">Motor</span>
                  <span className="telem-blue">-6</span>
                  <span className="telem-yellow">-N</span>
                </div>
                <div className="telem-row">
                  <span className="telem-label">rThrottle/Pedal</span>
                  <span className="telem-blue">-100.0</span>
                  <span className="telem-yellow">-0.0</span>
                  <span className="telem-unit">%</span>
                </div>
                <div className="telem-row">
                  <span className="telem-label">pRrakeΔT</span>
                  <span className="telem-blue">-8.5</span>
                  <span className="telem-yellow">-0.0</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Center Bottom */}
        <div className="bottom-center">
          <div className="data-rate-box">
            <div className="rate-title">DATA RATE</div>
            <div className="rate-bars">
              <div className="rate-bar"></div>
              <div className="rate-bar"></div>
              <div className="rate-bar"></div>
              <div className="rate-bar"></div>
              <div className="rate-bar active"></div>
            </div>
            <div className="rate-info">
              <div className="rate-status">Transferring</div>
              <div className="rate-speed">+3.3 MB/sec</div>
            </div>
          </div>
        </div>

        {/* Right Bottom */}
        <div className="bottom-right">
          <div className="section-grid reverse">
            <div className="pit-window-section yellow-theme">
              <div className="window-title yellow">NEXT PIT WINDOW LAPS</div>
              <div className="window-laps yellow-bg">35 - 38</div>
              <div className="window-stats">
                <div className="stat-group">
                  <div className="stat-name">OUTLAP</div>
                  <div className="stat-val">19</div>
                </div>
                <div className="stat-group">
                  <div className="stat-name yellow">PIT STOP TIMES</div>
                  <div className="stat-val yellow">3:174 sec</div>
                </div>
              </div>
            </div>

            <div className="tire-section">
              <div className="section-title">TIRE PRESSURE AND LIFE</div>
              <div className="tire-content reverse">
                <div className="tire-gauges">
                  <div className="tire-gauge">
                    <div className="gauge-label">L.Rear</div>
                    <div className="gauge-ring"></div>
                  </div>
                  <div className="tire-gauge">
                    <div className="gauge-label">L.Rear</div>
                    <div className="gauge-ring"></div>
                  </div>
                </div>
                <div className="tire-circle yellow">
                  <div className="tire-laps">11</div>
                  <div className="tire-label">LAPS</div>
                </div>
                <div className="pirelli-logo">Pirelli</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="timeline-section">
        <div className="timeline-left">
          <div className="timeline-title">PREVIOUS TYRES</div>
          <div className="timeline-track">
            <div className="timeline-marker" style={{left: '10%'}}>
              <div className="marker-dot blue"></div>
              <div className="marker-lap">1</div>
            </div>
            <div className="timeline-marker" style={{left: '55%'}}>
              <div className="marker-dot blue"></div>
              <div className="marker-lap">30</div>
              <div className="marker-label">PLANNED PIT 1</div>
            </div>
          </div>
        </div>

        <div className="timeline-center">
          <div className="kamm-title">KAMM DIST</div>
          <div className="kamm-bars">
            {[...Array(60)].map((_, i) => (
              <div 
                key={i} 
                className="kamm-bar" 
                style={{
                  height: i === 28 ? '50px' : i === 25 ? '40px' : Math.random() > 0.8 ? '15px' : '5px',
                  background: i === 28 ? '#ffd700' : i === 25 ? '#00bfff' : '#3a4555'
                }}
              ></div>
            ))}
          </div>
        </div>

        <div className="timeline-right">
          <div className="timeline-title">KAMM DIST</div>
          <div className="timeline-track">
            <div className="timeline-marker" style={{left: '55%'}}>
              <div className="marker-dot yellow"></div>
              <div className="marker-lap">30</div>
              <div className="marker-label">PIT WINDOW</div>
            </div>
            <div className="timeline-marker" style={{left: '80%'}}>
              <div className="marker-dot yellow"></div>
              <div className="marker-lap">45</div>
              <div className="marker-label yellow">PLANNED PIT 1</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <div className="footer-left">
          <div className="sap-badge">SAP</div>
          <div className="powered-by">Powered by HANA</div>
        </div>
        <div className="footer-right">
          <div className="race-status">RACE STATUS</div>
        </div>
      </div>
    </div>
  )
}

export default McLarenDashboard
