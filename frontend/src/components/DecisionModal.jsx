import { useState } from 'react'

function DecisionModal({ decision, onSelect, onClose }) {
  const [selectedOption, setSelectedOption] = useState(null)

  if (!decision) return null

  const { lap_number, options, context } = decision

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto border-4 border-yellow-500 shadow-2xl">

        {/* Header */}
        <div className="bg-gradient-to-r from-yellow-500 to-orange-500 p-6 sticky top-0 z-10">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                ⚠️ LAP {lap_number} - DECISION REQUIRED
              </h2>
              <p className="text-gray-800 text-lg">
                {context?.gap_ahead ? `Gap ahead: ${context.gap_ahead.toFixed(1)}s` : ''}
                {context?.gap_behind ? ` | Gap behind: ${context.gap_behind.toFixed(1)}s` : ''}
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-gray-900">{lap_number}/57</div>
              <div className="text-sm text-gray-700">Current Lap</div>
            </div>
          </div>
        </div>

        {/* AI Context */}
        {context && (
          <div className="p-6 bg-blue-900 bg-opacity-30 border-b border-gray-700">
            <div className="flex items-start space-x-3">
              <div className="text-3xl">🤖</div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-blue-300 mb-2">AI Analysis</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Leader:</span>
                    <span className="text-white ml-2 font-semibold">{context.leader || 'VER'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Leader Tire Age:</span>
                    <span className="text-white ml-2 font-semibold">{context.leader_tire_age} laps</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Decision Options */}
        <div className="p-6 space-y-4">
          <h3 className="text-2xl font-bold text-white mb-4">
            Choose Your Strategy:
          </h3>

          {options && options.map((option, index) => (
            <button
              key={option.option_id}
              onClick={() => setSelectedOption(option)}
              className={`w-full text-left p-6 rounded-xl border-2 transition-all ${
                selectedOption?.option_id === option.option_id
                  ? 'border-green-500 bg-green-900 bg-opacity-40 shadow-lg shadow-green-500/50'
                  : option.ai_confidence === 'HIGHLY_RECOMMENDED'
                  ? 'border-blue-500 bg-blue-900 bg-opacity-20 hover:bg-opacity-30'
                  : option.ai_confidence === 'RECOMMENDED'
                  ? 'border-yellow-500 bg-yellow-900 bg-opacity-20 hover:bg-opacity-30'
                  : 'border-gray-600 bg-gray-800 bg-opacity-20 hover:bg-opacity-30'
              }`}
            >
              {/* Option Header */}
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-3xl">
                      {index === 0 ? '🎯' : index === 1 ? '⚡' : '🔧'}
                    </span>
                    <h4 className="text-2xl font-bold text-white">{option.title}</h4>
                  </div>
                  <p className="text-gray-300 text-lg">{option.description}</p>
                </div>
                {option.ai_confidence === 'HIGHLY_RECOMMENDED' && (
                  <div className="ml-4 px-3 py-1 bg-blue-500 text-white text-xs font-bold rounded-full">
                    AI RECOMMENDS
                  </div>
                )}
              </div>

              {/* Reasoning */}
              <div className="mb-3 p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <p className="text-gray-200 italic">
                  💭 <strong>Reasoning:</strong> {option.reasoning}
                </p>
              </div>

              {/* Impact Metrics */}
              <div className="grid grid-cols-3 gap-3 mb-3">
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded">
                  <div className="text-xs text-gray-400 mb-1">Lap Time Impact</div>
                  <div className={`text-lg font-bold ${
                    option.predicted_lap_time_impact < 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {option.predicted_lap_time_impact > 0 ? '+' : ''}{option.predicted_lap_time_impact.toFixed(1)}s
                  </div>
                </div>
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded">
                  <div className="text-xs text-gray-400 mb-1">Race Time Impact</div>
                  <div className={`text-lg font-bold ${
                    option.predicted_race_time_impact < 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {option.predicted_race_time_impact > 0 ? '+' : ''}{option.predicted_race_time_impact.toFixed(1)}s
                  </div>
                </div>
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded">
                  <div className="text-xs text-gray-400 mb-1">Tire Wear</div>
                  <div className="text-lg font-bold text-yellow-400">
                    {option.tire_wear_impact.toFixed(1)}x
                  </div>
                </div>
              </div>

              {/* Pros & Cons */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-green-400 font-semibold mb-1">✅ Pros:</div>
                  <ul className="space-y-1 text-gray-300">
                    {option.pros.map((pro, i) => (
                      <li key={i}>• {pro}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-red-400 font-semibold mb-1">❌ Cons:</div>
                  <ul className="space-y-1 text-gray-300">
                    {option.cons.map((con, i) => (
                      <li key={i}>• {con}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Selected Indicator */}
              {selectedOption?.option_id === option.option_id && (
                <div className="mt-4 text-center text-green-400 font-bold">
                  👍 SELECTED - Press CONFIRM to execute
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="p-6 bg-gray-800 border-t border-gray-700 flex justify-between items-center sticky bottom-0">
          <div className="text-gray-400 text-sm">
            {selectedOption
              ? '👍 Thumbs up gesture to confirm'
              : '👆 Swipe to browse options, thumbs up to select'}
          </div>
          <div className="flex space-x-4">
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition"
            >
              Cancel
            </button>
            <button
              onClick={() => selectedOption && onSelect(selectedOption)}
              disabled={!selectedOption}
              className={`px-8 py-3 rounded-lg font-bold text-lg transition ${
                selectedOption
                  ? 'bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-500/50'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              ✅ CONFIRM DECISION
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DecisionModal
