package spacey.mars.habitat.integration.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import spacey.mars.habitat.integration.service.SensorPollingService;

import java.util.Map;

@RestController
@RequestMapping("/api/polling")
@RequiredArgsConstructor
public class PollingController {

	private final SensorPollingService pollingService;

	@GetMapping("/rate")
	public ResponseEntity<Long> getGlobalRate() {
		return ResponseEntity.ok(pollingService.getPollingRateMs());
	}

	@PostMapping("/rate")
	public ResponseEntity<Void> updateGlobalRate(@RequestBody Map<String, Long> payload) {

		Long rate = payload.get("rate");
		if (rate == null || rate <= 0)
			return ResponseEntity.badRequest().build();

		pollingService.updateRate(rate);
		return ResponseEntity.ok().build();

	}
}
