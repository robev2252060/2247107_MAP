package spacey.mars.habitat.integration.dto.topic;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class AirlockV1 {

	private String topic;

	@JsonProperty("event_time")
	private Instant eventTime;

	@JsonProperty("airlock_id")
	private String airlockId;

	@JsonProperty("cycles_per_hour")
	private Double cyclesPerHour;

	@JsonProperty("last_state")
	private AirlockState lastState;

}
