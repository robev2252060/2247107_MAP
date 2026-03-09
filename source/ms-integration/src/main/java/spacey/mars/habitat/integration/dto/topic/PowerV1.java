package spacey.mars.habitat.integration.dto.topic;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class PowerV1 {

	private String topic;

	@JsonProperty("event_time")
	private Instant eventTime;

	private String subsystem;

	@JsonProperty("power_kw")
	private Double powerKw;

	@JsonProperty("voltage_v")
	private Double voltageV;

	@JsonProperty("current_a")
	private Double currentA;

	@JsonProperty("cumulative_kwh")
	private Double cumulativeKwh;

}
