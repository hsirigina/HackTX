import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import './CompetitorModal.css'

const supabase = createClient(
  'https://wkcdbbmelonvmduxkkge.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrY2RiYm1lbG9udm1kdXhra2dlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NzM2NjMsImV4cCI6MjA3NjM0OTY2M30.UADl4E7idotTLC-OSEv_kbCslpRDykhehe-E9at1Vkk'
)

function CompetitorModal({ isOpen, onClose, raceConfig = {} }) {
  if (!isOpen) return null

  const [userData, setUserData] = useState(null)
  const [competitorData, setCompetitorData] = useState(null)
  const [weatherData, setWeatherData] = useState(null)

  const generateMockData = (raceId, driver, lap) => {
    const driverStats = {
      'VER': { speed: 330, teamStrength: 0.98, consistency: 0.95, aggression: 0.9 },
      'PER': { speed: 325, teamStrength: 0.95, consistency: 0.88, aggression: 0.75 },
      'LEC': { speed: 328, teamStrength: 0.92, consistency: 0.90, aggression: 0.85 },
      'SAI': { speed: 326, teamStrength: 0.90, consistency: 0.87, aggression: 0.80 },
      'HAM': { speed: 327, teamStrength: 0.88, consistency: 0.92, aggression: 0.88 },
      'RUS': { speed: 324, teamStrength: 0.86, consistency: 0.89, aggression: 0.82 },
      'NOR': { speed: 326, teamStrength: 0.87, consistency: 0.91, aggression: 0.87 },
      'PIA': { speed: 323, teamStrength: 0.85, consistency: 0.86, aggression: 0.79 },
      'ALO': { speed: 325, teamStrength: 0.80, consistency: 0.93, aggression: 0.83 },
      'STR': { speed: 322, teamStrength: 0.78, consistency: 0.85, aggression: 0.78 }
    }

    const trackMultipliers = {
      'italy': 1.08, 'saudi_arabia': 1.05, 'azerbaijan': 1.04,
      'bahrain': 1.02, 'austria': 1.01, 'britain': 1.0,
      'spain': 0.99, 'brazil': 0.98, 'japan': 0.98,
      'monaco': 0.82, 'singapore': 0.85, 'hungary': 0.87
    }

    const stats = driverStats[driver] || { speed: 322, teamStrength: 0.75, consistency: 0.85, aggression: 0.75 }
    const trackMult = trackMultipliers[raceId] || 1.0
    const seed = driver.charCodeAt(0) + lap * 17
    const random = (Math.sin(seed) + 1) / 2
    const lapVariation = Math.sin(lap * 0.3) * 0.02 + random * 0.03
    const lapFactor = Math.sin(lap * 0.15) * (1 - stats.consistency) * 3
    const strategyFactor = (lap > 15 && lap < 45) ? Math.cos(lap * 0.1) * 2 : 0
    const baseRank = (1 - stats.teamStrength) * 15
    const position = Math.max(1, Math.min(20, Math.round(baseRank + lapFactor + strategyFactor + random * 3)))

    return {
      speed_max: stats.speed * trackMult * (1 + lapVariation),
      speed_avg: stats.speed * trackMult * 0.75 * (1 + lapVariation * 0.5),
      throttle_avg: 65 + stats.aggression * 30 + random * 5,
      throttle_max: 98 + random * 2,
      brake_avg: (1 - stats.aggression) * 15 + random * 5,
      brake_max: 95 + random * 5,
      drs_available: random > 0.6,
      position_x: 50 + lap * 2 + random * 10,
      position_y: 30 + Math.sin(lap + seed) * 5 + random * 10,
      position: position
    }
  }

  const generateMockWeather = (raceId, lap) => {
    const weatherProfiles = {
      'bahrain': { temp: 25, trackTemp: 45, wind: 3.5, rain: false },
      'monaco': { temp: 22, trackTemp: 35, wind: 2.0, rain: false },
      'britain': { temp: 18, trackTemp: 28, wind: 5.5, rain: Math.random() > 0.7 },
      'singapore': { temp: 30, trackTemp: 40, wind: 1.5, rain: Math.random() > 0.8 },
      'belgium': { temp: 19, trackTemp: 30, wind: 4.0, rain: Math.random() > 0.6 },
      'brazil': { temp: 28, trackTemp: 42, wind: 2.5, rain: Math.random() > 0.5 },
      'abu_dhabi': { temp: 29, trackTemp: 44, wind: 3.0, rain: false },
      'japan': { temp: 21, trackTemp: 32, wind: 2.8, rain: Math.random() > 0.7 }
    }

    const profile = weatherProfiles[raceId] || { temp: 24, trackTemp: 38, wind: 3.0, rain: false }

    return {
      air_temp: profile.temp + Math.random() * 2,
      track_temp: profile.trackTemp + Math.random() * 3,
      wind_speed: profile.wind + Math.random() * 1.5,
      rainfall: profile.rain
    }
  }

  useEffect(() => {
    const fetchRaceData = async () => {
      if (!raceConfig.selectedRace) return

      const raceId = raceConfig.selectedRace.id || 'bahrain'
      const currentLap = raceConfig.currentLap || 0
      const competitorDriver = raceConfig.selectedDriver || 'VER'

      // Only fetch if race has started (currentLap > 0)
      if (currentLap === 0) {
        // Race hasn't started, clear data
        setUserData(null)
        setCompetitorData(null)
        setWeatherData(null)
        return
      }

      if (raceId === 'bahrain') {
        try {
          const { data: userTelem } = await supabase
            .from('driver_telemetry')
            .select('*')
            .eq('race_id', raceId)
            .eq('driver_number', 1)
            .eq('lap_number', currentLap)
            .single()

          if (userTelem) setUserData(userTelem)

          const { data: compTelem } = await supabase
            .from('driver_telemetry')
            .select('*')
            .eq('race_id', raceId)
            .eq('driver_name', competitorDriver)
            .eq('lap_number', currentLap)
            .single()

          if (compTelem) {
            setCompetitorData(compTelem)
          } else {
            setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
          }

          const { data: weather } = await supabase
            .from('weather_data')
            .select('*')
            .eq('race_id', raceId)
            .eq('lap_number', currentLap)
            .single()

          if (weather) {
            setWeatherData(weather)
          } else {
            setWeatherData(generateMockWeather(raceId, currentLap))
          }
        } catch (err) {
          console.error('Error fetching race data:', err)
          setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
          setWeatherData(generateMockWeather(raceId, currentLap))
        }
      } else {
        setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
        setWeatherData(generateMockWeather(raceId, currentLap))
      }
    }

    fetchRaceData()
  }, [raceConfig])

  const Tooltip = ({ children, text }) => (
    <div className="comp-tooltip">
      {children}
      <span className="comp-tooltip-text">{text}</span>
    </div>
  )

  return (
    <div className="comp-modal-overlay" onClick={onClose}>
      <div className="comp-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="comp-modal-header">
          <div className="comp-modal-title">
            <img src="/trackagent.png" alt="Competitor" style={{ width: '24px', marginRight: '10px' }} />
            COMPETITOR ANALYSIS
          </div>
          <button className="comp-close-btn" onClick={onClose}>✕</button>
        </div>

        {/* Content Grid */}
        <div className="comp-modal-content">
          {/* Left - Your Stats */}
          <div className="comp-driver-section">
            <div className="comp-section-label">YOU</div>

            {/* Car Image with Fuel Bar */}
            <div className="comp-car-fuel-container">
              <div className="comp-car-display">
                <img src="/1.png" alt="Your Car" />
              </div>
              <div className="comp-fuel-vertical">
                <div className="comp-fuel-label">FUEL</div>
                <div className="comp-fuel-bar-vertical">
                  <div className="comp-fuel-fill blue" style={{height: '60%'}}></div>
                </div>
                <div className="comp-fuel-percentage">60%</div>
                <div className="comp-fuel-icon-small blue">⛽</div>
                <div className="comp-drs-indicator blue">DRS ON</div>
              </div>
            </div>

            <Tooltip text="Current race position">
              <div className="comp-stat-large">
                <div className="comp-stat-label">POSITION</div>
                <div className="comp-stat-value-huge blue">
                  {raceConfig.raceState?.position ? `P${raceConfig.raceState.position}` : '--'}
                </div>
              </div>
            </Tooltip>

            <Tooltip text="X-axis position on track">
              <div className="comp-stat-row">
                <span className="comp-stat-label">LATITUDE</span>
                <span className="comp-stat-value">{userData?.position_x?.toFixed(3) || '43.730'}</span>
              </div>
            </Tooltip>

            <Tooltip text="Y-axis position on track">
              <div className="comp-stat-row">
                <span className="comp-stat-label">LONGITUDE</span>
                <span className="comp-stat-value">{userData?.position_y?.toFixed(5) || '9.29103'}</span>
              </div>
            </Tooltip>

            <Tooltip text="Maximum speed reached this lap">
              <div className="comp-stat-box blue-border">
                <div className="comp-stat-label">TOP SPEED</div>
                <div className="comp-stat-value-big">{userData?.speed_max?.toFixed(0) || '287'} km/h</div>
              </div>
            </Tooltip>

            <Tooltip text="Average speed across the lap">
              <div className="comp-stat-box blue-border">
                <div className="comp-stat-label">AVG PACE</div>
                <div className="comp-stat-value-big">{userData?.speed_avg?.toFixed(0) || '245'} km/h</div>
              </div>
            </Tooltip>

            <Tooltip text="Number of laps on current tire set">
              <div className="comp-stat-row">
                <span className="comp-stat-label">TIRE AGE</span>
                <span className="comp-stat-value">{raceConfig.raceState?.tireAge || 8} laps</span>
              </div>
            </Tooltip>

            <Tooltip text="Current tire type (Soft/Medium/Hard)">
              <div className="comp-stat-row">
                <span className="comp-stat-label">COMPOUND</span>
                <span className="comp-stat-value">{raceConfig.raceState?.tireCompound || 'SOFT'}</span>
              </div>
            </Tooltip>

            <Tooltip text="Throttle pedal position percentage">
              <div className="comp-stat-row">
                <span className="comp-stat-label">THROTTLE</span>
                <span className="comp-stat-value">{userData?.throttle_avg?.toFixed(1) || '100.0'}%</span>
              </div>
            </Tooltip>

            <Tooltip text="Brake pressure applied">
              <div className="comp-stat-row">
                <span className="comp-stat-label">BRAKE</span>
                <span className="comp-stat-value">{userData?.brake_avg?.toFixed(1) || '8.5'}%</span>
              </div>
            </Tooltip>
          </div>

          {/* Center - Weather & Track */}
          <div className="comp-center-section">
            <div className="comp-section-label">RACE CONDITIONS</div>

            {/* Speed Comparison Graph */}
            <div className="comp-telemetry-chart">
              <svg viewBox="0 0 1000 150" className="comp-chart-svg">
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
              <div className="comp-chart-legend">
                <span style={{color: '#00bfff'}}>● YOU</span>
                <span style={{color: '#ffd700'}}>● {raceConfig.selectedDriver || 'COMPETITOR'}</span>
              </div>
            </div>

            <div className="comp-weather-box">
              <div className="comp-weather-condition">{weatherData?.rainfall ? '🌧️ RAINY' : '☁️ CLOUDY'}</div>

              <Tooltip text="Ambient air temperature">
                <div className="comp-weather-stat">
                  <span className="comp-weather-label">AIR TEMP</span>
                  <span className="comp-weather-value">{weatherData?.air_temp?.toFixed(0) || '25'}°C</span>
                </div>
              </Tooltip>

              <Tooltip text="Track surface temperature affects tire grip">
                <div className="comp-weather-stat">
                  <span className="comp-weather-label">TRACK TEMP</span>
                  <span className="comp-weather-value">{weatherData?.track_temp?.toFixed(0) || '45'}°C</span>
                </div>
              </Tooltip>

              <Tooltip text="Wind speed affecting car stability">
                <div className="comp-weather-stat">
                  <span className="comp-weather-label">WIND</span>
                  <span className="comp-weather-value">{weatherData?.wind_speed?.toFixed(1) || '3.5'} m/s</span>
                </div>
              </Tooltip>
            </div>

            <div className="comp-telemetry-section">
              <div className="comp-section-sublabel">RAW TELEMETRY</div>

              <Tooltip text="Car velocity - average speed">
                <div className="comp-telem-row">
                  <span className="comp-telem-label">vCar</span>
                  <span className="comp-telem-blue">{userData?.speed_avg?.toFixed(1) || '259.3'}</span>
                  <span className="comp-telem-yellow">{competitorData?.speed_avg?.toFixed(1) || '258.4'}</span>
                  <span className="comp-telem-unit">kph</span>
                </div>
              </Tooltip>

              <Tooltip text="Throttle pedal position percentage">
                <div className="comp-telem-row">
                  <span className="comp-telem-label">Throttle</span>
                  <span className="comp-telem-blue">{userData?.throttle_avg?.toFixed(1) || '100.0'}</span>
                  <span className="comp-telem-yellow">{competitorData?.throttle_avg?.toFixed(1) || '98.5'}</span>
                  <span className="comp-telem-unit">%</span>
                </div>
              </Tooltip>

              <Tooltip text="Brake pressure applied">
                <div className="comp-telem-row">
                  <span className="comp-telem-label">Brake</span>
                  <span className="comp-telem-blue">{userData?.brake_avg?.toFixed(1) || '8.5'}</span>
                  <span className="comp-telem-yellow">{competitorData?.brake_avg?.toFixed(1) || '7.2'}</span>
                  <span className="comp-telem-unit">%</span>
                </div>
              </Tooltip>
            </div>

            <Tooltip text="Optimal lap range to pit for fresh tires">
              <div className="comp-pit-window">
                <div className="comp-section-sublabel">PIT WINDOW</div>
                <div className="comp-pit-laps">Laps 36-39</div>
              </div>
            </Tooltip>

            {/* Tire Visualization */}
            <div className="comp-tire-visual">
              <div className="comp-section-sublabel">TIRE COMPARISON</div>
              <div className="comp-tire-row">
                <div className="comp-tire-box blue-tire">
                  <div className="comp-tire-circle">
                    <div className="comp-tire-laps">{raceConfig.raceState?.tireAge || 8}</div>
                    <div className="comp-tire-label">LAPS</div>
                  </div>
                  <div className="comp-tire-name">YOU</div>
                </div>
                <div className="comp-tire-box yellow-tire">
                  <div className="comp-tire-circle">
                    <div className="comp-tire-laps">11</div>
                    <div className="comp-tire-label">LAPS</div>
                  </div>
                  <div className="comp-tire-name">{raceConfig.selectedDriver || 'COMP'}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right - Competitor Stats */}
          <div className="comp-driver-section">
            <div className="comp-section-label">{raceConfig.selectedDriver || 'COMPETITOR'}</div>

            {/* Car Image with Fuel Bar */}
            <div className="comp-car-fuel-container">
              <div className="comp-car-display">
                <img src="/2.png" alt="Competitor Car" />
              </div>
              <div className="comp-fuel-vertical">
                <div className="comp-fuel-label">FUEL</div>
                <div className="comp-fuel-bar-vertical">
                  <div className="comp-fuel-fill yellow" style={{height: '90%'}}></div>
                </div>
                <div className="comp-fuel-percentage">90%</div>
                <div className="comp-fuel-icon-small yellow">⚡</div>
                <div className="comp-drs-indicator yellow">{competitorData?.drs_available ? 'DRS AVAIL' : 'NO DRS'}</div>
              </div>
            </div>

            <Tooltip text="Current race position">
              <div className="comp-stat-large">
                <div className="comp-stat-label">POSITION</div>
                <div className="comp-stat-value-huge yellow">
                  {competitorData?.position ? `P${competitorData.position}` : '--'}
                </div>
              </div>
            </Tooltip>

            <Tooltip text="X-axis position on track">
              <div className="comp-stat-row">
                <span className="comp-stat-label">LATITUDE</span>
                <span className="comp-stat-value">{competitorData?.position_x?.toFixed(3) || '124.052'}</span>
              </div>
            </Tooltip>

            <Tooltip text="Y-axis position on track">
              <div className="comp-stat-row">
                <span className="comp-stat-label">LONGITUDE</span>
                <span className="comp-stat-value">{competitorData?.position_y?.toFixed(5) || '9.28070'}</span>
              </div>
            </Tooltip>

            <Tooltip text="Maximum speed reached this lap">
              <div className="comp-stat-box yellow-border">
                <div className="comp-stat-label">TOP SPEED</div>
                <div className="comp-stat-value-big">{competitorData?.speed_max?.toFixed(0) || '291'} km/h</div>
              </div>
            </Tooltip>

            <Tooltip text="Average speed across the lap">
              <div className="comp-stat-box yellow-border">
                <div className="comp-stat-label">AVG PACE</div>
                <div className="comp-stat-value-big">{competitorData?.speed_avg?.toFixed(0) || '248'} km/h</div>
              </div>
            </Tooltip>

            <Tooltip text="Number of laps on current tire set">
              <div className="comp-stat-row">
                <span className="comp-stat-label">TIRE AGE</span>
                <span className="comp-stat-value">11 laps</span>
              </div>
            </Tooltip>

            <Tooltip text="Current tire type (Soft/Medium/Hard)">
              <div className="comp-stat-row">
                <span className="comp-stat-label">COMPOUND</span>
                <span className="comp-stat-value">MEDIUM</span>
              </div>
            </Tooltip>

            <Tooltip text="Throttle pedal position percentage">
              <div className="comp-stat-row">
                <span className="comp-stat-label">THROTTLE</span>
                <span className="comp-stat-value">{competitorData?.throttle_avg?.toFixed(1) || '98.5'}%</span>
              </div>
            </Tooltip>

            <Tooltip text="Brake pressure applied">
              <div className="comp-stat-row">
                <span className="comp-stat-label">BRAKE</span>
                <span className="comp-stat-value">{competitorData?.brake_avg?.toFixed(1) || '7.2'}%</span>
              </div>
            </Tooltip>

            <Tooltip text="Drag Reduction System status">
              <div className="comp-stat-row">
                <span className="comp-stat-label">DRS</span>
                <span className="comp-stat-value">{competitorData?.drs_available ? 'AVAILABLE' : 'NO DRS'}</span>
              </div>
            </Tooltip>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CompetitorModal
