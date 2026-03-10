# SYSTEM DESCRIPTION:

Mars Automation Platform (MAP) is a distributed automation system for a Mars habitat. It integrates heterogeneous sensors (polling and streaming), normalizes telemetry into a unified internal format, evaluates IF-THEN automation rules, and controls actuators while exposing a real-time operator dashboard.

The system is organized as microservices behind an API gateway, with asynchronous communication through Kafka and persistent storage in PostgreSQL.

# USER STORIES:

1) As an Operator, I want to view a centralized dashboard of all habitat sensors so that I can monitor the overall health of the Mars base.
2) As an Operator, I want to see the most recent reading from each sensor instantly upon opening the dashboard so that I do not have to wait for the next data broadcast.
3) As an Operator, I want sensor data to update automatically on my screen without refreshing so that I am always looking at live telemetry.
4) As an Operator, I want to see standardized units and naming conventions for all data, regardless of source, so I do not misinterpret critical life-support metrics.
5) As an Operator, I want to view a live line chart for selected sensors while the page is open so that I can visually track rapid environmental trends.
6) As an Operator, I want sensors to be grouped by operational domain so that I can quickly find related metrics during an emergency.
7) As an Operator, I want the dashboard to display the exact time of the last data point so that I can understand data freshness.
8) As an Operator, I want a visual indicator when a sensor's data is older than 5 minutes so that I do not trust stale telemetry.
9) As a Habitat Administrator, I want to configure the global polling frequency for legacy sensors so that I can balance responsiveness and network load.
10) As an Operator, I want to manually refresh all actuator states from the dashboard so that I can verify physical status immediately.
11) As an Automation Engineer, I want to create rules in sentence form (IF sensor operator value THEN actuator state) so that I can script habitat behavior easily.
12) As an Automation Engineer, I want to select sensors and actuators from predefined lists when creating a rule so that I avoid typing errors.
13) As an Automation Engineer, I want to define rule conditions using operators `(<, <=, =, >, >=)` so that I can set precise thresholds.
14) As an Automation Engineer, I want to view a list of active rules so that I can audit habitat automation logic.
15) As an Automation Engineer, I want to delete automation rules so that I can remove outdated or unsafe logic.
16) As an Automation Engineer, I want to edit existing rules so that I can adjust thresholds as habitat conditions change.
17) As an Automation Engineer, I want to disable and re-enable rules without deleting them so that I can perform maintenance safely.
18) As a Habitat Administrator, I want automation rules to be permanently stored so that they survive restarts and power cycles.
19) As an Operator, I want the dashboard to display data from all habitat sensors regardless of transmission method so that no area is unmonitored.
20) As an Operator, I want the system to evaluate rules immediately when new sensor data arrives so that life-saving equipment can react quickly.
21) As an Operator, I want the monitoring dashboard to remain usable even if the automation engine is unavailable so that I can continue manual supervision.
22) As an Operator, I want a visual alert when a sensor is out of normal bounds even before a rule fires so that I get early warning.
23) As an Operator, I want a global system connection indicator (Green/Red) so that I immediately know if the UI has lost backend stream connectivity.
24) As an Operator, I want to be notified with a toast whenever an automated rule changes the state of an actuator, so that I know immediately what's going on in my habitat.

# CONTAINERS:

## CONTAINER_NAME: Mars-Gateway

### DESCRIPTION:
Single public entry point that routes browser requests to internal services and serves the frontend through reverse proxy.

### USER STORIES:
1, 3, 9, 10, 11, 14, 15, 16, 17, 23

### PORTS:
80:80

### DESCRIPTION:
Implements edge routing with Nginx. It proxies REST and SSE endpoints for integration, rule management, and actuator control.

### PERSISTENCE EVALUATION
No persistent data is stored in this container.

### EXTERNAL SERVICES CONNECTIONS
No direct external third-party services. Routes requests toward internal Docker network services.

### MICROSERVICES:

#### MICROSERVICE: nginx
- TYPE: middleware
- DESCRIPTION: Reverse proxy and API gateway for all frontend and backend traffic.
- PORTS: 80
- TECHNOLOGICAL SPECIFICATION:
Nginx 1.25 Alpine image, configured with upstream blocks and route mapping for `/api/integration/*`, `/api/rules/*`, `/api/actuators*`, and `/`.
- SERVICE ARCHITECTURE:
Single stateless process with path-based routing and SSE-friendly proxy settings (`proxy_buffering off`, long read timeout).

## CONTAINER_NAME: Mars-Frontend

### DESCRIPTION:
Web user interface used by operators and automation engineers for monitoring sensors, managing rules, and controlling actuators.

### USER STORIES:
1, 2, 3, 5, 6, 7, 10, 11, 12, 14, 15, 16, 17, 23

### PORTS:
3001:3000

### DESCRIPTION:
React SPA served in a container, accessed through the gateway. It consumes SSE streams and REST APIs exposed by backend services.

