package spacey.mars.habitat.integration.config;

import java.util.Collection;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class SensorRegistry {

	private final ConcurrentMap<String, SensorConfig> restSensors = new ConcurrentHashMap<>();
	private final ConcurrentMap<String, SensorConfig> streamSensors = new ConcurrentHashMap<>();

	public void registerRest(SensorConfig config) {
		restSensors.put(config.getId(), config);
	}

	public void registerStream(SensorConfig config) {
		streamSensors.put(config.getId(), config);
	}

	public SensorConfig getRest(String sensorId) {
		return restSensors.get(sensorId);
	}

	public SensorConfig getStream(String sensorId) {
		return streamSensors.get(sensorId);
	}

	public Collection<SensorConfig> getAllRest() {
		return restSensors.values();
	}

	public Collection<SensorConfig> getAllStream() {
		return streamSensors.values();
	}

}
