import { useState, useEffect } from 'react'

export default function RaceComparison({ comparisonData }) {
  if (!comparisonData) return null

  const { ai_strategy, baseline, current_lap, total_laps } = comparisonData

  // Calculate car position on track (0-100%)
  const getCarPosition = (lap) => {
    return (lap / total_laps) * 100
  }

  const aiPosition = getCarPosition(current_lap)
  const baselinePosition = getCarPosition(current_lap)

  // Calculate time difference for visual gap
  const timeDiff = ai_strategy.cumulative_time - baseline.cumulative_time
  const gapLaps = Math.abs(timeDiff / 90) // Approx 90s per lap Monaco

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-6 text-center">
        🏁 Live Race Comparison
      </h2>

      <div className="grid grid-cols-2 gap-8">
        {/* AI Strategy Side */}
        <div className="space-y-4">
          <div className="text-center">
            <div className="text-xl font-bold text-green-400 mb-2">
              🤖 AI Strategy
            </div>
            <div className="text-3xl font-bold text-white">
              {ai_strategy.cumulative_time.toFixed(1)}s
            </div>
          </div>

          {/* Track visualization */}
          <div className="relative h-64 bg-gray-900 rounded-lg border-2 border-green-500 overflow-hidden">
            {/* Track (oval) */}
            <div className="absolute inset-4 border-4 border-dashed border-gray-600 rounded-full"></div>

            {/* Start/Finish line */}
            <div className="absolute top-1/2 left-0 w-1 h-8 bg-white transform -translate-y-1/2"></div>
            <div className="absolute top-1/2 left-2 text-white text-xs transform -translate-y-1/2">START</div>

            {/* AI Car - animated around track */}
            <div
              className="absolute w-8 h-8 transition-all duration-1000"
              style={{
                top: `${50 + 35 * Math.sin((aiPosition / 100) * 2 * Math.PI - Math.PI / 2)}%`,
                left: `${50 + 35 * Math.cos((aiPosition / 100) * 2 * Math.PI - Math.PI / 2)}%`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <div className="text-3xl">🏎️</div>
            </div>

            {/* Pit stop indicator */}
            {ai_strategy.has_pitted && (
              <div className="absolute bottom-2 left-2 bg-orange-600 text-white text-xs px-2 py-1 rounded">
                ✅ PITTED Lap {ai_strategy.pit_lap}
              </div>
            )}
          </div>

          {/* Strategy details */}
          <div className="bg-gray-900 rounded p-3 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Tire:</span>
              <span className="text-white font-semibold">{ai_strategy.current_compound}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Tire Age:</span>
              <span className="text-white font-semibold">{ai_strategy.tire_age} laps</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Strategy:</span>
              <span className="text-green-400 font-semibold">Following AI</span>
            </div>
          </div>
        </div>

        {/* Baseline (No Strategy) Side */}
        <div className="space-y-4">
          <div className="text-center">
            <div className="text-xl font-bold text-red-400 mb-2">
              ❌ No Strategy
            </div>
            <div className="text-3xl font-bold text-white">
              {baseline.cumulative_time.toFixed(1)}s
            </div>
          </div>

          {/* Track visualization */}
          <div className="relative h-64 bg-gray-900 rounded-lg border-2 border-red-500 overflow-hidden">
            {/* Track (oval) */}
            <div className="absolute inset-4 border-4 border-dashed border-gray-600 rounded-full"></div>

            {/* Start/Finish line */}
            <div className="absolute top-1/2 left-0 w-1 h-8 bg-white transform -translate-y-1/2"></div>
            <div className="absolute top-1/2 left-2 text-white text-xs transform -translate-y-1/2">START</div>

            {/* Baseline Car - animated around track */}
            <div
              className="absolute w-8 h-8 transition-all duration-1000"
              style={{
                top: `${50 + 35 * Math.sin((baselinePosition / 100) * 2 * Math.PI - Math.PI / 2)}%`,
                left: `${50 + 35 * Math.cos((baselinePosition / 100) * 2 * Math.PI - Math.PI / 2)}%`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <div className="text-3xl opacity-70">🏎️</div>
            </div>

            {/* No pit indicator */}
            {!baseline.has_pitted && current_lap > 40 && (
              <div className="absolute bottom-2 left-2 bg-red-600 text-white text-xs px-2 py-1 rounded">
                ⚠️ NO PIT STOP
              </div>
            )}
          </div>

          {/* Strategy details */}
          <div className="bg-gray-900 rounded p-3 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Tire:</span>
              <span className="text-white font-semibold">{baseline.current_compound}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Tire Age:</span>
              <span className="text-white font-semibold">{baseline.tire_age} laps</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Strategy:</span>
              <span className="text-red-400 font-semibold">No AI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Time Difference Banner */}
      <div className="mt-6 text-center">
        {timeDiff !== 0 && (
          <div className={`inline-block px-6 py-3 rounded-lg ${
            timeDiff < 0
              ? 'bg-green-600 text-white'
              : 'bg-red-600 text-white'
          }`}>
            <div className="text-2xl font-bold">
              {timeDiff < 0 ? '🚀 AI AHEAD' : '⚠️ AI BEHIND'} by {Math.abs(timeDiff).toFixed(1)}s
            </div>
            <div className="text-sm opacity-90 mt-1">
              ≈ {gapLaps.toFixed(2)} car lengths
            </div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-400 mb-1">
          <span>Lap {current_lap}</span>
          <span>{total_laps} laps total</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
            style={{ width: `${(current_lap / total_laps) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  )
}
