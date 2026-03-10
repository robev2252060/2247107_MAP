# Student_doc.md — Mars IoT Platform

## Tech Stack

| Layer | Technology |
|---|---|
| Backend microservices | Python 3.12 + FastAPI |
| Message broker | Apache Kafka (Confluent Platform 7.5) |
| Database | MongoDB 7.0 (Motor async driver) |
| Frontend | React 18 + Vite 5 |
| API Gateway | Nginx 1.25 |
| Containerisation | Docker + Docker Compose |

---

## Microservice Responsibilities

### ingestion-service (port 8000)
- Polls all 8 REST sensors every 5 seconds (configurable via `POLL_INTERVAL_SECONDS`)
- Publishes raw payloads to Kafka topic `mars.raw.sensors`
- No external API; exposes only `/health`

### processing-service (port 8001)
- Consumes `mars.raw.sensors`
- Normalises each raw payload into the unified **MarsEvent** schema (see `input.md`)
- Publishes normalised events to `mars.normalized.events`
- Fetches active rules from MongoDB and evaluates them via the rule engine
- Publishes matched actuator commands to `mars.actuator.commands`

### state-service (port 8002)
- Consumes `mars.normalized.events`
- Maintains an in-memory dict of `{sensor_id → latest MarsEvent}`
- REST API: `GET /sensors`, `GET /sensors/{id}`
- SSE API: `GET /sensors/stream/sse` — streams `snapshot` + `sensor_update` events to the dashboard

### rule-service (port 8003)
- Full CRUD REST API for automation rules persisted in MongoDB
- Validates sensor/actuator names and operator syntax on write
- Endpoints: `GET /rules/`, `POST /rules/`, `GET /rules/{id}`, `PATCH /rules/{id}`, `DELETE /rules/{id}`

### actuator-service (port 8004)
- Consumes `mars.actuator.commands` from Kafka (automated triggers)
- REST API for manual actuator control from the frontend
- Translates commands into `POST /api/actuators/{id}` calls to the simulator

---

## Data Flow

```
Simulator REST sensors
    → ingestion-service (poll every 5s)
        → [Kafka: mars.raw.sensors]
            → processing-service (normalise + rule evaluation)
                → [Kafka: mars.normalized.events]
                    → state-service (in-memory cache + SSE)
                → [Kafka: mars.actuator.commands]
                    → actuator-service → Simulator actuator REST
```

---

## Starting the Platform

```bash
# 1. Load the simulator image
docker load -i mars-iot-simulator-oci.tar

# 2. Start everything
docker compose up --build

# 3. Access
#   Dashboard:  http://localhost/
#   Rule CRUD:  http://localhost/api/rules/
#   State API:  http://localhost/api/state/sensors
#   Actuators:  http://localhost/api/actuators/
#     returns JSON array `[{{id,state}}…]` rather than an object; this
#     matches what the frontend dashboard expects.
```

---

## Configuration (environment variables)

All values have sensible defaults and are overridable via `docker-compose.yml`.

| Variable | Service | Default |
|---|---|---|
| `SIMULATOR_BASE_URL` | ingestion, actuator | `http://simulator:8080` |
| `KAFKA_BOOTSTRAP_SERVERS` | all | `kafka:29092` |
| `POLL_INTERVAL_SECONDS` | ingestion | `5` |
