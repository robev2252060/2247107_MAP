## Mars Automation Platform (MAP) 


Project specifications:

* Python backend (FastAPI, Asyncio, Pydantic, AioKafka) 
* Vite frontend
* MongoDB database (in progress / to be changed) 
* Automation Engine in frontend/src/componenets/Rules
* Nginx


All of the micro-services have their corresponding Dockerfile and requirements.txt,
expect for frontend where nginx, package.json and vite.config.js are defined with a Dockerfile


Configuration files for Nginx are in the root of the project which probably needs to be added to the source folder, but I think that is an unnessesary headache for now.
Also the docker-compose should probably be inside source.


All of the services are defined in docker_compose with the following names:
- zookeeper (Distributed systems coordinatior)
- kafka (Message broker)
- mongodb 
- simulator (mars-iot-simulator-oci.tar)
- ingestion-service
- processing-service
- state-service
- rule-service
- actuator-service
- frontend
- nginx


Deployment:
1. docker image load -i mars-iot-simulator-oci.tar (if haven't before)
2. docker compose up -d --build

Access through: http://localhost:80

PostgreSQL bootstrap:
- Schema init script is in `source/postgres/01-init-schema.sql`.
- Single clean schema (127 lines) based on components.yaml spec.
- Creates 3 tables: rules, rule_executions, schema_version.
- Init scripts run only when the `postgres-data` volume is empty (fresh install).
- For clean reinstall: `docker compose down -v` then `docker compose up -d --build`.

For restart, first run:
`docker compose down -v`



Any changes can be made through refactoring the corresponding files of the service and the docker_compose itself, and adding dependencies through requirements.txt




