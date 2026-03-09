package spacey.mars.habitat.integration.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import spacey.mars.habitat.integration.service.EventStreamerService;

@Slf4j
@RestController
@RequiredArgsConstructor
public class SensorStreamController {

	private final EventStreamerService eventStreamerService;

	@GetMapping(
		path = "/api/v1/sensors/stream",
		produces = MediaType.TEXT_EVENT_STREAM_VALUE
	)
	public SseEmitter streamSensors() {
		log.info("New SSE stream connection request");
		return eventStreamerService.createEmitter();
	}
}
