import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import AgentStatus from './components/AgentStatus'
import StrategyCard from './components/StrategyCard'
import RacePosition from './components/RacePosition'
import './App.css'

const RACE_ID = 'monaco_2024'
const DRIVER = 'LEC'

function App() {
  const [currentLap, setCurrentLap] = useState(null)
  const [raceData, setRaceData] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-gradient-to-r from-red-600 to-red-800 rounded-lg p-6 shadow-2xl border border-red-500">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                🏎️ F1 AI Race Strategy System
              </h1>
              <p className="text-red-100 text-lg">
                Monaco Grand Prix 2024 • Driver: Charles Leclerc (LEC)
              </p>
            </div>
            <div className="text-right">
              <div className="text-5xl font-bold text-white">
                {currentLap || '--'}<span className="text-2xl text-red-200">/78</span>
              </div>
              <div className="text-red-100 text-sm uppercase tracking-wider">Current Lap</div>
            </div>
          </div>
        </div>
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
