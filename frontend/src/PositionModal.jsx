import { useState, useEffect } from 'react'
import './PositionModal.css'

function PositionModal({ isOpen, onClose, positionData, currentLap }) {
  const [animateIn, setAnimateIn] = useState(false)
  const [animateBars, setAnimateBars] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setAnimateIn(true)
      setTimeout(() => setAnimateBars(true), 300)
    } else {
      setAnimateBars(false)
    }
  }, [isOpen])

  const handleClose = () => {
    setAnimateIn(false)
    setTimeout(onClose, 300)
  }

  if (!isOpen) return null

  const currentPosition = Number(positionData?.position) || 3

  const formatGap = (value) => {
    if (value === null || value === undefined) return '--'
    if (typeof value === 'string') {
      const trimmed = value.trim()
      if (!trimmed.length) return '--'
      return trimmed
    }
    const numeric = Number(value)
    if (Number.isNaN(numeric)) return '--'
    if (Math.abs(numeric) < 0.05) return 'LEADER'
    return `${numeric > 0 ? '+' : ''}${numeric.toFixed(2)}s`
  }

  const normalizeArrow = (value) => {
    if (!value) return null
    if (value === '▲' || value === '▼') return value
    const lowered = String(value).toLowerCase()
    if (['up', 'gain', 'gaining', 'positive', 'improving'].includes(lowered)) return '▲'
    if (['down', 'loss', 'losing', 'negative', 'falling'].includes(lowered)) return '▼'
    return null
  }

  const normalizeTire = (value) => {
    if (!value) return '--'
    const upper = String(value).toUpperCase()
    if (upper.length <= 2) return upper
    if (['SOFT', 'MEDIUM', 'HARD'].includes(upper)) {
      return upper.startsWith('SO') ? 'S' : upper.startsWith('ME') ? 'M' : 'H'
    }
    return upper
  }

  const fallbackDriverOrder = ['VER', 'PER', 'LEC', 'SAI', 'NOR', 'PIA', 'HAM', 'RUS', 'ALO', 'STR', 'GAS', 'OCO', 'TSU', 'RIC', 'ALB', 'SAR', 'BOT', 'ZHO', 'MAG', 'HUL']
  const fallbackTires = ['S', 'M', 'H']

  const createFallbackPositions = () => {
    const windowSize = 10
    let startPos = currentPosition - Math.floor(windowSize / 2)
    startPos = Math.max(1, startPos)
    if (startPos + windowSize - 1 > 20) {
      startPos = Math.max(1, 20 - windowSize + 1)
    }

    const positions = []
    for (let i = 0; i < windowSize && startPos + i <= 20; i += 1) {
      const pos = startPos + i
      const isYou = pos === currentPosition
      const driverIndex = (pos - 1) % fallbackDriverOrder.length
      const driver = isYou ? 'YOU' : fallbackDriverOrder[driverIndex]
      const leaderGap = pos === startPos ? 'LEADER' : `+${(Math.abs(pos - startPos) * 1.5 + (isYou ? 0.0 : 1.8)).toFixed(2)}s`
      positions.push({
        pos,
        driver,
        gap: leaderGap,
        tire: isYou ? normalizeTire(positionData?.tire || positionData?.tire_compound || positionData?.compound || 'S') : fallbackTires[i % fallbackTires.length],
        team: isYou ? 'You' : 'Rival Team',
        arrow: null,
        isYou
      })
    }

    if (!positions.some((entry) => entry.isYou)) {
      positions.push({
        pos: currentPosition,
        driver: 'YOU',
        gap: formatGap(positionData?.gap_ahead),
        tire: normalizeTire(positionData?.tire || positionData?.tire_compound || positionData?.compound || 'S'),
        team: 'You',
        arrow: null,
        isYou: true
      })
    }

    return positions.sort((a, b) => a.pos - b.pos)
  }

  const rawPositions =
    (Array.isArray(positionData?.live_positions) && positionData.live_positions) ||
    (Array.isArray(positionData?.positions) && positionData.positions) ||
    (Array.isArray(positionData?.livePositions) && positionData.livePositions) ||
    []

  const normalizedPositions = rawPositions
    .map((entry, index) => {
      if (!entry) return null
      const positionNumber = Number(entry.pos ?? entry.position ?? entry.rank ?? (index + 1))
      const driver = entry.driver ?? entry.code ?? entry.name ?? `DRV${positionNumber}`
      const gapValue = entry.gap ?? entry.interval ?? entry.interval_seconds ?? entry.gap_to_leader
      const tireValue = entry.tire ?? entry.compound ?? entry.tyre ?? entry.tyre_compound
      const teamValue = entry.team ?? entry.constructor ?? entry.team_name ?? ''
      const arrowValue = entry.arrow ?? entry.trend ?? entry.delta

      return {
        pos: Number.isNaN(positionNumber) ? index + 1 : positionNumber,
        driver: String(driver).toUpperCase(),
        gap: formatGap(gapValue),
        tire: normalizeTire(tireValue),
        team: teamValue,
        arrow: normalizeArrow(arrowValue),
        isYou: entry.isYou === true || String(driver).toUpperCase() === 'YOU' || Number(positionNumber) === currentPosition
      }
    })
    .filter(Boolean)
    .sort((a, b) => a.pos - b.pos)

  const positions = normalizedPositions.length ? normalizedPositions : createFallbackPositions()

  const gapAhead = formatGap(positionData?.gap_ahead)
  const gapBehind = formatGap(positionData?.gap_behind)

  const startingPosition = Number(
    positionData?.starting_position ??
    positionData?.startingPosition ??
    positionData?.grid_position ??
    positionData?.gridPosition
  )

  const positionsGainedValue = Number(
    positionData?.positions_gained ??
    positionData?.positionsGained ??
    (Number.isFinite(startingPosition) ? startingPosition - currentPosition : 0)
  )

  const positionsGainedDisplay = Number.isFinite(positionsGainedValue)
    ? `${positionsGainedValue > 0 ? '+' : ''}${positionsGainedValue}`
    : '+0'

  const positionsGainedClass =
    Number.isFinite(positionsGainedValue) && positionsGainedValue < 0
      ? 'position-stat-value negative'
      : Number.isFinite(positionsGainedValue) && positionsGainedValue > 0
        ? 'position-stat-value positive'
        : 'position-stat-value'

  const historyEntries = Array.isArray(positionData?.history) && positionData.history.length
    ? positionData.history.map((item, index) => ({
        lap: item.lap ?? item.lap_number ?? item.lapNumber ?? index + 1,
        position: item.position ?? item.pos ?? currentPosition,
        change: item.change ?? item.status ?? ''
      })).filter((item) => item.lap && item.position)
    : [
        { lap: 1, position: Number.isFinite(startingPosition) ? startingPosition : currentPosition, change: 'Start' },
        { lap: Math.max(2, Math.floor((currentLap || currentPosition) / 2)), position: currentPosition, change: 'Mid' },
        { lap: currentLap || 1, position: currentPosition, change: 'Current' }
      ]

  const battleEntries = Array.isArray(positionData?.battles) && positionData.battles.length
    ? positionData.battles.map((battle, index) => ({
        title: battle.title ?? battle.name ?? `Battle for P${battle.target_position ?? currentPosition}`,
        ahead: {
          pos: battle.ahead?.position ?? battle.ahead_pos ?? (battle.target_position ?? currentPosition) - 1,
          driver: battle.ahead?.driver ?? battle.ahead_driver ?? '---',
          team: battle.ahead?.team ?? battle.ahead_team ?? ''
        },
        behind: {
          pos: battle.behind?.position ?? battle.behind_pos ?? (battle.target_position ?? currentPosition),
          driver: battle.behind?.driver ?? battle.behind_driver ?? '---',
          team: battle.behind?.team ?? battle.behind_team ?? ''
        },
        gap: formatGap(battle.gap ?? battle.interval ?? battle.delta)
      }))
    : [
        {
          title: `Battle for P${currentPosition}`,
          ahead: { pos: Math.max(1, currentPosition - 1), driver: 'RIVAL', team: 'Ferrari' },
          behind: { pos: currentPosition, driver: 'YOU', team: 'You' },
          gap: formatGap(positionData?.gap_ahead ?? 0.2)
        },
        {
          title: `Battle for P${Math.min(currentPosition + 2, 20)}`,
          ahead: { pos: Math.min(currentPosition + 1, 20), driver: 'CHASE', team: 'Mercedes' },
          behind: { pos: Math.min(currentPosition + 2, 20), driver: 'PRESS', team: 'McLaren' },
          gap: '+0.32s'
        }
      ]

  const raceNameRaw = positionData?.race_name ?? positionData?.raceName ?? 'Bahrain Grand Prix'
  const raceName = typeof raceNameRaw === 'string' ? raceNameRaw.toUpperCase() : 'BAHRAIN GRAND PRIX'
  const totalLaps = Number(positionData?.total_laps ?? positionData?.totalLaps ?? positionData?.laps ?? 57)
  const raceLocation = positionData?.location ?? positionData?.track ?? 'Sakhir, Bahrain'

  return (
    <div className={`position-modal-overlay ${animateIn ? 'active' : ''}`} onClick={handleClose}>
      <div className={`position-modal-container ${animateIn ? 'active' : ''}`} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="position-modal-header">
          <div className="position-modal-title">
            <span className="position-icon"><img src="/flagAgent.png" alt="Position Agent" /></span>
            POSITION ANALYSIS
          </div>
          <button className="position-close-btn" onClick={handleClose}>✕</button>
        </div>

        {/* Content Grid */}
        <div className="position-modal-content">
          {/* Left Side - Current Position & Live Positions */}
          <div className="position-status-section">
            {/* Current Position Status */}
            <div className="position-stats-header">
              <div className="position-stat-item large">
                <div className="position-stat-label">CURRENT POSITION</div>
                <div className="position-stat-value-large">P{currentPosition}</div>
              </div>
              <div className="position-stat-grid">
                <div className="position-stat-item">
                  <div className="position-stat-label">GAP AHEAD</div>
                  <div className="position-stat-value">{gapAhead}</div>
                </div>
                <div className="position-stat-item">
                  <div className="position-stat-label">GAP BEHIND</div>
                  <div className="position-stat-value">{gapBehind}</div>
                </div>
                <div className="position-stat-item">
                  <div className="position-stat-label">GAINED</div>
                  <div className={positionsGainedClass}>{positionsGainedDisplay}</div>
                </div>
              </div>
            </div>

            {/* Live Race Positions */}
            <div className="live-positions-section">
              <div className="section-title">LIVE RACE POSITIONS - LAP {currentLap || 1}</div>
              <div className="race-positions-grid">
                {positions.length ? (
                  positions.map((p, idx) => (
                    <div key={`${p.driver}-${p.pos}-${idx}`} className={`position-row ${p.isYou ? 'your-position' : ''} ${p.pos === 1 ? 'leader' : ''}`}>
                      <div className="pos-number">{p.pos}</div>
                      <div className="pos-arrow">{p.arrow && <span className={p.arrow === '▲' ? 'arrow-up' : 'arrow-down'}>{p.arrow}</span>}</div>
                      <div className="pos-driver-name">{p.driver}</div>
                      <div className="pos-gap">{p.gap}</div>
                      <div className="pos-tire-compound">{p.tire}</div>
                    </div>
                  ))
                ) : (
                  <div className="position-empty-state">Live position data unavailable</div>
                )}
              </div>
            </div>
          </div>

          {/* Right Side - Position History, Battles & Race Info */}
          <div className="position-analysis-section">
            {/* Position History */}
            <div className="position-history-section">
              <div className="section-title">POSITION HISTORY</div>
              <div className="history-grid">
                {historyEntries.map((h, idx) => (
                  <div key={`${h.lap}-${idx}`} className="history-item">
                    <span className="history-lap">Lap {h.lap}</span>
                    <span className={`history-pos ${String(h.change).toUpperCase() === 'CURRENT' ? 'highlight' : ''}`}>P{h.position}</span>
                    <span className="history-change">{h.change}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Battles */}
            <div className="battles-section">
              <div className="section-title">ACTIVE BATTLES</div>
              <div className="battles-grid">
                {battleEntries.map((battle, idx) => (
                  <div key={`${battle.title}-${idx}`} className="battle-card">
                    <div className="battle-header">{battle.title}</div>
                    <div className="battle-drivers">
                      <div className="battle-driver ahead">
                        <div className="battle-pos">P{battle.ahead.pos}</div>
                        <div className="battle-name">{battle.ahead.driver}</div>
                        <div className="battle-team">{battle.ahead.team}</div>
                      </div>
                      <div className="battle-gap">{battle.gap}</div>
                      <div className="battle-driver behind">
                        <div className="battle-pos">P{battle.behind.pos}</div>
                        <div className="battle-name">{battle.behind.driver}</div>
                        <div className="battle-team">{battle.behind.team}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Race Info */}
            <div className="race-info-section">
              <div className="race-info-label">{raceName}</div>
              <div className="race-info-lap">LAP {currentLap || 1} / {Number.isFinite(totalLaps) && totalLaps > 0 ? totalLaps : '--'}</div>
              <div className="race-info-location">{raceLocation}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PositionModal
