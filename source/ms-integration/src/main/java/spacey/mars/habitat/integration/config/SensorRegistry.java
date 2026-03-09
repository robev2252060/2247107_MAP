package spacey.mars.habitat.integration.config;

import java.util.Collection;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class SensorRegistry {

	private final ConcurrentMap<String, SensorConfig> sensors = new ConcurrentHashMap<>();

	public void register(SensorConfig config) {
		sensors.put(config.getId(), config);
	}

	public SensorConfig get(String sensorId) {
		return sensors.get(sensorId);
	}

	public Collection<SensorConfig> getAll() {
		return sensors.values();
	}

}