### PERSISTENCE EVALUATION
No server-side persistence. UI state is in-memory in the browser.

### EXTERNAL SERVICES CONNECTIONS
No direct external service usage; all data exchange happens via gateway routes.

### MICROSERVICES:

#### MICROSERVICE: frontend
- TYPE: frontend
- DESCRIPTION: React/Vite application with pages for dashboard, rules, and actuator control.
- PORTS: 3000
- TECHNOLOGICAL SPECIFICATION:
React 18, Vite 5, JavaScript modules. EventSource is used for real-time updates.
- SERVICE ARCHITECTURE:
Component-based SPA with page-level separation and API adapters (`integrationApi.js`, `ruleApi.js`, `actuatorApi.js`).

- PAGES:

| Name | Description | Related Microservice | User Stories               |
| ---- | ----------- | -------------------- |----------------------------|
| DashboardPage.jsx | Displays grouped live telemetry, line chart, and connection state | mars-ms-integration | 1, 2, 3, 5, 6, 7, 23, 24   |
| RulesPage.jsx | Rule CRUD UI with metric discovery from telemetry stream | mars-rulebook, mars-ms-integration | 11, 12, 13, 14, 15, 16, 17 |
| ActuatorsPage.jsx | Actuator list, manual toggle, and manual refresh | mars-ms-actuators | 10, 23, 24                 |

## CONTAINER_NAME: Mars-MS-Integration

### DESCRIPTION:
Ingests heterogeneous simulator telemetry, handles polling configuration, and exposes normalized measurement stream to clients.

### USER STORIES:
2, 3, 4, 9, 19, 21

### PORTS:
internal 8080 (not published to host)

### DESCRIPTION:
Spring Boot service responsible for sensor stream fan-out and polling-rate control APIs.

### PERSISTENCE EVALUATION
No durable storage in this service. It acts as integration and streaming layer.

### EXTERNAL SERVICES CONNECTIONS
Reads sensor data from external simulator endpoints and publishes measurement events to Kafka.

### MICROSERVICES:

#### MICROSERVICE: ms-integration
- TYPE: backend
- DESCRIPTION: Provides SSE sensor stream and polling-rate management for legacy sensors.
- PORTS: 8080
- TECHNOLOGICAL SPECIFICATION:
Java 17, Spring Boot, Spring Web, Spring Kafka. Uses `SseEmitter` for server-sent events.
- SERVICE ARCHITECTURE:
Controller layer (`SensorStreamController`, `PollingController`) with service layer for polling and event streaming.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /api/sensors/stream | Opens SSE stream of normalized measurement events | 2, 3, 19, 21, 23 |
| GET | /api/polling/rate | Returns current global polling interval | 9 |
| POST | /api/polling/rate | Updates global polling interval | 9 |

## CONTAINER_NAME: Mars-MS-Rulebook

### DESCRIPTION:
Stores and manages automation rules (CRUD) used by the automation engine.

### USER STORIES:
11, 12, 13, 14, 15, 16, 17, 18

### PORTS:
internal 8003 (not published to host)

### DESCRIPTION:
FastAPI service exposing REST endpoints for rule lifecycle operations.

### PERSISTENCE EVALUATION
Requires persistent storage in PostgreSQL to satisfy permanent rule storage.

### EXTERNAL SERVICES CONNECTIONS
Connects to PostgreSQL.

### MICROSERVICES:

#### MICROSERVICE: ms-rulebook
- TYPE: backend
- DESCRIPTION: Validates and persists automation rules.
- PORTS: 8003
- TECHNOLOGICAL SPECIFICATION:
Python 3.12, FastAPI, Pydantic, async PostgreSQL access, Uvicorn.
- SERVICE ARCHITECTURE:
Router-based API (`/api/rules`) with model validation and DB access module.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /health | Service health endpoint | - |
| GET | /api/rules/ | List all rules | 14 |
| POST | /api/rules/ | Create rule | 11, 12, 13 |
| GET | /api/rules/{rule_id} | Get one rule | 14 |
| PUT | /api/rules/{rule_id} | Update rule | 16, 17 |
| DELETE | /api/rules/{rule_id} | Delete rule | 15 |

## CONTAINER_NAME: Mars-MS-Automation

### DESCRIPTION:
Evaluates automation rules against incoming sensor measurements and emits actuator commands asynchronously.

### USER STORIES:
13, 17, 20, 21

### PORTS:
internal 8001 (not published to host)

### DESCRIPTION:
FastAPI service that consumes telemetry events and executes rule evaluation pipeline.

### PERSISTENCE EVALUATION
Reads/writes persistent data through PostgreSQL (rules and rule execution audit).

### EXTERNAL SERVICES CONNECTIONS
Connects to Kafka and PostgreSQL.

### MICROSERVICES:

