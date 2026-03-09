package spacey.mars.habitat.integration.service;

import com.fasterxml.jackson.databind.ObjectMapper;
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
import spacey.mars.habitat.integration.dto.stream.AirlockV1;
import spacey.mars.habitat.integration.dto.stream.EnvironmentV1;
import spacey.mars.habitat.integration.dto.stream.PowerV1;
import spacey.mars.habitat.integration.dto.stream.ThermalLoopV1;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

@Slf4j
@Service
@RequiredArgsConstructor
public class SensorConsumerService {

	private final SensorRegistry sensorRegistry;
	private final RestClient restClient;
	private final MeasurementEventConverter measurementEventConverter;
	private final EventStreamerService eventStreamerService;
	private final ObjectMapper objectMapper;

	@Value("${simulator.base-url}")
	private String simulatorBaseUrl;

	@Value("${simulator.protocol:http}")
	private String simulatorProtocol;

	private final ExecutorService executorService = Executors.newCachedThreadPool();
	private final ConcurrentHashMap<String, Future<?>> activeConsumers = new ConcurrentHashMap<>();

	public void startConsumer(String topic) {

		if (activeConsumers.containsKey(topic)) {
			log.warn("Consumer for topic {} already running", topic);
			return;
		}

		SensorConfig config = sensorRegistry.getStream(topic);
		if (config == null) {
			log.error("Topic {} not found in registry", topic);
			return;
		}

		Future<?> future = executorService.submit(() -> consumeSSE(config));
		activeConsumers.put(topic, future);
		log.info("Started SSE consumer for topic {}", topic);
	}

	private void consumeSSE(SensorConfig config) {
		while (!Thread.currentThread().isInterrupted()) {
			try {

				// Build connection string
				String url = simulatorProtocol +
					"://" +
					simulatorBaseUrl +
					"/api/telemetry/stream/mars/telemetry/" +
					config.getId();

				log.info("Connecting to SSE stream: {}", url);

				restClient.get()
					.uri(url)
					.exchange((request, response) -> {
						if (response.getStatusCode().is2xxSuccessful())
							try(
								InputStream inputStream = response.getBody();
								InputStreamReader isReader = new InputStreamReader(inputStream, StandardCharsets.UTF_8);
								BufferedReader reader = new BufferedReader(isReader)
							) {
								processStream(reader, config);
							}
						else
							log.error(
								"Failed to connect to topic {}: {}",
								config.getId(), response.getStatusCode()
							);
						return null;
					});

			} catch (Exception e) {

				log.error("Error consuming topic {}", config.getId(), e);

				// Wait before retrying reconnecting
				try {
					Thread.sleep(5000);
				} catch (InterruptedException ie) {
					Thread.currentThread().interrupt();
					break;
				}
			}
		}
		log.info("SSE consumer for topic {} stopped", config.getId());
	}

	private void processStream(BufferedReader reader, SensorConfig config) throws IOException {

		StringBuilder eventData = new StringBuilder();
		String line;

		while ((line = reader.readLine()) != null)
			if(line.startsWith("data:")) {

				String data = line.substring(5).trim();
				eventData.append(data);

			} else if(line.isEmpty() && !eventData.isEmpty()) {

				processEvent(eventData.toString(), config);
				eventData.setLength(0);

			}
	}

	private void processEvent(String jsonData, SensorConfig config) {
		try {

			Object payload = parsePayload(jsonData, config.getType());
			if(payload == null)
				return;

			MeasurementEvent measurementEvent = measurementEventConverter.convert(payload);
			eventStreamerService.broadcast(measurementEvent);

			log.debug("Processed event from topic {}", config.getId());

		} catch(Exception e) {
			log.error("Failed to process event from topic {}", config.getId(), e);
		}
	}

	private Object parsePayload(String jsonData, SensorType type) throws IOException {
		return switch (type) {
			case POWER_V1 -> objectMapper.readValue(jsonData, PowerV1.class);
			case ENVIRONMENT_V1 -> objectMapper.readValue(jsonData, EnvironmentV1.class);
			case THERMAL_LOOP_V1 -> objectMapper.readValue(jsonData, ThermalLoopV1.class);
			case AIRLOCK_V1 -> objectMapper.readValue(jsonData, AirlockV1.class);
			default -> null;
		};
	}

	public void startAll() {
		sensorRegistry.getAllStream().forEach(config -> startConsumer(config.getId()));
	}

}

