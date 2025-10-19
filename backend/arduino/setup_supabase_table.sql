-- Arduino Driver Display Communication Table
-- Run this in your Supabase SQL Editor

-- Drop existing table if needed (be careful!)
-- DROP TABLE IF EXISTS driver_display;

-- Create main table
CREATE TABLE IF NOT EXISTS driver_display (
  id BIGSERIAL PRIMARY KEY,
  race_id VARCHAR(50),
  message_type VARCHAR(50) NOT NULL,  -- 'PIT_NOW', 'ENGINEER_ALERT', 'STRATEGY', 'LAP_UPDATE', 'PIT_COUNTDOWN'
  content JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  acknowledged BOOLEAN DEFAULT FALSE,
  priority INTEGER DEFAULT 0  -- Higher = more urgent (0=normal, 5=engineer alert, 10=pit now)
);

-- Indexes for fast polling
CREATE INDEX IF NOT EXISTS idx_driver_display_unack 
  ON driver_display(acknowledged, created_at DESC) 
  WHERE acknowledged = FALSE;

CREATE INDEX IF NOT EXISTS idx_driver_display_race 
  ON driver_display(race_id);

CREATE INDEX IF NOT EXISTS idx_driver_display_priority 
  ON driver_display(priority DESC, created_at DESC);

-- Enable Row Level Security
ALTER TABLE driver_display ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations (adjust based on your auth setup)
CREATE POLICY "Allow all operations on driver_display" 
  ON driver_display FOR ALL 
  USING (true) 
  WITH CHECK (true);

-- Test insert
INSERT INTO driver_display (race_id, message_type, content, priority) 
VALUES (
  'test_race',
  'TEST',
  '{"message": "System ready", "timestamp": "2025-10-18"}'::jsonb,
  0
);

-- Verify
SELECT * FROM driver_display ORDER BY created_at DESC LIMIT 5;

-- Clean up test data
DELETE FROM driver_display WHERE message_type = 'TEST';

