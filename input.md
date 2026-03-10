# SYSTEM DESCRIPTION:

We are in 2036. After a long shift at SpaceY, the operations team is unexpectedly relocated to Mars and must restore a damaged habitat automation stack.

The **Mars Automation Platform (MAP)** is a distributed system for habitat monitoring and control. It must ingest heterogeneous sensor telemetry (both polled and streamed), normalize data into a common internal format, evaluate simple IF-THEN automation rules, and provide a real-time dashboard for operators.

The platform is mission-critical: it supports environmental awareness and rapid actuator response for life-support related conditions.

# USER STORIES:

1) As an Operator, I want to view a centralized dashboard of all habitat sensors so that I can monitor the overall health of the Mars base.
2) As an Operator, I want to see the most recent reading from each sensor instantly upon opening the dashboard so that I do not have to wait for the next data broadcast.
3) As an Operator, I want sensor data to update automatically on my screen without refreshing so that I am always looking at live telemetry.
4) As an Operator, I want to see standardized units and naming conventions for all data, regardless of source, so I do not misinterpret critical life-support metrics.
5) As an Operator, I want to view a live line chart for selected sensors while the page is open so that I can visually track rapid environmental trends.
6) As an Operator, I want sensors to be grouped by operational domain (for example Thermal, Power, Air Quality) so that I can quickly find related metrics during an emergency.
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
