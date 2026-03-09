package spacey.mars.habitat.integration.dto.stream;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import spacey.mars.habitat.integration.dto.Status;

import java.time.Instant;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class ThermalLoopV1 {

	private String topic;

	@JsonProperty("event_time")
	private Instant eventTime;

	private String loop;

	@JsonProperty("temperature_c")
	private Double temperatureC;

	@JsonProperty("flow_l_min")
	private Double flowLMin;

	private Status status;

}
