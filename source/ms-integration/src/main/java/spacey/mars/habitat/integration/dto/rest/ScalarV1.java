package spacey.mars.habitat.integration.dto.rest;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import spacey.mars.habitat.integration.dto.Status;

import java.time.Instant;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ScalarV1 {

	@JsonProperty("sensor_id")
	private String sensorId;

	@JsonProperty("captured_at")
	private Instant capturedAt;

	private String metric;

	private Double value;

	private String unit;

	private Status status;

}
