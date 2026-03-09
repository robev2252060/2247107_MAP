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
public class ParticulateV1 {

	@JsonProperty("sensor_id")
	private String sensorId;

	@JsonProperty("captured_at")
	private Instant capturedAt;

	@JsonProperty("pm1_ug_m3")
	private Double pm1UgM3;

	@JsonProperty("pm25_ug_m3")
	private Double pm25UgM3;

	@JsonProperty("pm10_ug_m3")
	private Double pm10UgM3;

	private Status status;

}
