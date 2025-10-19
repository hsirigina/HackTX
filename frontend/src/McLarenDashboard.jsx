import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import './McLarenDashboard.css'

const supabase = createClient(
  'https://wkcdbbmelonvmduxkkge.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrY2RiYm1lbG9udm1kdXhra2dlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NzM2NjMsImV4cCI6MjA3NjM0OTY2M30.UADl4E7idotTLC-OSEv_kbCslpRDykhehe-E9at1Vkk'
)

function McLarenDashboard({ isOpen, onClose, raceConfig = {} }) {
  if (!isOpen) return null

  const [userData, setUserData] = useState(null)
  const [competitorData, setCompetitorData] = useState(null)
  const [weatherData, setWeatherData] = useState(null)

  const trackMap = {
    'bahrain': '/tracks/bahrain.svg',
    'saudi_arabia': '/tracks/saudi_arabia.svg',
    'australia': '/tracks/australia.svg',
    'azerbaijan': '/tracks/azerbaijan.svg',
    'miami': '/tracks/miami.svg',
    'monaco': '/tracks/monaco.svg',
    'spain': '/tracks/spain.svg',
    'canada': '/tracks/canada.svg',
    'austria': '/tracks/austria.svg',
    'britain': '/tracks/britain.svg',
    'hungary': '/tracks/hungary.svg',
    'belgium': '/tracks/belgium.svg',
    'netherlands': '/tracks/netherlands.svg',
    'italy': '/tracks/italy.svg',
    'singapore': '/tracks/singapore.svg',
    'japan': '/tracks/japan.svg',
    'qatar': '/tracks/qatar.svg',
    'usa': '/tracks/usa.svg',
    'mexico': '/tracks/mexico.svg',
    'brazil': '/tracks/brazil.svg',
    'las_vegas': '/tracks/las_vegas.svg',
    'abu_dhabi': '/tracks/abu_dhabi.svg',
    'china': '/tracks/china.svg',
    'imola': '/tracks/imola.svg'
  }

  const trackNames = {
    'bahrain': 'BAHRAIN INTERNATIONAL CIRCUIT',
    'saudi_arabia': 'JEDDAH CORNICHE CIRCUIT',
    'australia': 'ALBERT PARK CIRCUIT',
    'azerbaijan': 'BAKU CITY CIRCUIT',
    'miami': 'MIAMI INTERNATIONAL AUTODROME',
    'monaco': 'CIRCUIT DE MONACO',
    'spain': 'CIRCUIT DE BARCELONA-CATALUNYA',
    'canada': 'CIRCUIT GILLES VILLENEUVE',
    'austria': 'RED BULL RING',
    'britain': 'SILVERSTONE CIRCUIT',
    'hungary': 'HUNGARORING',
    'belgium': 'CIRCUIT DE SPA-FRANCORCHAMPS',
    'netherlands': 'CIRCUIT ZANDVOORT',
    'italy': 'AUTODROMO NAZIONALE DI MONZA',
    'singapore': 'MARINA BAY STREET CIRCUIT',
    'japan': 'SUZUKA CIRCUIT',
    'qatar': 'LOSAIL INTERNATIONAL CIRCUIT',
    'usa': 'CIRCUIT OF THE AMERICAS',
    'mexico': 'AUTÓDROMO HERMANOS RODRÍGUEZ',
    'brazil': 'AUTÓDROMO JOSÉ CARLOS PACE',
    'las_vegas': 'LAS VEGAS STREET CIRCUIT',
    'abu_dhabi': 'YAS MARINA CIRCUIT',
    'china': 'SHANGHAI INTERNATIONAL CIRCUIT',
    'imola': 'AUTODROMO ENZO E DINO FERRARI'
  }

  // Generate dynamic mock data that changes realistically
  const generateMockData = (raceId, driver, lap) => {
    // Driver characteristics (base speed, team strength, consistency, aggression)
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

    // Track speed multipliers
    const trackMultipliers = {
      'italy': 1.08, 'saudi_arabia': 1.05, 'azerbaijan': 1.04,
      'bahrain': 1.02, 'austria': 1.01, 'britain': 1.0,
      'spain': 0.99, 'brazil': 0.98, 'japan': 0.98,
      'monaco': 0.82, 'singapore': 0.85, 'hungary': 0.87
    }

    const stats = driverStats[driver] || { speed: 322, teamStrength: 0.75, consistency: 0.85, aggression: 0.75 }
    const trackMult = trackMultipliers[raceId] || 1.0
    
    // Create dynamic position based on multiple factors
    const seed = driver.charCodeAt(0) + lap * 17
    const random = (Math.sin(seed) + 1) / 2
    const lapVariation = Math.sin(lap * 0.3) * 0.02 + random * 0.03
    
    // Calculate dynamic position (1-20) based on:
    // - Team strength (base performance)
    // - Lap progression (tire deg, strategy)
    // - Driver consistency (how much they vary)
    const lapFactor = Math.sin(lap * 0.15) * (1 - stats.consistency) * 3
    const strategyFactor = (lap > 15 && lap < 45) ? Math.cos(lap * 0.1) * 2 : 0 // pit window effects
    const baseRank = (1 - stats.teamStrength) * 15 // 0-15 range based on team
    const position = Math.max(1, Math.min(20, Math.round(baseRank + lapFactor + strategyFactor + random * 3)))
    
    // Driver number based on position with some variation
    const driverNumber = position + Math.floor(random * 5)
    
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
      position: position,
      driver_number: driverNumber
    }
  }

  const generateMockWeather = (raceId, lap) => {
    // Track-specific weather
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
      if (!raceConfig.selectedRace || !raceConfig.currentLap) {
        console.log('Missing race config:', raceConfig)
        return
      }

      const raceId = raceConfig.selectedRace.id || 'bahrain'
      const currentLap = raceConfig.currentLap || 1
      const competitorDriver = raceConfig.selectedDriver || 'VER'
      
      console.log('Fetching data for:', { raceId, currentLap, selectedDriver: competitorDriver })

      // Use real data for Bahrain, mock data for others
      if (raceId === 'bahrain') {
        try {
          // Fetch user telemetry (always driver 1 for now)
          const { data: userTelem, error: userError } = await supabase
            .from('driver_telemetry')
            .select('*')
            .eq('race_id', raceId)
            .eq('driver_number', 1)
            .eq('lap_number', currentLap)
            .single()

          if (!userError && userTelem) setUserData(userTelem)
          // Don't generate mock data for user - position comes from raceState

          // Fetch competitor telemetry
          const { data: compTelem, error: compError } = await supabase
            .from('driver_telemetry')
            .select('*')
            .eq('race_id', raceId)
            .eq('driver_name', competitorDriver)
            .eq('lap_number', currentLap)
            .single()

          if (!compError && compTelem) setCompetitorData(compTelem)
          else {
            setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
          }

          // Fetch weather data
          const { data: weather, error: weatherError } = await supabase
            .from('weather_data')
            .select('*')
            .eq('race_id', raceId)
            .eq('lap_number', currentLap)
            .single()

          if (!weatherError && weather) setWeatherData(weather)
          else {
            setWeatherData(generateMockWeather(raceId, currentLap))
          }

        } catch (err) {
          console.error('Error fetching race data:', err)
          // Use mock data as fallback (but not for user position - that's from raceState)
          setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
          setWeatherData(generateMockWeather(raceId, currentLap))
        }
      } else {
        // Generate realistic mock data for non-Bahrain races
        // User position comes from raceState, only generate opponent data
        setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
        setWeatherData(generateMockWeather(raceId, currentLap))
      }
    }

    fetchRaceData()
  }, [raceConfig])

  const currentTrack = raceConfig.selectedRace?.id || 'bahrain'
  const trackSvgPath = trackMap[currentTrack]
  const trackName = trackNames[currentTrack] || 'AUTODROMO DI MONZA'

  const [animateIn, setAnimateIn] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setAnimateIn(true)
    }
  }, [isOpen])

  const handleClose = () => {
    setAnimateIn(false)
    setTimeout(onClose, 300)
  }

  return (
    <div 
      className={`mclaren-modal-overlay ${animateIn ? 'active' : ''}`}
      onClick={handleClose}
    >
      <div 
        className={`mclaren-dashboard mclaren-modal-container ${animateIn ? 'active' : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="mclaren-modal-header">
          <div className="mclaren-modal-title">
            <span className="competitor-icon"><img src="/trackagent.png" alt="Competitor Agent" /></span>
            COMPETITOR ANALYSIS
          </div>
          <button className="mclaren-close-btn" onClick={handleClose}>✕</button>
        </div>

        {/* Main Container */}
        <div className="main-container">
        {/* Left Driver Section - YOU */}
        <div className="driver-column left-driver">
          <div className="driver-info-header">
            <div className="label">DRIVER</div>
            <div className="label">POSITION</div>
          </div>

          <div className="driver-name-section">
            <div className="driver-name-left">
              <h2>YOU</h2>
              <div className="driver-badge blue">{raceConfig.raceState?.position || 10}</div>
              <div className="driver-delta blue">-1.075</div>
            </div>
            <div className="position-huge">{raceConfig.raceState?.position || 10}</div>
          </div>

          <div className="driver-stats">
            <div className="stat-line">
              <span className="stat-label">LATITUDE</span>
              <span className="stat-value">{userData?.position_x?.toFixed(3) || '43.730'}</span>
            </div>
            <div className="stat-line">
              <span className="stat-label">LONGITUDE</span>
              <span className="stat-value">{userData?.position_y?.toFixed(5) || '9.29103'}</span>
            </div>
          </div>

          <div className="car-display">
            <img src="/1.png" alt="Your Car" />
          </div>

          <div className="safety-status">
            <div className="status-label">ON SAFETY CAR</div>
            <div className="status-action blue">GO TO PIT</div>
          </div>

          <div className="fuel-section">
            <div className="fuel-icon blue">⛽</div>
            <div className="fuel-info">
              <div className="fuel-lap">LAP {raceConfig.currentLap || 51}</div>
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
              <div className="telem-value">{raceConfig.raceState?.tireAge || 8} laps</div>
            </div>
            <div className="telem-box">
              <div className="telem-label">COMPOUND</div>
              <div className="telem-value">{raceConfig.raceState?.tireCompound || 'SOFT'}</div>
            </div>
          </div>

          <div className="speed-box">
            <div className="speed-label">TOP LAP SPEED</div>
            <div className="speed-big">{userData?.speed_max?.toFixed(0) || '287'}<span>km/h</span></div>
            <div className="pace-row">
              <span>AVG PACE</span>
              <span>{userData?.speed_avg?.toFixed(0) || '245'}km/h</span>
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
                <div className="detail-bars blue" style={{width: `${userData?.throttle_avg || 65}%`}}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Center Section - Track & Weather */}
        <div className="center-column">
          <div className="track-header">
            <div className="location">{trackName}</div>
          </div>

          <div className="weather-box" style={{margin: '20px auto', maxWidth: '300px'}}>
            <div className="weather-condition">{weatherData?.rainfall ? 'Rainy' : 'Cloudy'}</div>
            <div className="temperature">{weatherData?.air_temp?.toFixed(0) || '25'}°<span>C</span></div>
              <div className="wind-info">
                <span className="wind-label">WIND</span>
              <span className="wind-value">{weatherData?.wind_speed?.toFixed(1) || '3.5'}m/s ↓</span>
              </div>
              <div className="track-temp-info">
                <span className="temp-label">TRACK TEMP</span>
              <span className="temp-value">{weatherData?.track_temp?.toFixed(0) || '45'}°C</span>
            </div>
          </div>

          <div className="telemetry-chart" style={{marginTop: '30px'}}>
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

          {/* Blue Section - YOU */}
          <div className="section-grid" style={{marginTop: '30px'}}>
            <div className="tire-section">
              <div className="section-title">TYRES AND LAPS PACED</div>
              <div className="tire-content">
                <div className="pirelli-logo">Pirelli</div>
                <div className="tire-circle blue">
                  <div className="tire-laps">{raceConfig.raceState?.tireAge || 8}</div>
                  <div className="tire-label">LAPS</div>
                </div>
                <div className="tire-gauges">
                  <div className="tire-gauge">
                    <div className="gauge-label">L.Rear</div>
                    <div className="gauge-ring"></div>
                  </div>
                  <div className="tire-gauge">
                    <div className="gauge-label">R.Rear</div>
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
                  <span className="telem-blue">{userData?.speed_avg?.toFixed(1) || '259.3'}</span>
                  <span className="telem-yellow">{competitorData?.speed_avg?.toFixed(1) || '258.4'}</span>
                  <span className="telem-unit">kph</span>
                </div>
                <div className="telem-row">
                  <span className="telem-label">Motor</span>
                  <span className="telem-blue">6</span>
                  <span className="telem-yellow">N</span>
                </div>
                <div className="telem-row">
                  <span className="telem-label">Throttle</span>
                  <span className="telem-blue">{userData?.throttle_avg?.toFixed(1) || '100.0'}</span>
                  <span className="telem-yellow">{competitorData?.throttle_avg?.toFixed(1) || '98.5'}</span>
                  <span className="telem-unit">%</span>
                </div>
                <div className="telem-row">
                  <span className="telem-label">Brake</span>
                  <span className="telem-blue">{userData?.brake_avg?.toFixed(1) || '8.5'}</span>
                  <span className="telem-yellow">{competitorData?.brake_avg?.toFixed(1) || '7.2'}</span>
              </div>
            </div>
          </div>
        </div>

          {/* Yellow Section - COMPETITOR */}
          <div className="section-grid reverse" style={{marginTop: '20px'}}>
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
                    <div className="gauge-label">R.Rear</div>
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

        {/* Right Driver Section - COMPETITOR */}
        <div className="driver-column right-driver">
          <div className="driver-info-header reverse">
            <div className="label">POSITION</div>
            <div className="label">DRIVER</div>
          </div>

          <div className="driver-name-section reverse">
            <div className="position-huge">{competitorData?.position || 1}</div>
            <div className="driver-name-right">
              <h2>{raceConfig.selectedDriver || 'COMPETITOR'}</h2>
              <div className="driver-badge yellow">{competitorData?.position || 1}</div>
              <div className="driver-delta yellow">+1.075</div>
            </div>
          </div>

          <div className="driver-stats reverse">
            <div className="stat-line">
              <span className="stat-value">{competitorData?.position_x?.toFixed(3) || '124.052'}</span>
              <span className="stat-label">LATITUDE</span>
            </div>
            <div className="stat-line">
              <span className="stat-value">{competitorData?.position_y?.toFixed(5) || '9.28070'}</span>
              <span className="stat-label">LONGITUDE</span>
            </div>
          </div>

          <div className="car-display">
            <img src="/2.png" alt="Competitor Car" />
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
              <div className="fuel-status">{competitorData?.drs_available ? 'DRS AVAILABLE' : 'NO DRS'}</div>
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
            <div className="speed-big">{competitorData?.speed_max?.toFixed(0) || '291'}<span>km/h</span></div>
            <div className="pace-row">
              <span>AVG PACE</span>
              <span>{competitorData?.speed_avg?.toFixed(0) || '248'}km/h</span>
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
                <div className="detail-bars yellow" style={{width: `${competitorData?.brake_avg || 45}%`}}></div>
              </div>
              <div className="detail-row">
                <span>THROTTLE</span>
                <div className="detail-bars yellow"></div>
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
              <div className="marker-lap">{raceConfig.currentLap || 30}</div>
              <div className="marker-label">CURRENT LAP</div>
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
              <div className="marker-lap">{raceConfig.currentLap || 30}</div>
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
      </div>
    </div>
  )
}

export default McLarenDashboard
