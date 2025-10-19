import CollapsibleBox from './CollapsibleBox'

export default function AgentStatus({ raceData }) {
  if (!raceData) {
    return (
      <div className="space-y-4">
        <CollapsibleBox title="Agent Status" icon="📊" defaultOpen={true}>
          <p className="text-gray-400">No race data available. Start the backend race replay.</p>
        </CollapsibleBox>
      </div>
    )
  }

  const { agentStatus } = raceData

  return (
    <div className="space-y-4">
      {/* Tire Agent */}
      <CollapsibleBox title="Tire Agent 🛞" icon="📊" defaultOpen={true}>
        <div className="space-y-3 text-sm">
          {agentStatus?.tire_compound ? (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Compound</div>
                  <div className="text-lg font-bold text-white">{agentStatus.tire_compound}</div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Age</div>
                  <div className="text-lg font-bold text-white">{agentStatus.tire_age} laps</div>
                </div>
              </div>

              <div className="bg-orange-900 bg-opacity-30 rounded p-3">
                <div className="text-xs text-gray-400">Degradation Trend (last 5 laps)</div>
                <div className="text-xl font-bold text-orange-300">
                  {agentStatus.tire_degradation_trend !== null
                    ? `${agentStatus.tire_degradation_trend > 0 ? '+' : ''}${agentStatus.tire_degradation_trend.toFixed(2)}s`
                    : 'Calculating...'}
                </div>
              </div>

              {agentStatus.predicted_cliff_lap !== null && agentStatus.predicted_cliff_lap !== undefined && (
                <div className={`rounded p-3 ${agentStatus.predicted_cliff_lap > 0 ? 'bg-orange-900 bg-opacity-30' : 'bg-red-900 bg-opacity-50'}`}>
                  <div className="text-xs text-gray-400">
                    {agentStatus.predicted_cliff_lap > 0 ? '⚠️ Tire Cliff Warning' : '🔴 TIRES DEGRADED'}
                  </div>
                  <div className={`text-xl font-bold ${agentStatus.predicted_cliff_lap > 0 ? 'text-orange-300' : 'text-red-200'}`}>
                    {agentStatus.predicted_cliff_lap > 0
                      ? `${agentStatus.predicted_cliff_lap} laps until cliff`
                      : `Past cliff by ${Math.abs(agentStatus.predicted_cliff_lap)} laps`}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {agentStatus.predicted_cliff_lap > 0
                      ? 'Tires will lose ~3s/lap performance'
                      : 'Tires severely degraded - Consider pitting'}
                  </div>
                </div>
              )}

              <details className="mt-4">
                <summary className="text-gray-400 cursor-pointer hover:text-white">View Raw Data</summary>
                <pre className="mt-2 p-2 bg-gray-900 rounded text-xs overflow-auto max-h-40">
                  {JSON.stringify(agentStatus, null, 2)}
                </pre>
              </details>
            </>
          ) : (
            <p className="text-gray-400">Collecting tire data...</p>
          )}
        </div>
      </CollapsibleBox>

      {/* Lap Time Agent */}
      <CollapsibleBox title="Pace Agent ⏱️" icon="📊" defaultOpen={true}>
        <div className="space-y-3 text-sm">
          {agentStatus?.current_pace !== null ? (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Current Pace</div>
                  <div className="text-lg font-bold text-white">{agentStatus.current_pace?.toFixed(3)}s</div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Average</div>
                  <div className="text-lg font-bold text-white">{agentStatus.avg_lap_time?.toFixed(3)}s</div>
                </div>
              </div>

              <div className={`rounded p-3 ${agentStatus.pace_trend > 0 ? 'bg-red-900 bg-opacity-30' : 'bg-green-900 bg-opacity-30'}`}>
                <div className="text-xs text-gray-400">Pace Trend</div>
                <div className={`text-xl font-bold ${agentStatus.pace_trend > 0 ? 'text-red-300' : 'text-green-300'}`}>
                  {agentStatus.pace_trend > 0 ? '📉' : '📈'}
                  {agentStatus.pace_trend > 0 ? '+' : ''}{agentStatus.pace_trend?.toFixed(3)}s/lap
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {agentStatus.pace_trend > 0 ? 'Getting slower' : 'Getting faster'}
                </div>
              </div>
            </>
          ) : (
            <p className="text-gray-400">Collecting pace data...</p>
          )}
        </div>
      </CollapsibleBox>

      {/* Position Agent */}
      <CollapsibleBox title="Position Agent 🏁" icon="📊" defaultOpen={true}>
        <div className="space-y-3 text-sm">
          {agentStatus?.current_position ? (
            <>
              <div className="text-center py-4">
                <div className="text-6xl font-bold text-white">P{agentStatus.current_position}</div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Gap Ahead</div>
                  <div className="text-lg font-bold text-white">
                    {agentStatus.gap_ahead !== null && agentStatus.gap_ahead < 999
                      ? `+${agentStatus.gap_ahead.toFixed(2)}s`
                      : 'Leader'}
                  </div>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <div className="text-xs text-gray-400">Gap Behind</div>
                  <div className="text-lg font-bold text-white">
                    {agentStatus.gap_behind !== null && agentStatus.gap_behind < 999
                      ? `-${agentStatus.gap_behind.toFixed(2)}s`
                      : 'Last'}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <p className="text-gray-400">Collecting position data...</p>
          )}
        </div>
      </CollapsibleBox>

      {/* Competitor Agent */}
      <CollapsibleBox title="Competitor Agent 🏎️" icon="📊" defaultOpen={true}>
        <div className="space-y-3 text-sm">
          {agentStatus?.nearby_threats?.length > 0 || agentStatus?.nearby_opportunities?.length > 0 ? (
            <>
              {agentStatus.nearby_threats?.length > 0 && (
                <div className="bg-red-900 bg-opacity-20 rounded p-3">
                  <div className="text-xs text-red-300 font-bold mb-2">⚠️ Threats</div>
                  {agentStatus.nearby_threats.map((threat, idx) => (
                    <div key={idx} className="text-white text-xs py-1">
                      {threat.driver || 'Unknown'}: {threat.message || 'Faster pace'}
                    </div>
                  ))}
                </div>
              )}

              {agentStatus.nearby_opportunities?.length > 0 && (
                <div className="bg-green-900 bg-opacity-20 rounded p-3">
                  <div className="text-xs text-green-300 font-bold mb-2">✅ Opportunities</div>
                  {agentStatus.nearby_opportunities.map((opp, idx) => (
                    <div key={idx} className="text-white text-xs py-1">
                      {opp.driver || 'Unknown'}: {opp.message || 'Slower pace'}
                    </div>
                  ))}
                </div>
              )}

              {!agentStatus.nearby_threats?.length && !agentStatus.nearby_opportunities?.length && (
                <p className="text-gray-400">No immediate threats or opportunities</p>
              )}
            </>
          ) : (
            <p className="text-gray-400">Analyzing nearby competitors...</p>
          )}
        </div>
      </CollapsibleBox>
    </div>
  )
}
