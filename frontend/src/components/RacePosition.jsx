import CollapsibleBox from './CollapsibleBox'

export default function RacePosition({ raceData }) {
  if (!raceData || !raceData.position) {
    return (
      <CollapsibleBox title="Race Position" icon="📍" defaultOpen={false}>
        <p className="text-gray-400">No position data available</p>
      </CollapsibleBox>
    )
  }

  const { position } = raceData
  const currentPos = position.position || '?'

  return (
    <CollapsibleBox title="Race Position" icon="📍" defaultOpen={false}>
      <div className="space-y-4">
        <div className="text-center">
          <div className="text-6xl font-bold text-white mb-2">
            P{currentPos}
          </div>
          <div className="text-sm text-gray-400">Current Position</div>
        </div>

        <details>
          <summary className="text-gray-400 cursor-pointer hover:text-white text-sm">Raw Data</summary>
          <pre className="mt-2 p-2 bg-gray-900 rounded text-xs overflow-auto max-h-40">
            {JSON.stringify(position, null, 2)}
          </pre>
        </details>
      </div>
    </CollapsibleBox>
  )
}
