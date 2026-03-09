package spacey.mars.habitat.integration.service;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import spacey.mars.habitat.integration.config.SensorConfig;
import spacey.mars.habitat.integration.config.SensorRegistry;
import spacey.mars.habitat.integration.config.SensorType;
import spacey.mars.habitat.integration.component.MeasurementEventConverter;
import spacey.mars.habitat.integration.dto.MeasurementEvent;
import spacey.mars.habitat.integration.dto.polling.ChemistryV1;
import spacey.mars.habitat.integration.dto.polling.LevelV1;
import spacey.mars.habitat.integration.dto.polling.ParticulateV1;
import spacey.mars.habitat.integration.dto.polling.ScalarV1;

import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
@Service
@RequiredArgsConstructor
public class SensorPollingService {

	private final SensorRegistry sensorRegistry;
	private final RestClient restClient;
	private final MeasurementEventConverter measurementEventConverter;
	private final EventStreamerService eventStreamerService;
	private final ScheduledExecutorService executor;

	@Value("${simulator.base-url}")
	private String simulatorBaseUrl;

	@Value("${simulator.protocol:http}")
	private String simulatorProtocol;

	@Value("${ms-integration.base-polling-rate:5000}")
	private long configuredBasePollingRate;

	private final ConcurrentHashMap<String, ScheduledFuture<?>> tasks = new ConcurrentHashMap<>();
	private final AtomicLong pollingRateMs = new AtomicLong(5000L);

	@PostConstruct
	void initRateFromProperties() {

		if (configuredBasePollingRate > 0)
			pollingRateMs.set(configuredBasePollingRate);

	}

	public void startPolling(String sensorId) {

		SensorConfig config = sensorRegistry.getRest(sensorId);
		if (config == null || tasks.containsKey(sensorId))
			return;

		ScheduledFuture<?> task = executor.scheduleAtFixedRate(
			() -> poll(sensorId),
			0,
			pollingRateMs.get(),
			TimeUnit.MILLISECONDS
		);

		tasks.put(sensorId, task);
	}

	private void poll(String sensorId) {
		try {

			SensorConfig cfg = sensorRegistry.getRest(sensorId);
			if (cfg == null)
				return;

			Object payload = fetch(sensorId, cfg.getType());
			if (payload == null)
				return;

			MeasurementEvent measurementEvent = measurementEventConverter.convert(payload);
			eventStreamerService.broadcast(measurementEvent);

		} catch (Exception e) {
			log.error("Poll error: {}", sensorId, e);
		}
	}

	private Object fetch(String sensorId, SensorType sensorType) {

		String url = simulatorProtocol +
			"://" +
			simulatorBaseUrl +
			"/api/sensors/" +
			sensorId;

		try {

			return switch(sensorType) {
				case SCALAR_V1 -> restClient.get().uri(url).retrieve().body(ScalarV1.class);
				case CHEMISTRY_V1 -> restClient.get().uri(url).retrieve().body(ChemistryV1.class);
				case LEVEL_V1 -> restClient.get().uri(url).retrieve().body(LevelV1.class);
				case PARTICULATE_V1 -> restClient.get().uri(url).retrieve().body(ParticulateV1.class);
				default -> throw new IllegalArgumentException("Unsupported sensor type: " + sensorType);
			};

		} catch (Exception e) {
			log.error(
				"Failed to fetch data for sensor {}: {}",
				sensorId, e.getMessage(), e
			);
			return null;
		}
	}

	public void stopPolling(String sensorId) {

		ScheduledFuture<?> task = tasks.remove(sensorId);
		if (task != null)
			task.cancel(false);

	}

	public void updateRate(long rateMs) {
		pollingRateMs.set(rateMs);
		ArrayList<String> activeSensorIds = new ArrayList<>(tasks.keySet());
		activeSensorIds.forEach(this::stopPolling);
		activeSensorIds.forEach(this::startPolling);
	}

	public long getPollingRateMs() {
		return pollingRateMs.get();
	}

	public void startAll() {
		sensorRegistry.getAllRest().forEach(c -> startPolling(c.getId()));
	}

}
