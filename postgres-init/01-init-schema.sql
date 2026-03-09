-- =============================================================================
-- MARS IoT System PostgreSQL Schema
-- Stores all system data: sensor readings, states, rules, actuations, logs
-- =============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS mars;

SET search_path TO mars, public;

-- =============================================================================
-- CORE ENTITIES
-- =============================================================================

-- Sensors/Devices
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sensor Readings (from Kafka - ingestion service)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id),
    device_id VARCHAR(255),
    measurement_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device ON sensor_readings(device_id);

-- Processed Data (from processing-service)
CREATE TABLE IF NOT EXISTS processed_data (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id),
    device_id VARCHAR(255),
    normalized_value FLOAT,
    status VARCHAR(50),
    anomaly_detected BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_processed_data_timestamp ON processed_data(processed_at);

-- =============================================================================
-- STATE MANAGEMENT
-- =============================================================================

-- Current State of Devices (from state-service)
CREATE TABLE IF NOT EXISTS device_states (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    state JSONB NOT NULL,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- State History (audit trail)
CREATE TABLE IF NOT EXISTS state_history (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_state_history_device ON state_history(device_id);
CREATE INDEX IF NOT EXISTS idx_state_history_timestamp ON state_history(changed_at);

-- =============================================================================
-- RULES & ACTIONS
-- =============================================================================

-- Automation Rules (from rule-service)
-- IF sensor_id <operator> threshold THEN set actuator_id to actuator_state
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(255) NOT NULL,
    operator VARCHAR(10) NOT NULL CHECK (operator IN ('<', '<=', '=', '>=', '>')),
    threshold FLOAT NOT NULL,
    unit VARCHAR(50),
    actuator_id VARCHAR(255) NOT NULL,
    actuator_state VARCHAR(10) NOT NULL CHECK (actuator_state IN ('ON', 'OFF')),
    enabled BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rules_sensor ON rules(sensor_id);
CREATE INDEX IF NOT EXISTS idx_rules_enabled ON rules(enabled);

-- Rule Executions (audit trail)
CREATE TABLE IF NOT EXISTS rule_executions (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES rules(id),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_result VARCHAR(50),
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_rule_executions_rule ON rule_executions(rule_id);
CREATE INDEX IF NOT EXISTS idx_rule_executions_timestamp ON rule_executions(triggered_at);

-- =============================================================================
-- ACTUATIONS
-- =============================================================================

-- Actuator Commands (from actuator-service)
CREATE TABLE IF NOT EXISTS actuator_commands (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    command VARCHAR(100) NOT NULL,
    parameters JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_actuator_commands_device ON actuator_commands(device_id);
CREATE INDEX IF NOT EXISTS idx_actuator_commands_status ON actuator_commands(status);

-- =============================================================================
-- API & SYSTEM LOGS
-- =============================================================================

-- API Request Log
CREATE TABLE IF NOT EXISTS api_requests (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    request_body JSONB,
    response_body JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_api_requests_endpoint ON api_requests(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_requests_timestamp ON api_requests(timestamp);

-- System Events Log
CREATE TABLE IF NOT EXISTS system_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    service_name VARCHAR(100),
    message TEXT,
    severity VARCHAR(20) DEFAULT 'info',
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(created_at);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_sensors_type ON sensors(type);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_value ON sensor_readings(value);
CREATE INDEX IF NOT EXISTS idx_processed_data_anomaly ON processed_data(anomaly_detected);

-- =============================================================================
-- VIEWS FOR EASY ACCESS
-- =============================================================================

-- Latest readings per sensor
CREATE OR REPLACE VIEW latest_readings AS
SELECT 
    s.device_id,
    s.name,
    sr.measurement_type,
    sr.value,
    sr.unit,
    sr.timestamp
FROM sensors s
LEFT JOIN sensor_readings sr ON s.id = sr.sensor_id
WHERE sr.timestamp = (
    SELECT MAX(timestamp) 
    FROM sensor_readings 
    WHERE sensor_id = s.id
);

-- Active anomalies
CREATE OR REPLACE VIEW active_anomalies AS
SELECT 
    device_id,
    COUNT(*) as anomaly_count,
    MAX(processed_at) as last_anomaly
FROM processed_data
WHERE anomaly_detected = TRUE
  AND processed_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY device_id;

COMMIT;
