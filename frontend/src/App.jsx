import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import AgentStatus from './components/AgentStatus'
import StrategyCard from './components/StrategyCard'
import RacePosition from './components/RacePosition'
import PitStopNotification from './components/PitStopNotification'
import RaceComparison from './components/RaceComparison'
import DecisionModal from './components/DecisionModal'
import './App.css'

const RACE_ID = 'bahrain_2024'
const DRIVER = 'LEC'

function App() {
  const [mode, setMode] = useState('monitor') // 'monitor' or 'simulator'
  const [currentLap, setCurrentLap] = useState(null)
  const [raceData, setRaceData] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [latestPitStop, setLatestPitStop] = useState(null)
  const [lastPitStopLap, setLastPitStopLap] = useState(null)
  const [comparisonData, setComparisonData] = useState(null)

  // Simulator mode state
  const [pendingDecision, setPendingDecision] = useState(null)
  const [simulatorState, setSimulatorState] = useState(null)

  // Poll Supabase every 2 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get latest lap number (use driver_name field)
        const { data: lapData, error: lapError } = await supabase
          .from('lap_times')
          .select('lap_number, lap_time_seconds, driver_number, sector_1_time, sector_2_time, sector_3_time')
          .eq('race_id', RACE_ID)
          .eq('driver_name', DRIVER)
          .order('lap_number', { ascending: false })
          .limit(1)

        console.log('Lap data:', lapData, 'Error:', lapError)

        if (lapData && lapData.length > 0) {
          const currentLapNum = lapData[0].lap_number
          const driverNumber = lapData[0].driver_number

          setCurrentLap(currentLapNum)

          // Get agent status (analyzed insights, not raw data)
          const { data: agentStatus, error: agentError } = await supabase
            .from('agent_status')
            .select('*')
            .eq('race_id', RACE_ID)
            .eq('driver_name', DRIVER)
            .order('lap_number', { ascending: false })
            .limit(1)
            .maybeSingle()

          console.log('Agent Status:', agentStatus, 'Error:', agentError)

          // Get latest AI recommendation
          const { data: recData } = await supabase
            .from('agent_recommendations')
            .select('*')
            .eq('race_id', RACE_ID)
            .order('lap_number', { ascending: false })
            .limit(1)

          // Get latest pit stop for this driver
          const { data: pitStopData } = await supabase
            .from('pit_stops')
            .select('*')
            .eq('race_id', RACE_ID)
            .eq('driver_name', DRIVER)
            .order('lap_number', { ascending: false })
            .limit(1)

          // Check if we have a new pit stop to show
          if (pitStopData && pitStopData.length > 0) {
            const newPitStopLap = pitStopData[0].lap_number

            // If this is a new pit stop (different lap than before)
            if (newPitStopLap !== lastPitStopLap) {
              setLatestPitStop(pitStopData[0])
              setLastPitStopLap(newPitStopLap)

              // Auto-dismiss notification after 5 seconds
              setTimeout(() => {
                setLatestPitStop(null)
              }, 5000)
            }
          }

          // Get race comparison data
          const { data: compData } = await supabase
            .from('race_comparison')
            .select('*')
            .eq('race_id', RACE_ID)
            .eq('driver_name', DRIVER)
            .order('lap_number', { ascending: false })
            .limit(1)

          if (compData && compData.length > 0) {
            const data = compData[0]
            setComparisonData({
              current_lap: data.lap_number,
              total_laps: 78,
              ai_strategy: {
                cumulative_time: data.ai_cumulative_time,
                current_compound: data.ai_tire_compound,
                tire_age: data.ai_tire_age,
                has_pitted: data.ai_has_pitted,
                pit_lap: data.ai_pit_lap
              },
              baseline: {
                cumulative_time: data.baseline_cumulative_time,
                current_compound: data.baseline_tire_compound,
                tire_age: data.baseline_tire_age,
                has_pitted: data.baseline_has_pitted,
                pit_lap: data.baseline_pit_lap
              }
            })
          }

          setRaceData({
            lap: lapData[0],
            agentStatus: agentStatus || {}
          })

          if (recData && recData.length > 0) {
            setRecommendation(recData[0])
          }

          setLoading(false)
        } else {
          // No data yet, but don't stay in loading forever
          console.log('No race data found yet...')
          setTimeout(() => setLoading(false), 5000) // Show UI after 5 seconds even if no data
        }
      } catch (error) {
        console.error('Error fetching data:', error)
        setLoading(false) // Show UI even on error
      }
    }

    // Initial fetch
    fetchData()

    // Poll every 2 seconds
    const interval = setInterval(fetchData, 2000)

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-red-500 mx-auto mb-4"></div>
          <p className="text-xl text-gray-300">Loading Race Data...</p>
        </div>
      </div>
    )
  }

  const handleDecisionSelect = (option) => {
    console.log('User selected option:', option)
    // Here we'll send the decision to backend
    setPendingDecision(null)
    // TODO: Call backend API to execute decision
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-6">
      {/* Decision Modal (Simulator Mode) */}
      {mode === 'simulator' && pendingDecision && (
        <DecisionModal
          decision={pendingDecision}
          onSelect={handleDecisionSelect}
          onClose={() => setPendingDecision(null)}
        />
      )}

      {/* Pit Stop Notification */}
      <PitStopNotification pitStop={latestPitStop} />

      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-gradient-to-r from-red-600 to-red-800 rounded-lg p-6 shadow-2xl border border-red-500">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                🏎️ F1 AI Race Strategy System
              </h1>
              <p className="text-red-100 text-lg">
                Bahrain Grand Prix 2024 • Driver: {mode === 'simulator' ? 'YOU' : 'Charles Leclerc (LEC)'}
              </p>
            </div>
            <div className="flex items-center space-x-6">
              {/* Mode Toggle */}
              <div className="flex space-x-2">
                <button
                  onClick={() => setMode('monitor')}
                  className={`px-4 py-2 rounded-lg font-semibold transition ${
                    mode === 'monitor'
                      ? 'bg-white text-red-800'
                      : 'bg-red-800 bg-opacity-50 text-red-200 hover:bg-opacity-70'
                  }`}
                >
                  📊 Monitor Mode
                </button>
                <button
                  onClick={() => setMode('simulator')}
                  className={`px-4 py-2 rounded-lg font-semibold transition ${
                    mode === 'simulator'
                      ? 'bg-white text-red-800'
                      : 'bg-red-800 bg-opacity-50 text-red-200 hover:bg-opacity-70'
                  }`}
                >
                  🎮 Simulator Mode
                </button>
              </div>

              {/* Lap Counter */}
              <div className="text-right">
                <div className="text-5xl font-bold text-white">
                  {currentLap || '--'}<span className="text-2xl text-red-200">/57</span>
                </div>
                <div className="text-red-100 text-sm uppercase tracking-wider">Current Lap</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Simulator Mode Test Button */}
      {mode === 'simulator' && !pendingDecision && (
        <div className="max-w-7xl mx-auto mb-6">
          <button
            onClick={() => {
              // Test decision with sample data
              setPendingDecision({
                lap_number: 12,
                context: {
                  gap_ahead: 2.5,
                  gap_behind: 5.0,
                  leader: 'VER',
                  leader_tire_age: 11
                },
                options: [
                  {
                    option_id: 1,
                    category: 'PIT_STOP',
                    title: 'Pit Now - Medium Tires',
                    description: 'Box this lap for MEDIUM compound',
                    action: 'PIT_NOW',
                    parameters: { compound: 'MEDIUM' },
                    predicted_lap_time_impact: -25.0,
                    predicted_race_time_impact: 65.3,
                    tire_wear_impact: 0.0,
                    reasoning: 'Pit now for MEDIUM - 45 laps remaining on fresh tires',
                    pros: ['Fresh MEDIUM tires', '45 laps to end', 'Clear track ahead'],
                    cons: ['25s pit loss', 'Lose track position', 'Undercut risk from behind'],
                    ai_confidence: 'ALTERNATIVE'
                  },
                  {
                    option_id: 2,
                    category: 'PIT_STOP',
                    title: 'Stay Out - Extend Stint',
                    description: 'Stay out for 3 more laps (pit lap 15)',
                    action: 'STAY_OUT',
                    parameters: { extend_laps: 3 },
                    predicted_lap_time_impact: 0.3,
                    predicted_race_time_impact: -23.8,
                    tire_wear_impact: 1.3,
                    reasoning: 'Extend stint 3 laps - delay pit stop, build undercut window',
                    pros: ['No pit loss yet', 'Undercut cars ahead', 'Track position maintained'],
                    cons: ['Tire age will be 15 laps', 'Performance degradation', 'Risk of tire cliff'],
                    ai_confidence: 'HIGHLY_RECOMMENDED'
                  },
                  {
                    option_id: 3,
                    category: 'PIT_STOP',
                    title: 'Pit Now - Hard Tires',
                    description: 'Box this lap for HARD compound (long stint to end)',
                    action: 'PIT_NOW',
                    parameters: { compound: 'HARD' },
                    predicted_lap_time_impact: -25.0,
                    predicted_race_time_impact: 44.9,
                    tire_wear_impact: 0.0,
                    reasoning: 'Pit now for HARD - 45 laps remaining on fresh tires',
                    pros: ['Fresh HARD tires', '45 laps to end', 'One-stop strategy'],
                    cons: ['25s pit loss', 'Slower initial pace', 'Undercut risk'],
                    ai_confidence: 'RECOMMENDED'
                  }
                ]
              })
            }}
            className="w-full bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-bold py-4 px-6 rounded-lg shadow-lg transition"
          >
            🎮 TEST: Trigger Decision (Lap 12 - First Pit Window)
          </button>
        </div>
      )}

      {/* Race Comparison - Full Width */}
      <div className="max-w-7xl mx-auto mb-6">
        <RaceComparison comparisonData={comparisonData} />
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Agent Status */}
        <div className="lg:col-span-1 space-y-6">
          <AgentStatus raceData={raceData} />
          <RacePosition raceData={raceData} />
        </div>

        {/* Right Column - Strategy Recommendations */}
        <div className="lg:col-span-2">
          <StrategyCard recommendation={recommendation} currentLap={currentLap} />
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-6">
        <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-gray-700">
          <div className="flex justify-between items-center text-sm text-gray-400">
            <div>
              🤖 Powered by 4 Data Agents + AI Coordinator (Gemini 2.0)
            </div>
            <div>
              {recommendation && (
                <span className="text-green-400">
                  ✅ Last Analysis: Lap {recommendation.lap_number}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