#### MICROSERVICE: ms-automation
- TYPE: backend
- DESCRIPTION: Consumes measurement events, evaluates enabled rules, produces automation actuator commands.
- PORTS: 8001
- TECHNOLOGICAL SPECIFICATION:
Python 3.12, FastAPI, asyncio, AIOKafka-based consumer/producer, PostgreSQL.
- SERVICE ARCHITECTURE:
Event-driven background consumer started at service startup; REST exposure is limited to health endpoint.

## CONTAINER_NAME: Mars-MS-Actuators

### DESCRIPTION:
Handles manual and automated actuator commands and exposes current actuator states to the UI.

### USER STORIES:
10, 20, 21, 23

### PORTS:
internal 8004 (not published to host)

### DESCRIPTION:
FastAPI service consuming automation commands from Kafka and forwarding commands to simulator actuators.

### PERSISTENCE EVALUATION
No durable storage. State is fetched from simulator and cached in-memory for SSE snapshots.

### EXTERNAL SERVICES CONNECTIONS
Connects to Kafka and to simulator REST actuator endpoints.

### MICROSERVICES:

#### MICROSERVICE: ms-actuators
- TYPE: backend
- DESCRIPTION: Supports actuator state listing, manual override, and SSE stream of actuator updates.
- PORTS: 8004
- TECHNOLOGICAL SPECIFICATION:
Python 3.12, FastAPI, asyncio, AIOKafka consumer, EventSource-compatible SSE responses.
- SERVICE ARCHITECTURE:
Startup task consumes Kafka automation topic; HTTP layer serves manual control and stream APIs.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /health | Service health endpoint | - |
| GET | /api/actuators/stream | SSE stream of actuator state changes | 10, 23 |
| GET | /actuators/ | Returns current actuator states | 10 |
| POST | /actuators/{actuator_id} | Manually set actuator state | 10 |

## CONTAINER_NAME: Mars-Kafka

### DESCRIPTION:
Asynchronous event backbone for decoupled communication between ingestion/integration, automation, and actuation services.

### USER STORIES:
3, 19, 20, 21

### PORTS:
9094:9094 (external listener), internal 9092

### DESCRIPTION:
Kafka broker container used for telemetry and command topics.

### PERSISTENCE EVALUATION
Persistent broker log storage via Docker volume `kafka-data`.

### EXTERNAL SERVICES CONNECTIONS
No external third-party services.

### MICROSERVICES:

#### MICROSERVICE: kafka
- TYPE: middleware
- DESCRIPTION: Broker for event topics including measurements and actuator automation commands.
- PORTS: 9092, 9094
- TECHNOLOGICAL SPECIFICATION:
Apache Kafka 3.9 in KRaft mode (broker + controller roles).
- SERVICE ARCHITECTURE:
Single-node broker configuration for development deployment.

## CONTAINER_NAME: Mars-Postgres

### DESCRIPTION:
Central relational persistence for rules and rule execution history.

### USER STORIES:
18, 20

### PORTS:
internal 5432 (not published to host)

### DESCRIPTION:
PostgreSQL schema includes `mars.rules`, `mars.rule_executions`, and `mars.schema_version`.

### PERSISTENCE EVALUATION
Primary persistent store of the platform. Data survives container restarts through Docker volume `postgres-data`.

### EXTERNAL SERVICES CONNECTIONS
No external third-party services.

### MICROSERVICES:

#### MICROSERVICE: postgres
- TYPE: database
- DESCRIPTION: Stores rule definitions and execution audit data.
- PORTS: 5432
- TECHNOLOGICAL SPECIFICATION:
PostgreSQL 16 (alpine image), initialization script at `source/postgres/01-init-schema.sql`.
- SERVICE ARCHITECTURE:
Single database instance with startup schema bootstrap.

- DB STRUCTURE:

**_rules_** : | **_id_** | sensor_source | sensor_metric | operator | threshold_value | target_actuator | target_state | enabled | description | created_at | updated_at |

**_rule_executions_** : | **_id_** | rule_id | triggered_at | execution_result | details |

**_schema_version_** : | **_version_** | applied_at | description |

## CONTAINER_NAME: Mars-Simulator

### DESCRIPTION:
External dependency that emulates habitat sensors and actuators.

### USER STORIES:
1, 2, 3, 9, 10, 19, 20

### PORTS:
8080:8080

### DESCRIPTION:
Provides heterogeneous sensor telemetry and actuator endpoints used by MAP services.

### PERSISTENCE EVALUATION
Outside MAP ownership; persistence details are not controlled by this project.

### EXTERNAL SERVICES CONNECTIONS
This is the external service itself.

### MICROSERVICES:

#### MICROSERVICE: mars-iot-simulator
- TYPE: external system
- DESCRIPTION: Source of sensor data and destination for actuator control commands.
- PORTS: 8080
- TECHNOLOGICAL SPECIFICATION:
Provided OCI image (`mars-iot-simulator:multiarch_v1`) loaded externally.
- SERVICE ARCHITECTURE:
Black-box service; interacted with through HTTP APIs by integration and actuation containers.
