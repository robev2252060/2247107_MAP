-- =============================================================================
-- Mars Automation Platform - PostgreSQL Schema
-- Created: March 10, 2026
-- Based on: components.yaml OpenAPI specification
-- =============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS mars;

SET search_path TO mars, public;

-- =============================================================================
-- AUTOMATION RULES
-- =============================================================================
-- Based on: components.yaml#/components/schemas/AutomationRule
--
-- Stores automation rules for the Mars Habitat control system.
-- IF sensor_source.sensor_metric <operator> threshold_value
-- THEN set target_actuator to target_state
-- =============================================================================

CREATE TABLE IF NOT EXISTS rules (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Rule definition (required fields from AutomationRule schema)
    sensor_source VARCHAR(255) NOT NULL,      -- e.g., "rest:greenhouse_temperature"
    sensor_metric VARCHAR(255) NOT NULL,      -- e.g., "temperature"
    operator VARCHAR(10) NOT NULL CHECK (operator IN ('<', '<=', '=', '>', '>=')),
    threshold_value DOUBLE PRECISION NOT NULL,
    target_actuator VARCHAR(255) NOT NULL,    -- e.g., "cooling_fan"
    target_state VARCHAR(10) NOT NULL CHECK (target_state IN ('ON', 'OFF')),

    -- Optional fields
    enabled BOOLEAN DEFAULT TRUE,
    description TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_rules_sensor_source ON rules(sensor_source) WHERE enabled = TRUE;
CREATE INDEX idx_rules_enabled ON rules(enabled);
CREATE INDEX idx_rules_created_at ON rules(created_at DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_rules_updated_at
    BEFORE UPDATE ON rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- RULE EXECUTIONS (AUDIT TRAIL)
-- =============================================================================
-- Tracks when rules are triggered/cleared for auditing and debugging.
-- =============================================================================

CREATE TABLE IF NOT EXISTS rule_executions (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES rules(id) ON DELETE CASCADE,

    -- Execution details
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    execution_result VARCHAR(50) NOT NULL,    -- 'triggered', 'cleared', etc.

    -- Context data (JSONB for flexibility)
    details JSONB,                            -- sensor values, conditions, etc.

    -- Index for time-series queries
    CONSTRAINT valid_execution_result CHECK (execution_result IN ('triggered', 'cleared', 'error'))
);

CREATE INDEX idx_rule_executions_rule_id ON rule_executions(rule_id);
CREATE INDEX idx_rule_executions_triggered_at ON rule_executions(triggered_at DESC);
CREATE INDEX idx_rule_executions_result ON rule_executions(execution_result);

-- =============================================================================
-- COMMENTS & DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE rules IS 'Automation rules for habitat control (ms-rulebook service)';
COMMENT ON COLUMN rules.sensor_source IS 'Source identifier from MeasurementEvent (e.g., rest:greenhouse_temperature)';
COMMENT ON COLUMN rules.sensor_metric IS 'Specific metric to monitor from readings array (e.g., temperature)';
COMMENT ON COLUMN rules.operator IS 'Comparison operator: <, <=, =, >=, >';
COMMENT ON COLUMN rules.threshold_value IS 'Numeric threshold for comparison';
COMMENT ON COLUMN rules.target_actuator IS 'Actuator to control when rule triggers';
COMMENT ON COLUMN rules.target_state IS 'Desired actuator state: ON or OFF';
COMMENT ON COLUMN rules.enabled IS 'Whether rule is active and should be evaluated';

COMMENT ON TABLE rule_executions IS 'Audit trail of rule evaluations (ms-automation service)';
COMMENT ON COLUMN rule_executions.details IS 'JSONB context: {sensor_source, sensor_metric, measurement_value, threshold_value, timestamp}';

-- =============================================================================
-- SAMPLE DATA (OPTIONAL - COMMENTED OUT)
-- =============================================================================
-- Uncomment to insert sample rules for testing
--
-- INSERT INTO mars.rules (sensor_source, sensor_metric, operator, threshold_value, target_actuator, target_state, description) VALUES
-- ('rest:greenhouse_temperature', 'temperature', '>', 28.0, 'cooling_fan', 'ON', 'Turn on cooling when temperature exceeds 28°C'),
-- ('rest:water_tank_level', 'level_pct', '<', 20.0, 'water_alarm', 'ON', 'Alert when water level drops below 20%'),
-- ('stream:mars/telemetry/power_bus', 'voltage_v', '<', 380.0, 'power_alarm', 'ON', 'Alert on low voltage');

-- =============================================================================
-- SCHEMA VERSION
-- =============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO mars.schema_version (version, description) VALUES
('1.0.0', 'Initial schema based on components.yaml - AutomationRule support');

COMMIT;
