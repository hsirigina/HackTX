import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { createClient } from '@supabase/supabase-js'
import './McLarenDashboard.css'

const supabase = createClient(
  'https://wkcdbbmelonvmduxkkge.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrY2RiYm1lbG9udm1kdXhra2dlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NzM2NjMsImV4cCI6MjA3NjM0OTY2M30.UADl4E7idotTLC-OSEv_kbCslpRDykhehe-E9at1Vkk'
)

function McLarenDashboard() {
  const location = useLocation()
  const raceConfig = location.state || {}
  
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

  // Generate realistic mock data for non-Bahrain races
  const generateMockData = (raceId, driver, lap) => {
    // Driver characteristics (base speed, consistency, aggression)
    const driverStats = {
      'VER': { speed: 330, consistency: 0.95, aggression: 0.9 },
      'PER': { speed: 325, consistency: 0.88, aggression: 0.75 },
      'LEC': { speed: 328, consistency: 0.90, aggression: 0.85 },
      'SAI': { speed: 326, consistency: 0.87, aggression: 0.80 },
      'HAM': { speed: 327, consistency: 0.92, aggression: 0.88 },
      'RUS': { speed: 324, consistency: 0.89, aggression: 0.82 },
      'NOR': { speed: 326, consistency: 0.91, aggression: 0.87 },
      'PIA': { speed: 323, consistency: 0.86, aggression: 0.79 },
      'ALO': { speed: 325, consistency: 0.93, aggression: 0.83 },
      'STR': { speed: 322, consistency: 0.85, aggression: 0.78 }
    }

    // Track speed multipliers
    const trackMultipliers = {
      'italy': 1.08, 'saudi_arabia': 1.05, 'azerbaijan': 1.04,
      'bahrain': 1.02, 'austria': 1.01, 'britain': 1.0,
      'spain': 0.99, 'brazil': 0.98, 'japan': 0.98,
      'monaco': 0.82, 'singapore': 0.85, 'hungary': 0.87
    }

    const stats = driverStats[driver] || driverStats['NOR']
    const trackMult = trackMultipliers[raceId] || 1.0
    
    // Add some lap-to-lap variation
    const lapVariation = Math.sin(lap * 0.3) * 0.02 + Math.random() * 0.03
    
    return {
      speed_max: stats.speed * trackMult * (1 + lapVariation),
      speed_avg: stats.speed * trackMult * 0.75 * (1 + lapVariation * 0.5),
      throttle_avg: 65 + stats.aggression * 30 + Math.random() * 5,
      throttle_max: 98 + Math.random() * 2,
      brake_avg: (1 - stats.aggression) * 15 + Math.random() * 5,
      brake_max: 95 + Math.random() * 5,
      drs_available: Math.random() > 0.6,
      position_x: 50 + lap * 2 + Math.random() * 10,
      position_y: 30 + Math.sin(lap) * 5 + Math.random() * 10
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
          else {
            // Fallback to mock if no data
            setUserData(generateMockData(raceId, 'YOU', currentLap))
          }

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
          // Use mock data as fallback
          setUserData(generateMockData(raceId, 'YOU', currentLap))
          setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
          setWeatherData(generateMockWeather(raceId, currentLap))
        }
      } else {
        // Generate realistic mock data for non-Bahrain races
        setUserData(generateMockData(raceId, 'YOU', currentLap))
        setCompetitorData(generateMockData(raceId, competitorDriver, currentLap))
        setWeatherData(generateMockWeather(raceId, currentLap))
      }
    }

    fetchRaceData()
  }, [raceConfig])

  const currentTrack = raceConfig.selectedRace?.id || 'bahrain'
  const trackSvgPath = trackMap[currentTrack]
  const trackName = trackNames[currentTrack] || 'AUTODROMO DI MONZA'

  return (
    <div className="mclaren-dashboard">
      {/* Top Header */}
      <div className="top-header">
        <div className="header-left">VODAFONE McLAREN MERCEDES</div>
        <div className="header-right">VODAFONE McLAREN MERCEDES</div>
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
              <div className="driver-badge blue">{raceConfig.raceState?.position || 3}</div>
              <div className="driver-delta blue">-1.075</div>
            </div>
            <div className="position-huge">{raceConfig.raceState?.position || 2}</div>
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

          <div className="lap-weather-row">
            <div className="lap-counter">
              <div className="lap-label">LAP</div>
              <div className="lap-number">{raceConfig.currentLap || 30}/{raceConfig.selectedRace?.laps || 53}</div>
            </div>

            <div className="weather-box">
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
          </div>

          <div className="track-map">
            {trackSvgPath ? (
              <img src={trackSvgPath} alt={trackName} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
            ) : (
              <svg viewBox="0 0 800 400" className="track-svg">
                {/* Fallback track outline */}
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
            )}

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

        {/* Right Driver Section - COMPETITOR */}
        <div className="driver-column right-driver">
          <div className="driver-info-header reverse">
            <div className="label">POSITION</div>
            <div className="label">DRIVER</div>
          </div>

          <div className="driver-name-section reverse">
            <div className="position-huge">1</div>
            <div className="driver-name-right">
              <h2>{raceConfig.selectedDriver || 'COMPETITOR'}</h2>
              <div className="driver-badge yellow">1</div>
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
