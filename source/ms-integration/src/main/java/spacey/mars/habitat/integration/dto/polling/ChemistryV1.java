package spacey.mars.habitat.integration.dto.polling;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import spacey.mars.habitat.integration.dto.Measurement;
import spacey.mars.habitat.integration.dto.Status;

import java.time.Instant;
import java.util.List;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ChemistryV1 {

	@JsonProperty("sensor_id")
	private String sensorId;

	@JsonProperty("captured_at")
	private Instant capturedAt;

	private List<Measurement> measurements;

	private Status status;

}

