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

  // Mock data for position metrics
  const mockData = {
    currentPosition: positionData?.position || 3,
    gapAhead: positionData?.gap_ahead || '+0.5',
    gapBehind: positionData?.gap_behind || '-1.2',
    positionsGained: 0,

    // Live race positions
    positions: [
      { pos: 1, driver: 'VER', gap: 'LEADER', tire: 'M', team: 'Red Bull', arrow: null },
      { pos: 2, driver: 'LEC', gap: '+2.345', tire: 'M', team: 'Ferrari', arrow: null },
      { pos: 3, driver: 'YOU', gap: '+4.567', tire: 'S', team: 'You', arrow: null, isYou: true },
      { pos: 4, driver: 'PIA', gap: '+6.123', tire: 'M', team: 'McLaren', arrow: null },
      { pos: 5, driver: 'RUS', gap: '+8.901', tire: 'M', team: 'Mercedes', arrow: '▲' },
      { pos: 6, driver: 'HAM', gap: '+10.234', tire: 'M', team: 'Mercedes', arrow: '▼' },
      { pos: 7, driver: 'ALO', gap: '+12.567', tire: 'H', team: 'Aston Martin', arrow: null },
      { pos: 8, driver: 'STR', gap: '+15.890', tire: 'H', team: 'Aston Martin', arrow: null },
      { pos: 9, driver: 'SAI', gap: '+18.123', tire: 'M', team: 'Ferrari', arrow: '▲' },
      { pos: 10, driver: 'BOT', gap: '+20.456', tire: 'H', team: 'Kick Sauber', arrow: '▼' }
    ],

    // Position history
    history: [
      { lap: 1, position: 3, change: 'START' },
      { lap: Math.max(5, Math.floor((currentLap || 1) / 2)), position: positionData?.position || 3, change: '---' },
      { lap: currentLap || 1, position: positionData?.position || 3, change: 'CURRENT' }
    ],

    // Battle data
    battles: [
      {
        title: `BATTLE FOR P${positionData?.position || 3}`,
        ahead: { pos: (positionData?.position || 3) - 1, driver: 'LEC', team: 'Ferrari' },
        behind: { pos: positionData?.position || 3, driver: 'YOU', team: 'You' },
        gap: '+0.189'
      },
      {
        title: 'BATTLE FOR P9th',
        ahead: { pos: 9, driver: 'SAI', team: 'Ferrari' },
        behind: { pos: 10, driver: 'BOT', team: 'Kick Sauber' },
        gap: '+0.324'
      }
    ]
  }

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
                <div className="position-stat-value-large">P{mockData.currentPosition}</div>
              </div>
              <div className="position-stat-grid">
                <div className="position-stat-item">
                  <div className="position-stat-label">GAP AHEAD</div>
                  <div className="position-stat-value">{mockData.gapAhead}</div>
                </div>
                <div className="position-stat-item">
                  <div className="position-stat-label">GAP BEHIND</div>
                  <div className="position-stat-value">{mockData.gapBehind}</div>
                </div>
                <div className="position-stat-item">
                  <div className="position-stat-label">GAINED</div>
                  <div className="position-stat-value positive">+{mockData.positionsGained}</div>
                </div>
              </div>
            </div>

            {/* Live Race Positions */}
            <div className="live-positions-section">
              <div className="section-title">LIVE RACE POSITIONS - LAP {currentLap || 1}</div>
              <div className="race-positions-grid">
                {mockData.positions.map((p, idx) => (
                  <div key={idx} className={`position-row ${p.isYou ? 'your-position' : ''} ${p.pos === 1 ? 'leader' : ''}`}>
                    <div className="pos-number">{p.pos}</div>
                    <div className="pos-arrow">{p.arrow && <span className={p.arrow === '▲' ? 'arrow-up' : 'arrow-down'}>{p.arrow}</span>}</div>
                    <div className="pos-driver-name">{p.driver}</div>
                    <div className="pos-gap">{p.gap}</div>
                    <div className="pos-tire-compound">{p.tire}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Side - Position History, Battles & Race Info */}
          <div className="position-analysis-section">
            {/* Position History */}
            <div className="position-history-section">
              <div className="section-title">POSITION HISTORY</div>
              <div className="history-grid">
                {mockData.history.map((h, idx) => (
                  <div key={idx} className="history-item">
                    <span className="history-lap">Lap {h.lap}</span>
                    <span className={`history-pos ${h.change === 'CURRENT' ? 'highlight' : ''}`}>P{h.position}</span>
                    <span className="history-change">{h.change}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Battles */}
            <div className="battles-section">
              <div className="section-title">ACTIVE BATTLES</div>
              <div className="battles-grid">
                {mockData.battles.map((battle, idx) => (
                  <div key={idx} className="battle-card">
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
              <div className="race-info-label">BAHRAIN GRAND PRIX</div>
              <div className="race-info-lap">LAP {currentLap || 1} / 57</div>
              <div className="race-info-location">Sakhir, Bahrain</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PositionModal
