package spacey.mars.habitat.integration.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import spacey.mars.habitat.integration.dto.MeasurementEvent;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Service
@RequiredArgsConstructor
public class SensorStreamService {

	private final ObjectMapper objectMapper;
	private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();

	public SseEmitter createEmitter() {

		SseEmitter emitter = new SseEmitter(0L); // No timeout for continuous streaming
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

		if (emitters.isEmpty())
			return;

		List<SseEmitter> deadEmitters = new CopyOnWriteArrayList<>();

		for (SseEmitter emitter : emitters)
			try {

				String jsonData = objectMapper.writeValueAsString(event);
				emitter.send(SseEmitter.event()
					.name("measurement")
					.data(jsonData));

			} catch(IOException e) {
				deadEmitters.add(emitter);
				log.debug("Failed to send event to emitter, marking for removal");
			}

		emitters.removeAll(deadEmitters);
	}

}

