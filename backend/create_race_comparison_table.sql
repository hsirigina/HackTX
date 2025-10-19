-- Create race_comparison table for visual split-screen demo
CREATE TABLE IF NOT EXISTS race_comparison (
  id BIGSERIAL PRIMARY KEY,
  race_id TEXT NOT NULL,
  driver_name TEXT NOT NULL,
  lap_number INTEGER NOT NULL,

  -- AI Strategy state
  ai_cumulative_time FLOAT NOT NULL,
  ai_tire_compound TEXT NOT NULL,
  ai_tire_age INTEGER NOT NULL,
  ai_has_pitted BOOLEAN DEFAULT FALSE,
  ai_pit_lap INTEGER,

  -- Baseline state
  baseline_cumulative_time FLOAT NOT NULL,
  baseline_tire_compound TEXT NOT NULL,
  baseline_tire_age INTEGER NOT NULL,
  baseline_has_pitted BOOLEAN DEFAULT FALSE,
  baseline_pit_lap INTEGER,

  -- Meta
  time_difference FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Unique constraint: one record per lap per driver
  UNIQUE(race_id, driver_name, lap_number)
);

-- Add index for fast lookups
CREATE INDEX IF NOT EXISTS idx_race_comparison_lookup
ON race_comparison(race_id, driver_name, lap_number DESC);
