import CollapsibleBox from './CollapsibleBox'

export default function StrategyCard({ recommendation, currentLap }) {
  if (!recommendation) {
    return (
      <CollapsibleBox title="AI Strategy Recommendation" icon="🎯" defaultOpen={true}>
        <div className="text-center py-8">
          <div className="text-6xl mb-4">🤖</div>
          <p className="text-xl text-gray-300">Waiting for AI analysis...</p>
          <p className="text-sm text-gray-500 mt-2">Data agents are monitoring the race</p>
        </div>
      </CollapsibleBox>
    )
  }

  return (
    <CollapsibleBox title={`AI Recommendation (Lap ${recommendation.lap_number})`} icon="🎯" defaultOpen={true}>
      <div className="space-y-4">
        {/* Main Info */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-700 rounded p-3">
            <div className="text-xs text-gray-400">Type</div>
            <div className="text-lg font-bold text-white">{recommendation.recommendation_type || 'N/A'}</div>
          </div>
          <div className="bg-blue-900 bg-opacity-40 rounded p-3">
            <div className="text-xs text-gray-400">Confidence</div>
            <div className="text-lg font-bold text-white">
              {recommendation.confidence_score ? (recommendation.confidence_score * 100).toFixed(0) + '%' : 'N/A'}
            </div>
          </div>
        </div>

        {/* Reasoning */}
        <CollapsibleBox title="AI Reasoning" icon="💡" defaultOpen={true}>
          <p className="text-gray-200 text-sm whitespace-pre-wrap">{recommendation.reasoning || 'No reasoning provided'}</p>
        </CollapsibleBox>

        {/* Raw Data */}
        <details>
          <summary className="text-gray-400 cursor-pointer hover:text-white text-sm">View Raw JSON</summary>
          <pre className="mt-2 p-2 bg-gray-900 rounded text-xs overflow-auto max-h-60">
            {JSON.stringify(recommendation, null, 2)}
          </pre>
        </details>
      </div>
    </CollapsibleBox>
  )
}
