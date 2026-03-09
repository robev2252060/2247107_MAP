package spacey.mars.habitat.integration.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import spacey.mars.habitat.integration.dto.Measurement;
import spacey.mars.habitat.integration.dto.MeasurementEvent;

import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Service
@RequiredArgsConstructor
public class EventStreamerService {

	private final ObjectMapper objectMapper;
	private final KafkaTemplate<String, MeasurementEvent> kafkaTemplate;
	private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();
	private final Map<String, CachedMeasurement> measurementCache = new ConcurrentHashMap<>();

	private static final String MEASUREMENTS_TOPIC = "measurements";

	public SseEmitter createEmitter() {

		SseEmitter emitter = new SseEmitter(0L); // No timeout for continuous streaming
		replayCachedMeasurements(emitter);
		emitters.add(emitter);

		emitter.onCompletion(() -> {
			emitters.remove(emitter);
			log.debug("SSE emitter completed, {} active connections", emitters.size());
		});

		emitter.onTimeout(() -> {
			emitters.remove(emitter);
			log.debug("SSE emitter timeout, {} active connections", emitters.size());
		});

		emitter.onError(ex -> {
			emitters.remove(emitter);
			log.debug("SSE emitter error, {} active connections", emitters.size());
		});

		log.info("New SSE connection established, {} active connections", emitters.size());

		return emitter;
	}

	public void broadcast(MeasurementEvent event) {

		cacheEvent(event);
		publishToKafka(event);

		if (emitters.isEmpty())
			return;

		List<SseEmitter> deadEmitters = new CopyOnWriteArrayList<>();

		for (SseEmitter emitter : emitters)
			try {

				sendMeasurementEvent(emitter, event);

			} catch(IOException e) {
				deadEmitters.add(emitter);
				log.debug("Failed to send event to emitter, marking for removal");
			}

		emitters.removeAll(deadEmitters);
	}

	private void publishToKafka(MeasurementEvent event) {
		try {
			kafkaTemplate.send(MEASUREMENTS_TOPIC, event.getSource(), event);
			log.debug("Published measurement event to Kafka topic '{}' for source: {}", MEASUREMENTS_TOPIC, event.getSource());
		} catch (Exception e) {
			log.error("Failed to publish measurement event to Kafka", e);
		}
	}

	private void cacheEvent(MeasurementEvent event) {

		if (event == null || event.getSource() == null || event.getReadings() == null)
			return;

		for (Measurement reading : event.getReadings()) {

			if (reading == null || reading.getMetric() == null)
				continue;

			String key = cacheKey(event.getSource(), reading.getMetric());
			Measurement measurementCopy = new Measurement(reading.getMetric(), reading.getValue(), reading.getUnit());
			measurementCache.put(key, new CachedMeasurement(
				event.getSource(),
				event.getTimestamp(),
				event.getStatus(),
				measurementCopy
			));

		}
	}

	private void replayCachedMeasurements(SseEmitter emitter) {
		if (measurementCache.isEmpty())
			return;

		Map<String, ReplayBucket> bySource = new LinkedHashMap<>();

		for (CachedMeasurement cached : measurementCache.values()) {
			ReplayBucket bucket = bySource.computeIfAbsent(cached.source(), ignored -> new ReplayBucket(cached.source()));
			bucket.add(cached);
		}

		for (ReplayBucket bucket : bySource.values()) {
			MeasurementEvent replayEvent = bucket.toMeasurementEvent();
			try {
				sendMeasurementEvent(emitter, replayEvent);
			} catch (IOException e) {
				log.debug("Failed to replay cached measurements to new emitter");
				return;
			}
		}
	}

	private void sendMeasurementEvent(SseEmitter emitter, MeasurementEvent event) throws IOException {

		String jsonData = objectMapper.writeValueAsString(event);
		emitter.send(SseEmitter.event()
			.name("measurement")
			.data(jsonData));

	}

	private String cacheKey(String source, String metric) {
		return source + "::" + metric;
	}

	private record CachedMeasurement(
		String source,
		Instant timestamp,
		String status,
		Measurement measurement
	) {
	}

	private static class ReplayBucket {

		private final String source;
		private Instant timestamp;
		private String status;
		private final List<Measurement> readings = new ArrayList<>();

		private ReplayBucket(String source) {
			this.source = source;
		}

		private void add(CachedMeasurement cached) {
			readings.add(cached.measurement());
			if (timestamp == null || (cached.timestamp() != null && cached.timestamp().isAfter(timestamp))) {
				timestamp = cached.timestamp();
				status = cached.status();
			}
		}

		private MeasurementEvent toMeasurementEvent() {
			return new MeasurementEvent(timestamp, source, status, readings);
		}
	}

}
