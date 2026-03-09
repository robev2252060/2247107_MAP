namespace MAPEngine;

record SensorEvent (
    string SensorName,
    double Value,
    string Unit,
    DateTimeOffset Timestamp
);

record ActuatorCommand (
    string ActuatorName,
    string State    // "ON" | "OFF"
);